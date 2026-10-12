# kitty 中文输入设置（Fcitx5 + 拼音）

2026-10-11 从本机配置整理。适用基线：Ubuntu 24.04.5、GNOME **X11**、kitty 0.49.1、Fcitx5 5.1.7。本机检查时 Fcitx5 正在运行，`fcitx5-remote` 返回 `2`、当前输入法为 `pinyin`；尚未执行自动化中文键入测试。Wayland 和其他发行版需另行验证。

补充验证（2026-10-11）：Ubuntu 22.04.5、GNOME X11、Fcitx5 5.0.14。此机器仅执行 `im-config -n fcitx5` 后重新登录，Fcitx5 未自动启动，GNOME 启动了 IBus；添加下面的桌面自启动项后完成配置。当前会话已验证 kitty 内 `Ctrl+Space` → `nihao` → Space → Enter 实际输出「你好」。新增自启动项尚未经过下一次登录验证。

## 1. 安装依赖

先按仓库主 README 安装 kitty，再安装输入法和中文字体：

```bash
sudo apt update
sudo apt install fcitx5 fcitx5-chinese-addons fcitx5-frontend-all \
  fcitx5-config-qt im-config fonts-noto-cjk
im-config -n fcitx5
```

Ubuntu 22.04 没有 `fcitx5-frontend-all` 元包，改为明确安装各 frontend：

```bash
sudo apt install fcitx5 fcitx5-chinese-addons \
  fcitx5-frontend-gtk2 fcitx5-frontend-gtk3 fcitx5-frontend-gtk4 \
  fcitx5-frontend-qt5 fcitx5-config-qt im-config fonts-noto-cjk
im-config -n fcitx5
```

`im-config` 使用普通用户运行。它会设置 `~/.xinputrc`，使下次桌面登录使用 Fcitx5。

## 2. 恢复拼音配置

本目录只保存设置，不包含用户词库、输入历史或缓存：

| 仓库文件 | 目标路径 |
| --- | --- |
| `fcitx5/profile` | `~/.config/fcitx5/profile` |
| `fcitx5/config` | `~/.config/fcitx5/config` |
| `fcitx5/conf/pinyin.conf` | `~/.config/fcitx5/conf/pinyin.conf` |

先从托盘菜单退出 Fcitx5，避免运行中的进程在退出时写回旧设置。然后执行以下命令（假设仓库克隆到 `~/config`，使用标准 `~/.config` 路径）：

```bash
cd "$HOME/config"
backup_dir="$(mktemp -d "$HOME/.fcitx5-backup-XXXXXXXX")"
if [ -e "$HOME/.config/fcitx5" ]; then
  cp -a "$HOME/.config/fcitx5" "$backup_dir/fcitx5"
fi
mkdir -p "$HOME/.config/fcitx5/conf"
cp input-method/fcitx5/profile input-method/fcitx5/config "$HOME/.config/fcitx5/"
cp input-method/fcitx5/conf/pinyin.conf "$HOME/.config/fcitx5/conf/"
printf '旧输入法配置备份：%s\n' "$backup_dir"
```

这些文件提供 US 键盘和拼音；默认从英文开始，各输入上下文独立保存状态。拼音每页显示 7 个候选，启用 Emoji、拆字和云拼音，未启用联想预测。云拼音会向云服务查询候选；如不需要，在 `fcitx5-configtool` 的拼音设置中关闭「云拼音」。`ShuangpinProfile=Ziranma` 是双拼方案偏好，当前配置选择的输入法仍是 `pinyin`。

仓库根目录的 `restore.sh` 仅恢复原有 kitty / zsh / tmux 配置；输入法配置通过此处步骤单独恢复。

## 3. 设置环境变量

在 `~/.profile` 中保留或补充以下内容，每个变量只设置一次：

```bash
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
export GLFW_IM_MODULE=ibus
```

仓库的 `zsh/.profile` 已有最后一行。不要只在 `.zshrc` 里设置：kitty 启动后才打开 shell，此时 shell 的环境变量无法影响父进程 kitty。

