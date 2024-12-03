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
        '--add-data=' + os.path.join(ROOT_DIR, 'resources') + os.pathsep + 'resources',
        '--add-data=' + os.path.join(ROOT_DIR, 'src', 'ui') + os.pathsep + 'ui',
        '--add-data=' + os.path.join(ROOT_DIR, 'src', 'database') + os.pathsep + 'database',
        '--add-data=' + os.path.join(ROOT_DIR, 'src', 'utils') + os.pathsep + 'utils',
        '--paths=' + os.path.join(ROOT_DIR, 'src'),
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=cryptography',
        '--hidden-import=keyring',
        '--hidden-import=requests',
        '--hidden-import=ui.main_window',
        '--hidden-import=database.db_manager',
        '--hidden-import=utils.config',
        '--hidden-import=src.ui.display_settings_dialog',
        '--exclude-module=black',
        '--exclude-module=flake8',
        '--exclude-module=python-dotenv',
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