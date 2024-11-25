from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QMessageBox)
import re

class NoteSplitterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.note_input = QTextEdit()
        layout.addWidget(QLabel("请粘贴读书笔记:"))
        layout.addWidget(self.note_input)
        
        self.separator_input = QLineEdit()
        layout.addWidget(QLabel("分隔标识字符:"))
        layout.addWidget(self.separator_input)
        
        split_btn = QPushButton("拆分笔记")
        split_btn.clicked.connect(self.split_notes)
        layout.addWidget(split_btn)
        
        self.setLayout(layout)

    def split_notes(self):
        content = self.note_input.toPlainText()
        separator = self.separator_input.text().strip()
        
        if not separator:
            QMessageBox.warning(self, "警告", "请输入分隔标识字符")
            return
        
        lines = content.split('\n')
        split_notes = []
        current_note = []
        
        for line in lines:
            if separator in line:
                if current_note:
                    split_notes.append('\n'.join(current_note))
                    current_note = []
            current_note.append(line)
        
        if current_note:
            split_notes.append('\n'.join(current_note))
        
        if not split_notes:
            QMessageBox.warning(self, "警告", "没有找到有效的笔记")
            return
        
        self.split_notes = split_notes
        self.accept()

    def get_split_notes(self):
        return self.split_notes
