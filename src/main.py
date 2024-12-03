import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox

# 获取应用程序的基础路径
if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    BASE_DIR = sys._MEIPASS
else:
    # 如果是开发环境
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)

from src.ui.main_window import MainWindow
from src.database.db_manager import DatabaseManager
from src.utils.config import Config

class NoteImporter:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # 加载样式表
        self.STYLE_SHEET = self.load_stylesheet()
        if self.STYLE_SHEET:
            print("样式表已加载")
        else:
            print("未能加载样式表")
            # 使用默认样式
            self.STYLE_SHEET = """
                * {
                    font-family: Arial, "Microsoft YaHei", SimSun, sans-serif;
                }
            """
        
        # 设置样式表
        self.app.setStyleSheet(self.STYLE_SHEET)
        
        self.config = Config()
        self.db_manager = DatabaseManager(self.config)
        
        # 显示数据库选择对话框
        if not self.show_database_selector():
            sys.exit(0)
            
        self.main_window = None
        self.db_initialized = True

    def show_database_selector(self):
        from src.ui.database_selector import DatabaseSelectorDialog
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
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.dirname(__file__))
            
            style_path = os.path.join(base_path, 'resources', 'styles', 'minimalist.qss')
            print(f"尝试加载样式表: {style_path}")
            
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    style_content = f.read()
                    print("样式表内容预览:")
                    return style_content
        except Exception as e:
            print(f"加载样式表时出错: {str(e)}")
        return ""

if __name__ == "__main__":
    importer = NoteImporter()
    importer.run()
