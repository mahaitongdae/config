# 在 quick access terminal 中切换"全屏"和原始高度
# X11 下 kitty 不支持动态修改 panel 配置，所以直接改窗口像素尺寸
import json
import os

from kittens.tui.handler import result_handler
from kitty.fast_data_types import get_os_window_pos, get_os_window_size, glfw_primary_monitor_size, set_os_window_size

STATE_FILE = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), 'kitty-qa-fullscreen.json')


def main(args):
    pass


@result_handler(no_ui=True)
def handle_result(args, answer, target_window_id, boss):
    w = boss.window_id_map.get(target_window_id)
    if w is None:
        return
    osw = w.os_window_id
    sz = get_os_window_size(osw)
    if not sz:
        return
    key = f'{os.getpid()}:{osw}'
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except Exception:
        state = {}

    if key in state:
        # 已经是全屏，恢复原始尺寸
        width, height = state.pop(key)
    else:
        # 记录原始尺寸，然后拉伸到屏幕底部
        state[key] = [sz['width'], sz['height']]
        _, mon_h = glfw_primary_monitor_size()
        _, y = get_os_window_pos(osw)
        width, height = sz['width'], mon_h - y
    set_os_window_size(osw, width, height)

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)
