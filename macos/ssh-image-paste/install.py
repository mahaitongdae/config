#!/usr/bin/env python3
"""Build the clipboard helper and install the iTerm2-only Karabiner shortcut."""
import datetime
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys


def main():
    if sys.platform != 'darwin':
        raise SystemExit('此脚本仅支持 macOS。')
    if sys.version_info < (3, 10):
        raise SystemExit('请使用 Python 3.10 或更新版本。')
    swift = shutil.which('swiftc')
    if not swift:
        raise SystemExit('缺少 Swift 编译器，请先运行 xcode-select --install。')
    source = Path(__file__).resolve().parent
    config = Path.home() / '.config/karabiner/karabiner.json'
    if not config.exists():
        raise SystemExit('请先安装并启动 Karabiner-Elements，完成权限设置后重试。')
    data = json.loads(config.read_text())
    profiles = [p for p in data.get('profiles', []) if p.get('selected')]
    if len(profiles) != 1:
        raise SystemExit('无法确定 Karabiner 当前配置，请先在 Karabiner 中选择一个 profile。')
    runtime = Path.home() / 'Library/Application Support/SSHImagePaste'
    runtime.mkdir(parents=True, exist_ok=True)
    python = runtime / 'venv/bin/python'
    if not python.exists():
        subprocess.run([sys.executable, '-m', 'venv', str(runtime / 'venv')], check=True)
    subprocess.run([str(python), '-m', 'pip', 'install', 'iterm2==2.30'], check=True)
    subprocess.run([swift, str(source / 'clipboard.swift'), '-o', str(runtime / 'clipboard-image')], check=True)
    for name in ('paste.py', 'clipboard.swift'):
        shutil.copy2(source / name, runtime / name)
    # Re-read after compilation to preserve any concurrent Karabiner edits.
    data = json.loads(config.read_text())
    profiles = [p for p in data.get('profiles', []) if p.get('selected')]
    if len(profiles) != 1:
        raise SystemExit('Karabiner 当前 profile 已变化，请重新运行安装。')
    backup = runtime / ('karabiner-backup-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.json')
    shutil.copy2(config, backup)
    description = 'SSH Image Paste: Ctrl+Shift+V in iTerm2'
    command = shlex.quote(str(python)) + ' ' + shlex.quote(str(runtime / 'paste.py'))
    command += ' >> ' + shlex.quote(str(runtime / 'paste.log')) + ' 2>&1'
    rule = {'description': description, 'manipulators': [{
        'type': 'basic',
        'from': {'key_code': 'v', 'modifiers': {'mandatory': ['control', 'shift']}},
        'to': [{'shell_command': command}],
        'conditions': [{'type': 'frontmost_application_if', 'bundle_identifiers': ['^com\\.googlecode\\.iterm2$']}]
    }]}
    rules = profiles[0].setdefault('complex_modifications', {}).setdefault('rules', [])
    rules[:] = [r for r in rules if r.get('description') != description]
    rules.append(rule)
    temp = config.with_suffix('.json.ssh-image-tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=4) + '\n')
    temp.chmod(0o600)
    temp.replace(config)
    print('Installed:', runtime)
    print('Backup:', backup)
    print('请开启 iTerm2 → Settings → General → Magic → Enable Python API。')
    print('在 iTerm2 的 SSH 输入框按 Ctrl+Shift+V；首次 API 授权需手动允许。')


if __name__ == '__main__':
    main()
