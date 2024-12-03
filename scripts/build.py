import PyInstaller.__main__
import os
import sys

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build():
    args = [
        os.path.join(ROOT_DIR, 'src', 'main.py'),
        '--name=WR2Flomo',
        '--windowed',
        '--onefile',
        '--icon=' + os.path.join(ROOT_DIR, 'resources', 'icons', 'app.ico'),
        '--add-data=' + os.path.join(ROOT_DIR, 'resources') + os.pathsep + 'resources',
        '--add-data=' + os.path.join(ROOT_DIR, 'resources', 'styles', 'minimalist.qss') + os.pathsep + os.path.join('resources', 'styles'),
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtGui',
        '--clean',
        '--noupx'
    ]
    
    if sys.platform.startswith('win'):
        args.extend(['--runtime-hook=' + os.path.join(ROOT_DIR, 'scripts', 'windows_hook.py')])
    elif sys.platform.startswith('darwin'):
        args.extend(['--runtime-hook=' + os.path.join(ROOT_DIR, 'scripts', 'macos_hook.py')])
    
    PyInstaller.__main__.run(args)

if __name__ == '__main__':
    build()
