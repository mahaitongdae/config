# iTerm2 SSH 图片粘贴

将剪贴板图片上传到当前 iTerm2 pane 的 SSH 目标，然后把路径粘贴到 Claude Code / Codex。**Ctrl+Shift+V** 仅在 iTerm2 内生效。

## 新 Mac 上安装

前提：macOS、Python 3.10+、Xcode Command Line Tools、iTerm2、Karabiner-Elements，以及可用的 SSH 密钥或 ssh-agent。

如使用 Homebrew，可先安装依赖（已有的软件可跳过）：

```sh
brew install python
brew install --cask iterm2 karabiner-elements
xcode-select --install  # 已安装 Command Line Tools 时无需重复
```

1. 启动 Karabiner-Elements，按它的提示完成系统权限设置，选中要使用的 profile。
2. 在 iTerm2 → Settings → General → Magic 开启 **Enable Python API**。
3. 在本仓库根目录运行：

```sh
python3 macos/ssh-image-paste/install.py
```

安装器在 `~/Library/Application Support/SSHImagePaste` 创建独立 Python 环境、安装 `iterm2==2.30`，并使用本机 Swift 编译剪贴板读取程序。随后备份 Karabiner 配置，只在当前 profile 中添加这一条快捷键规则。重复运行会更新同名规则，不会重复添加。安装需要网络以下载 Python 依赖。

仓库不包含编译后的二进制、运行日志、配置备份、图片或 SSH 凭据。无需修改远端 tmux 配置。

## 开机后

脚本无需开机启动，每次按快捷键时才运行。保持 Karabiner-Elements 的登录启动和后台运行；正常打开 iTerm2、连接 SSH 即可。首次运行时按 iTerm2 提示授权此脚本访问 API。

## 使用

1. 用 **Cmd+Ctrl+Shift+4** 截图到剪贴板，或复制一张图片。
2. 切回直接运行 `ssh host` 的 iTerm2 pane，进入远程 tmux 的 Claude Code / Codex 输入框。
3. 按 **Ctrl+Shift+V**，等待上传完成。远程图片绝对路径会作为 bracketed paste 事件进入输入框，不附带 Enter。
4. 支持粘贴图片路径的客户端会将路径转换为图片附件。`Image #1` 的具体显示由客户端版本决定，脚本不会伪造附件标签。

会话定位及粘贴使用 iTerm2 官方 Python API，避免 AppleScript 的 `Can't get tab 1` 错误。首次运行时，iTerm2 可能请求允许 Python 脚本访问，请核对脚本属于 `SSHImagePaste` 后允许。

## 自动识别范围

- 根据当前 iTerm2 pane 的 tty，识别唯一的前台 SSH 进程；不是根据所有 SSH 进程猜目标。
- 使用原 SSH host / 用户，并继承 SSH 配置；保留常用端口、密钥、ProxyJump 和 `-o` 参数。
- 普通 `ssh host` → 远程 `tmux` → Claude Code / Codex 的流程受支持。
- 本地 tmux 内再 ssh、`ssh -CC`、远端二次 ssh、容器或计算节点里的不同文件系统，未实现自动追踪。图片上传到 Mac 直接连接的那台机器。
- 上传中不要切换远端 tmux pane。脚本会检测 iTerm2 pane 或 SSH 进程变化，但无法检测远程 tmux 内部的 pane 切换。
- 上传使用非交互 SSH，需已有密钥、ssh-agent 或可用的连接复用；不会弹出终端密码提示，也不会自行关闭主机校验。

## 文件与排错

- 剪贴板内容保留不变。
- 图片保存到远端 `/tmp/ssh-image.随机串/clipboard-随机串.png`，目录 700、文件 600。
- 本地临时 PNG 自动删除；远端图片保留以便聊天继续引用，可能被系统临时目录清理机制删除。不适合长期归档。
- 最大图片大小 50 MB，失败会弹出提示且不粘贴。
- 日志：`~/Library/Application Support/SSHImagePaste/paste.log`。
- 检查当前识别目标：

```sh
"$HOME/Library/Application Support/SSHImagePaste/venv/bin/python" "$HOME/Library/Application Support/SSHImagePaste/paste.py" --check
```

## 移除快捷键

打开 Karabiner-Elements → Complex Modifications，删除名为 `SSH Image Paste: Ctrl+Shift+V in iTerm2` 的规则。其他规则不受影响。

原配置备份保存在安装目录中的 `karabiner-backup-*.json`。不要在后续配置有变化时直接覆盖整份配置。

## 验证情况

已验证 SSH 目标识别、常见 SSH 参数解析、读取实际剪贴板图片、真实上传、两端 SHA-256 一致及远端权限；用户已确认实际快捷键流程可用。

修订版通过模拟会话测试：正确发送 bracketed paste、不广播到其他 pane、切换会话时拒绝粘贴、没有窗口时给出明确提示；启动入口参数已按安装版本的真实接口签名检查。

官方接口参考：[iTerm2 Python API](https://iterm2.com/python-api/)。
