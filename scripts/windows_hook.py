import os
import sys

def setup_windows():
    if getattr(sys, 'frozen', False):
        os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt6', 'Qt', 'plugins')

setup_windows()  # 确保函数被调用 