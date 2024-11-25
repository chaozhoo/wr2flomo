import sys
import os
import asyncio
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtCore import QTimer
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from utils.config import Config

class NoteImporter:
    def __init__(self):
        self.STYLE_SHEET = """
            * {
                font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
            }
        """
        self.app = QApplication(sys.argv)
        self.load_stylesheet()
        
        self.config = Config()
        self.db_manager = DatabaseManager(self.config)
        
        # 检查数据库路径是否已设置
        if not self.db_manager.is_initialized():
            self.set_initial_db_path()
        else:
            self.db_manager.ensure_tables_exist()
        
        self.main_window = None
        self.db_initialized = False

    def set_initial_db_path(self):
        default_path = os.path.join(os.path.expanduser("~"), "wr2flomo.db")
        db_path, _ = QFileDialog.getSaveFileName(None, "选择数据库文件位置", default_path, "SQLite 数据库 (*.db)")
        if db_path:
            self.db_manager.initialize_database(db_path)
        else:
            raise ValueError("未选择数据库路径，程序无法继续。")

    async def initialize_db(self):
        if not self.db_manager.is_initialized():
            self.set_initial_db_path()
        else:
            await asyncio.to_thread(self.db_manager.ensure_tables_exist)
        self.db_initialized = True

    def show_main_window(self):
        if self.main_window is None:
            self.main_window = MainWindow(self.db_manager, self.config, self.STYLE_SHEET)
        self.main_window.show()

    def run(self):
        self.show_main_window()
        asyncio.run(self.initialize_db())
        QTimer.singleShot(0, self.check_db_initialized)
        sys.exit(self.app.exec())

    def check_db_initialized(self):
        if self.db_initialized:
            self.main_window.enable_features()  # 假设有这样一个方法来启用依赖数据库的功能
        else:
            QTimer.singleShot(100, self.check_db_initialized)

    def load_stylesheet(self):
        self.app.setStyleSheet(self.STYLE_SHEET)

if __name__ == "__main__":
    importer = NoteImporter()
    importer.run()
