#!/usr/bin/env python3
"""macOS iTerm2: clipboard PNG -> current SSH destination -> bracketed paste."""
import fcntl
import asyncio
import iterm2
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parent

def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, timeout=60, **kwargs)

def applescript(source, *args):
    return run(['/usr/bin/osascript', '-e', source, *args]).stdout.decode().strip()

async def session(app):
    await app.async_refresh_focus()
    window = app.current_window
    tab = window.current_tab if window else None
    selected = tab.current_session if tab else None
    if selected is None:
        raise ValueError('iTerm2 当前没有可用的终端会话。请关闭设置/弹窗，点击 SSH 输入框后重试。')
    tty = await selected.async_get_variable('tty')
    if not isinstance(tty, str) or not tty.startswith('/dev/'):
        raise ValueError('当前会话没有本机 tty；暂不支持 iTerm2 的 tmux -CC 集成会话。')
    return selected, tty

def parse_ssh(command):
    words = shlex.split(command)
    if Path(words.pop(0)).name != 'ssh':
        raise ValueError('不是 SSH 连接')
    kept = []
    takes_arg = set('BbcDEeFIiJLlmOopQRSWw')
    preserve = set('bF iJlp'.replace(' ', ''))
    i = 0
    while i < len(words):
        word = words[i]
        if word == '--':
            i += 1
            break
        if not word.startswith('-'):
            break
        flags = word[1:]
        for n, flag in enumerate(flags):
            if flag in takes_arg:
                value = flags[n+1:]
                if not value:
                    i += 1
                    if i >= len(words):
                        raise ValueError('SSH 参数不完整')
                    value = words[i]
                if flag in preserve:
                    kept.extend(['-' + flag, value])
                elif flag == 'o':
                    key = re.split(r'[=\s]', value, maxsplit=1)[0].lower()
                    if key not in {'remotecommand', 'requesttty', 'localforward', 'remoteforward', 'dynamicforward', 'sessiontype', 'forkafterauthentication', 'stdin null', 'stdinnull'}:
                        kept.extend(['-o', value])
                elif flag in 'OWQ':
                    raise ValueError('当前 SSH 不是普通交互连接')
                break
            if flag in '46':
                kept.append('-' + flag)
        i += 1
    if i >= len(words) or words[i].startswith('-'):
        raise ValueError('无法确定 SSH 目标')
    return kept, words[i]

def connection(tty):
    output = run(['/bin/ps', '-ww', '-t', tty.removeprefix('/dev/'), '-o', 'pid=,stat=,comm=,args=']).stdout.decode()
    matches = []
    for line in output.splitlines():
        fields = line.strip().split(None, 3)
        if len(fields) == 4 and Path(fields[2]).name == 'ssh' and '+' in fields[1]:
            opts, host = parse_ssh(fields[3])
            matches.append((fields[0], opts, host))
    if len(matches) != 1:
        raise ValueError('当前 iTerm2 pane 没有唯一的前台 SSH 连接。请在直接 ssh 的窗口使用此快捷键。')
    return matches[0]

def ssh_args(options, host):
    return ['/usr/bin/ssh', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
            '-o', 'ClearAllForwardings=yes', '-o', 'RemoteCommand=none',
            '-o', 'RequestTTY=no', '-o', 'SessionType=default',
            '-o', 'ForkAfterAuthentication=no', *options, host]

async def paste(app, selected, tty, text):
    current, current_tty = await session(app)
    if current.session_id != selected.session_id or current_tty != tty:
        raise ValueError('上传时切换了终端，已取消粘贴。图片位于 ' + text)
    await selected.async_send_text('\x1b[200~' + text + '\x1b[201~', suppress_broadcast=True)

def upload(options, host):
    with tempfile.TemporaryDirectory(prefix='ssh-image-') as temp:
        png = Path(temp) / 'image.png'
        run([str(ROOT / 'clipboard-image'), str(png)])
        if png.stat().st_size > 50 * 1024 * 1024:
            raise ValueError('图片超过 50 MB，请缩小后重试。')
        name = 'clipboard-' + uuid.uuid4().hex + '.png'
        # Exclusive private directory, atomic rename; stdout contains only the path.
        remote = ('set -eu; umask 077; d=$(mktemp -d /tmp/ssh-image.XXXXXXXXXX); '
                  'trap \'rm -f "$d/partial"; rmdir "$d" 2>/dev/null || true\' EXIT; '
                  'cat > "$d/partial"; mv "$d/partial" "$d/' + name + '"; '
                  'printf "%s\\n" "$d/' + name + '"')
        result = run([*ssh_args(options, host), remote], input=png.read_bytes())
        path = result.stdout.decode().strip()
        if not re.fullmatch(r'/tmp/ssh-image\.[A-Za-z0-9]+/clipboard-[0-9a-f]{32}\.png', path):
            raise ValueError('远程返回了意外的路径；已取消粘贴。')
        return path

async def main(api_connection):
    app = await iterm2.async_get_app(api_connection)
    selected, tty = await session(app)
    identity = connection(tty)
    _, options, host = identity
    if '--check' in sys.argv:
        print(json.dumps({'session': selected.session_id, 'tty': tty, 'host': host, 'options': options}, ensure_ascii=False))
        return
    path = await asyncio.to_thread(upload, options, host)
    if '--upload-only' in sys.argv:
        print(path)
        return
    if connection(tty) != identity:
        raise ValueError('SSH 连接已变化，已取消粘贴。图片位于 ' + host + ':' + path)
    await paste(app, selected, tty, path)
    print(host + ':' + path)

if __name__ == '__main__':
    os.umask(0o077)
    with open(ROOT / '.lock', 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            sys.exit(0)
        try:
            iterm2.Connection().run_until_complete(main, retry=False)
        except Exception as exc:
            detail = str(exc)
            if isinstance(exc, subprocess.CalledProcessError):
                detail = exc.stderr.decode(errors='replace').strip() or detail
            print(detail, file=sys.stderr)
            applescript('''on run argv
                display alert "SSH 图片粘贴失败" message (item 1 of argv) as warning
            end run''', detail[:1500])
            sys.exit(1)
