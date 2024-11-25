import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 获取项目根目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from utils.config import Config

class NoteImporter:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # 加载样式表并保存
        self.STYLE_SHEET = self.load_stylesheet()
        if self.STYLE_SHEET:
            self.app.setStyleSheet(self.STYLE_SHEET)
            print("样式表已加载")
        else:
            print("未能加载样式表")
            
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
        style_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'resources', 'styles', 'minimalist.qss')
        print(f"尝试加载样式表: {style_path}")
        if os.path.exists(style_path):
            with open(style_path, 'r', encoding='utf-8') as f:
                style_content = f.read()
                print("样式表内容长度:", len(style_content))
                return style_content
        else:
            print("样式表文件不存在")
        return ""

if __name__ == "__main__":
    importer = NoteImporter()
    importer.run()
