from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

class NoteEditorWidget(QWidget):
    note_updated = pyqtSignal(dict)

    def __init__(self, note, parent=None):
        super().__init__(parent, Qt.WindowType.Tool)  # 使用Tool窗口类型使其成为浮动面板
        self.note = note
        self.init_ui()
        self.setup_auto_save()

    def init_ui(self):
        self.setWindowTitle("编辑笔记")
        layout = QVBoxLayout()

        self.note_edit = QPlainTextEdit()
        self.note_edit.setPlainText(self.note['content'])
        layout.addWidget(self.note_edit)

        save_btn = QPushButton("保存 (Ctrl+S)")
        save_btn.clicked.connect(self.save_note)
        layout.addWidget(save_btn)

        self.setLayout(layout)

        # 添加快捷键
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_note)

    def save_note(self):
        self.note['content'] = self.note_edit.toPlainText()
        self.note['imported'] = self.note.get('imported', False)  # 确保包含 'imported' 字段
        self.note_updated.emit(self.note)

    def setup_auto_save(self):
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.save_note)
        self.auto_save_timer.start(60000)  # 每60秒自动保存一次

    def set_note(self, note):
        self.note = note
        self.note_edit.setPlainText(note['content'])
        self.setWindowTitle(f"编辑笔记 - ID: {note['id']}")

    def closeEvent(self, event):
        self.save_note()  # 关闭窗口时保存笔记
        super().closeEvent(event)
