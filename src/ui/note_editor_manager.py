from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class NoteEditorManager(QWidget):
    note_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.current_note = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("编辑笔记")
        layout = QVBoxLayout()

        self.note_edit = QTextEdit()
        layout.addWidget(self.note_edit)

        save_btn = QPushButton("保存 (Ctrl+S)")
        save_btn.clicked.connect(self.save_note)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def set_note(self, note):
        self.current_note = note
        self.note_edit.setText(note['content'])
        self.setWindowTitle(f"编辑笔记 - ID: {note['id']}")

    def save_note(self):
        if self.current_note:
            self.current_note['content'] = self.note_edit.toPlainText()
            self.note_updated.emit(self.current_note)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.save_note()
        else:
            super().keyPressEvent(event)
