from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QSpinBox, QPushButton)
from PyQt6.QtCore import Qt

class DisplaySettingsDialog(QDialog):
    def __init__(self, parent=None, current_font_size=16):
        super().__init__(parent)
        self.font_size = current_font_size
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("显示设置")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        # 字体大小设置
        font_size_layout = QHBoxLayout()
        label = QLabel("字体大小(px):")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.font_size)
        font_size_layout.addWidget(label)
        font_size_layout.addWidget(self.font_size_spin)
        layout.addLayout(font_size_layout)
        
        # 确定取消按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_font_size(self):
        return self.font_size_spin.value() 