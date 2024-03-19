# 这个可以捕捉到applsci-11-06083这篇paper所需要的鼠标数据

import Quartz
from AppKit import NSWorkspace
from pynput.mouse import Listener as MouseListener, Button
import pandas as pd
import time
import numpy as np

pd.set_option('display.float_format', '{:.6f}'.format)

def get_active_window_info():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
    active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
    active_app_name = active_app.localizedName() if active_app else 'Unknown'
    for window in window_list:
        if 'kCGWindowOwnerName' in window and window['kCGWindowOwnerName'] == active_app_name:
            return {
                'window_id': window.get('kCGWindowNumber', 'Unknown'),
                'active_app_name': active_app_name
            }
    return {'window_id': 'Unknown', 'active_app_name': active_app_name}

data = []

def on_move(x, y):
    window_info = get_active_window_info()
    data.append(['move', time.time(), window_info['active_app_name'], window_info['window_id'], x, y])

def on_click(x, y, button, pressed):
    button_type = 'left' if button == Button.left else 'right'
    event_type = f"{button_type}_{'down' if pressed else 'up'}"
    window_info = get_active_window_info()
    data.append([event_type, time.time(), window_info['active_app_name'], window_info['window_id'], x, y])

with MouseListener(on_move=on_move, on_click=on_click) as listener:
    time.sleep(3)  # listening for only 3 seconds to see sample data
    listener.stop()

df = pd.DataFrame(data, columns=['event_type', 'time', 'active_app_name', 'window_id', 'x', 'y'])

print(df.head())