`GLFW_IM_MODULE=ibus` 指定 kitty 在 X11 下使用 IBus 协议；实际服务可由 Fcitx5 的 IBus frontend 提供，并不意味着必须启动 `ibus-daemon`。这是 [Fcitx 官方文档描述的 kitty 集成方式](https://fcitx-im.org/wiki/How_does_an_application_talk_to_Fcitx)。本机检查时 `org.freedesktop.IBus` 的所有者确实是 `fcitx5`。

如果已有 `~/.config/environment.d/fcitx.conf` 或 `fcitx5.conf`，检查其中变量是否与以上值一致即可。本机两份文件内容重复；新机器无需重复创建。

## 4. 自动启动与重新登录

Ubuntu 通常通过 `im-config` 在桌面登录时启动输入法，但本次 Ubuntu 22.04 GNOME X11 实测未启动。注销并重新登录后，**先运行 `pgrep -a -x fcitx5`**。不要先运行 `fcitx5-remote`：它可能通过 D-Bus 按需启动 Fcitx5，掩盖登录时未启动的问题。如果没有自动启动，按 [Fcitx 官方设置文档](https://fcitx-im.org/wiki/Setup_Fcitx_5/en) 添加桌面自启动：

```bash
mkdir -p "$HOME/.config/autostart"
cp -n /usr/share/applications/org.fcitx.Fcitx5.desktop "$HOME/.config/autostart/"
```

无需立即注销时，可先在当前图形桌面会话中启动：

```bash
fcitx5 -d
pgrep -a -x fcitx5
busctl --user list --no-pager | grep -E 'org.fcitx.Fcitx5|org.freedesktop.IBus'
```

确认 `org.freedesktop.IBus` 的进程是 `fcitx5`；本次启动 Fcitx5 后，它接管了该服务，GNOME 的 IBus daemon 随之退出。已打开的应用可能需要完全重启才能重新连接。

随后再次注销并重新登录，先用 `pgrep` 验证自启动，再完全退出并重新打开 kitty（包括 quick-access 下拉终端）。仅重新加载 kitty 配置或 `exec zsh -l` 不会更新已运行 kitty 进程的环境。

## 5. 使用与验证

| 按键 | 功能 |
| --- | --- |
| `Ctrl+Space` 或左 `Shift` | 中英文切换 |
| `-` / `=` 或 `↑` / `↓` | 拼音候选翻页 |
| `Tab` / `Shift+Tab` | 下一个 / 上一个候选 |
| `Ctrl+Alt+P` | 切换应用内预编辑显示 |

仓库的 zsh 配置也用 `Ctrl+Space` 接受灰色建议。输入法可能先消费这个按键；接受建议可使用行尾 `→`，或在 `fcitx5-configtool` 中调整输入法切换键。

在桌面会话的 kitty 内检查：

```bash
printf 'session=%s GLFW=%s GTK=%s QT=%s XMODIFIERS=%s\n' \
  "$XDG_SESSION_TYPE" "$GLFW_IM_MODULE" "$GTK_IM_MODULE" "$QT_IM_MODULE" "$XMODIFIERS"
pgrep -a -x fcitx5
fcitx5-remote
busctl --user call org.fcitx.Fcitx5 /controller org.fcitx.Fcitx.Controller1 CurrentInputMethod
busctl --user list --no-pager | grep -E 'org.fcitx.Fcitx5|org.freedesktop.IBus'
fc-match ':lang=zh-cn'
```

`fcitx5-remote -n` 在 Ubuntu 22.04 的 Fcitx5 5.0.14 中不可用；上面的 D-Bus 命令可查询当前输入法，中文激活时应返回 `s "pinyin"`。

预期环境是 `x11 / ibus / fcitx / fcitx / @im=fcitx`。`fcitx5-remote` 的状态值：`0` 为关闭，`1` 为未激活，`2` 为已激活；英文状态下返回 `1` 也是正常的。此命令反映当前输入上下文，焦点变化会影响结果。中文字体应能匹配到 Noto Sans CJK SC。

手动测试时先运行 `cat`，按 `Ctrl+Space`，输入 `nihao`，选中「你好」并按 Enter，确认终端正确显示；按 `Ctrl+C` 结束测试。

## 排查与撤销

- `Ctrl+Space` 无反应、无候选框：先检查 `pgrep -a -x fcitx5`，再检查上述 D-Bus 服务的进程名。如果 Fcitx5 没有运行，添加第 4 节的桌面自启动项并运行 `fcitx5 -d`，然后完全重启 kitty。
- 没有拼音：运行 `fcitx5-configtool`，确认列表包含 Keyboard - English (US) 和 Pinyin；检查中文插件包是否安装。
- 其他程序能输入、kitty 不行：检查 kitty 启动前是否已有 `GLFW_IM_MODULE=ibus`，以及 IBus 服务是否由 Fcitx5 提供。修改后重新登录并重启所有 kitty 进程。
- D-Bus 连接失败：在本机图形桌面会话中检查，不要从无桌面会话的 SSH、容器或隔离环境判断输入法状态。
- 显示方框：确认 `fonts-noto-cjk` 已安装，再运行 `fc-cache -f`。
- 需要撤销设置：退出 Fcitx5，从前面输出的备份目录复制原文件回 `~/.config/fcitx5/`；原本不存在的文件需单独移除。环境变量恢复为编辑前内容，并通过 `im-config` 选择原输入法，然后重新登录。
