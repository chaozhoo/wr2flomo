from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, 
                           QLabel, QFileDialog)
from PyQt6.QtCore import Qt

class DatabaseSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_path = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("选择笔记库")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        # 添加说明文本
        label = QLabel("请选择操作：")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        # 新建笔记库按钮
        new_db_btn = QPushButton("新建笔记库")
        new_db_btn.clicked.connect(self.create_new_database)
        layout.addWidget(new_db_btn)
        
        # 加载笔记库按钮
        load_db_btn = QPushButton("加载笔记库")
        load_db_btn.clicked.connect(self.load_database)
        layout.addWidget(load_db_btn)
        
        self.setLayout(layout)
    
    def create_new_database(self):
        file_dialog = QFileDialog()
        db_path, _ = file_dialog.getSaveFileName(
            self,
            "新建数据库文件",
            "",
            "SQLite 数据库 (*.db)"
        )
        if db_path:
            self.selected_path = db_path
            self.accept()
    
    def load_database(self):
        file_dialog = QFileDialog()
        db_path, _ = file_dialog.getOpenFileName(
            self,
            "选择数据库文件",
            "",
            "SQLite 数据库 (*.db)"
        )
        if db_path:
            self.selected_path = db_path
            self.accept() 