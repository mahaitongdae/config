# kitty 和 zsh 配置备份

2026-09-27 从 Linux 桌面环境备份。配置文件保持原样；没有包含历史记录、缓存、凭据、旧备份、字体二进制或软件本体。

## 文件对应关系

| 仓库文件 | 恢复位置 | 用途 |
| --- | --- | --- |
| `zsh/.zshrc` | `~/.zshrc` | Oh My Zsh、Powerlevel10k、别名和 PATH |
| `zsh/.zprofile` | `~/.zprofile` | 登录时加载 `.profile` |
| `zsh/.profile` | `~/.profile` | 用户 PATH 和 `GLFW_IM_MODULE=ibus` |
| `zsh/.p10k.zsh` | `~/.p10k.zsh` | 提示符样式 |
| `kitty/kitty.conf` | `~/.config/kitty/kitty.conf` | 字体、窗口、透明度、标签栏 |
| `kitty/current-theme.conf` | `~/.config/kitty/current-theme.conf` | Catppuccin Mocha 配色 |
| `kitty/quick-access-terminal.conf` | `~/.config/kitty/quick-access-terminal.conf` | 下拉终端配置 |

## 在新机器上恢复

### 1. 安装软件并克隆本仓库

Ubuntu / Debian 可先安装基础工具：

```bash
sudo apt update
sudo apt install git zsh fontconfig unzip curl
git clone https://github.com/mahaitongdae/config.git "$HOME/config"
cd "$HOME/config"
```

这是私有仓库，克隆前需配置 GitHub 身份验证（例如 `gh auth login` 后 `gh auth setup-git`），或使用已配置 SSH 密钥的 SSH 地址。不要将访问令牌写入配置文件。

另行安装 kitty；本次备份使用 **kitty 0.49.1** 和 **zsh 5.9**。发行版自带的旧版 kitty 可能不支持窗口位置或 quick-access 等选项。安装入口：https://sw.kovidgoyal.net/kitty/binary/

### 2. 安装 Oh My Zsh 和 Powerlevel10k

下面只克隆缺失的目录，不覆盖已有安装：

```bash
if [ ! -e "$HOME/.oh-my-zsh" ]; then
  git clone https://github.com/ohmyzsh/ohmyzsh.git "$HOME/.oh-my-zsh"
fi
if [ ! -e "$HOME/.oh-my-zsh/custom/themes/powerlevel10k" ]; then
  git clone https://github.com/romkatv/powerlevel10k.git \
    "$HOME/.oh-my-zsh/custom/themes/powerlevel10k"
fi
```

本次备份的依赖版本如下。如需复现同一版本，可以在新克隆的目录中分别执行对应的 checkout；已有安装有本地改动时应先处理改动。

```bash
git -C "$HOME/.oh-my-zsh" checkout 74965c96098134b192f00084f966b4b02438a739
git -C "$HOME/.oh-my-zsh/custom/themes/powerlevel10k" checkout d05a1b00f9a61f9578bf9dc19b8451942dde8734
```

启用的 `git` 插件由 Oh My Zsh 自带，无需单独安装。Powerlevel10k 首次启动可能下载 gitstatus 组件，需要网络。

### 3. 安装字体

kitty 配置使用 **IosevkaTermSlab Nerd Font**，提示符配置使用 Nerd Fonts v3 图标。到 Nerd Fonts 的发布页下载 `IosevkaTermSlab.zip`：https://github.com/ryanoasis/nerd-fonts/releases

假设下载到 `~/Downloads/IosevkaTermSlab.zip`，Linux 下执行：

```bash
mkdir -p "$HOME/.local/share/fonts/IosevkaTermSlab"
unzip -o "$HOME/Downloads/IosevkaTermSlab.zip" -d "$HOME/.local/share/fonts/IosevkaTermSlab"
fc-cache -f
fc-match 'IosevkaTermSlab Nerd Font'
```

最后一条命令应匹配 IosevkaTermSlab 字体。未安装时 kitty 可能回退到其他字体，图标和间距会不同。

### 4. 恢复配置并重新打开终端

```bash
cd "$HOME/config"
bash restore.sh
exec zsh -l
```

脚本将上述 7 个文件复制到 HOME 中，覆盖前把已有文件（含符号链接）移动到 `~/.config-backup-日期时间-随机后缀/`，并输出备份路径。它会覆盖 `.profile`，因为 `.zprofile` 依赖它；新机器如有额外环境变量，请从旧文件合并回来。脚本不安装软件、不更改默认 shell，也不会删除 kitty 目录中的其他文件。不要使用 `sudo` 运行。

完整退出并重新打开 kitty。若需要让 zsh 成为默认 shell，可执行 `chsh -s "$(command -v zsh)"`，然后注销并重新登录。

恢复目标使用标准 HOME 路径。如果新机器设置了 `ZDOTDIR`、`KITTY_CONFIG_DIRECTORY` 或自定义 `XDG_CONFIG_HOME`，请调整目标位置或取消相关覆盖。也可以用 `bash restore.sh /绝对路径/测试目录` 在已有的空目录中试恢复。

### 环境差异与已知问题

- 窗口尺寸 `1835 × 926` 来自原机器，可按新屏幕修改。
- 透明度、模糊、窗口位置和下拉终端行为取决于 kitty 版本、窗口系统与合成器；macOS / 其他系统需适配字体安装位置和相关选项。
- 原始 `quick-access-terminal.conf` 最后一行是 `kittty_override tab_bar_min_tabs=2`，其中 `kittty_override` 拼写有误。本仓库忠实保留备份；使用下拉终端前请在恢复后的文件中改为 `kitty_override`。
- `.profile` 的 `GLFW_IM_MODULE=ibus` 来自原 Linux 输入法环境；新机器不使用 ibus 时可删除该行。

## 撤销一次恢复

脚本输出的备份目录保留了原路径层级。将需要撤销的文件移回去，例如（替换为实际备份目录）：

```bash
backup_dir="$HOME/.config-backup-实际日期时间-实际后缀"
cp -a "$backup_dir/.zshrc" "$HOME/.zshrc"
```

其他文件按文件表逐一恢复。原本不存在的文件不会出现在备份目录中，需要时手动删除这次新增的对应文件。

## 更新备份

在本机修改配置后，显式复制要更新的文件，再检查并提交：

```bash
cd "$HOME/config"
git pull --ff-only
cp "$HOME/.zshrc" "$HOME/.zprofile" "$HOME/.p10k.zsh" "$HOME/.profile" zsh/
cp "$HOME/.config/kitty/kitty.conf" \
   "$HOME/.config/kitty/current-theme.conf" \
   "$HOME/.config/kitty/quick-access-terminal.conf" kitty/
git diff
git add zsh/ kitty/
git diff --cached
git commit -m "Update kitty and zsh configuration"
git push
```

提交前确认差异中没有密码或 token。新增 include/source 文件时，也要备份对应文件并更新恢复脚本和文件表。
