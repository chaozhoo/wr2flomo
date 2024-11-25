import os
import sys

def setup_macos():
    if getattr(sys, 'frozen', False):
        os.environ['QT_MAC_WANTS_LAYER'] = '1'
        os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt6', 'Qt', 'plugins')

setup_macos()  # 确保函数被调用 