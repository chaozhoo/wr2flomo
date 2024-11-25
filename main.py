import sys
import os
import asyncio
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
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
        
        # 显示数据库选择对话框
        if not self.show_database_selector():
            sys.exit(0)
            
        self.main_window = None
        self.db_initialized = True

    def show_database_selector(self):
        from ui.database_selector import DatabaseSelectorDialog
        dialog = DatabaseSelectorDialog()
        if dialog.exec():
            db_path = dialog.selected_path
            if db_path:
                try:
                    self.db_manager.initialize_database(db_path)
                    return True
                except Exception as e:
                    QMessageBox.critical(None, "错误", f"初始化数据库失败：{str(e)}")
        return False

    def show_main_window(self):
        if self.main_window is None:
            self.main_window = MainWindow(self.db_manager, self.config, self.STYLE_SHEET)
        self.main_window.show()

    def run(self):
        self.show_main_window()
        sys.exit(self.app.exec())

    def load_stylesheet(self):
        self.app.setStyleSheet(self.STYLE_SHEET)

if __name__ == "__main__":
    importer = NoteImporter()
    importer.run()
