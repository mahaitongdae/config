"""Zoom the current terminal without undoing the X11 panel's F11 size."""
from kittens.tui.handler import result_handler
from kitty.fast_data_types import (
    get_os_window_size,
    layer_shell_config_for_os_window,
    set_os_window_size,
)


def main(args):
    pass


@result_handler(no_ui=True)
def handle_result(args, answer, target_window_id, boss):
    window = boss.window_id_map.get(target_window_id)
    if window is None:
        return
    amount = float(args[1])
    osw = window.os_window_id
    size = get_os_window_size(osw)
    is_panel = layer_shell_config_for_os_window(osw) is not None
    boss.change_font_size(False, '+' if amount > 0 else '-', abs(amount))
    # Panels otherwise recalculate their pixel height from the configured lines.
    # Restore after that resize, leaving the F11 saved normal size untouched.
    if is_panel and size:
        set_os_window_size(osw, size['width'], size['height'])
