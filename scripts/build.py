import PyInstaller.__main__
import sys
import os

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build():
    args = [
        os.path.join(ROOT_DIR, 'src', 'main.py'),
        '--name=WR2Flomo',
        '--windowed',
        '--onefile',
        '--icon=' + os.path.join(ROOT_DIR, 'resources', 'icons', 'app.ico'),
        '--add-data=' + os.path.join(ROOT_DIR, 'resources', 'styles') + ':styles',
        '--add-data=' + os.path.join(ROOT_DIR, 'src', 'ui') + ':ui',
        '--add-data=' + os.path.join(ROOT_DIR, 'src', 'database') + ':database',
        '--add-data=' + os.path.join(ROOT_DIR, 'src', 'utils') + ':utils',
        '--paths=' + os.path.join(ROOT_DIR, 'src'),
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=ui.main_window',
        '--hidden-import=database.db_manager',
        '--hidden-import=utils.config',
        '--clean',
        '--noupx',
        '--debug=all'
    ]
    
    if sys.platform.startswith('win'):
        args.extend(['--runtime-hook=' + os.path.join(ROOT_DIR, 'scripts', 'windows_hook.py')])
    elif sys.platform.startswith('darwin'):
        args.extend([
            '--runtime-hook=' + os.path.join(ROOT_DIR, 'scripts', 'macos_hook.py'),
            '--target-architecture=x86_64,arm64'
        ])
    
    PyInstaller.__main__.run(args)

if __name__ == '__main__':
    build() 