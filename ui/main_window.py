from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, 
                             QTreeWidget, QTreeWidgetItem, QSplitter, QFileDialog, QMessageBox,
                             QCheckBox, QProgressDialog, QApplication, QInputDialog, QAbstractItemView, QListWidget, QListWidgetItem, QTabWidget, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QThreadPool
from PyQt6.QtGui import QShortcut, QKeySequence, QFontMetrics
import os
import sys
from ui.note_splitter import NoteSplitterDialog
from ui.note_editor import NoteEditorWidget
from ui.note_editor_manager import NoteEditorManager
from utils.flomo_api import FlomoAPI
import re

class ImportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, flomo_api, notes, custom_tag, add_default_tag):
        super().__init__()
        self.flomo_api = flomo_api
        self.notes = notes
        self.custom_tag = custom_tag
        self.add_default_tag = add_default_tag

    def run(self):
        for i, note in enumerate(self.notes):
            content = note['content']
            if self.custom_tag:
                content += f"\n#{self.custom_tag}"
            if self.add_default_tag:
                content += "\n#wr2flomo"
            if self.flomo_api.send_note(content):
                note['imported'] = True
            self.progress.emit(i + 1)
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self, db_manager, config, style_sheet=None):
        super().__init__()
        print("Initializing MainWindow...")
        self.db_manager = db_manager
        self.config = config
        self._left_panel = None
        self._right_panel = None
        self._note_tree = None
        self._api_url_input = None
        self._custom_tag_input = None
        self._always_add_default_tag = None
        self.thread_pool = QThreadPool()
        
        # 初始化 note_editor
        self.note_editor = NoteEditorWidget({"id": None, "content": ""}, self)
        self.note_editor.note_updated.connect(self.on_note_updated)
        
        if style_sheet:
            app = QApplication.instance()
            if app:
                app.setStyleSheet(style_sheet)
        
        print("Calling init_ui...")
        self.init_ui()
        print("Calling ensure_database_initialized...")
        self.ensure_database_initialized()
        print("MainWindow initialization complete.")

    def ensure_database_initialized(self):
        if not self.db_manager.is_initialized():
            self.create_new_database()
        else:
            self.db_manager.ensure_tables_exist()
        self.update_note_list()

    def create_new_database(self):
        file_dialog = QFileDialog()
        db_path, _ = file_dialog.getSaveFileName(
            self,
            "新建数据库文件",
            "",
            "SQLite 数据库 (*.db)"
        )
        
        if db_path:
            try:
                self.db_manager.initialize_database(db_path)
                self.config.set('db_path', db_path)
                self.update_db_name_display()
                self.enable_features()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"创建数据库失败：{str(e)}")

    def init_ui(self):
        print("Setting up UI...")
        self.setWindowTitle("读书笔记导入flomo")
        self.setGeometry(100, 100, 1000, 600)

        main_layout = QHBoxLayout()
        print("Creating left panel...")
        left_panel = self.create_left_panel()
        print("Creating right panel...")
        right_panel = self.create_right_panel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

        print("Updating note list...")
        self.update_note_list()
        print("UI setup complete.")

        self.setup_shortcuts()

        # 创建笔记编辑器
        self.note_editor = NoteEditorWidget({"id": None, "content": ""}, self)
        self.note_editor.note_updated.connect(self.on_note_updated)
        self.note_editor.hide()  # 初始时隐藏编辑器

        self._note_tabs.currentChanged.connect(self.on_tab_changed)

        # 初始化时为第一个标签页设置信号连接
        first_tab = self._note_tabs.widget(0)
        if isinstance(first_tab, QListWidget):
            first_tab.itemSelectionChanged.connect(self.on_selection_changed)

    @property
    def left_panel(self):
        if self._left_panel is None:
            self._left_panel = self.create_left_panel()
        return self._left_panel

    @property
    def right_panel(self):
        if self._right_panel is None:
            self._right_panel = self.create_right_panel()
        return self._right_panel

    @property
    def note_tree(self):
        if self._note_tree is None:
            self._note_tree = QTreeWidget()
            self._note_tree.setHeaderHidden(True)
            self._note_tree.itemDoubleClicked.connect(self.open_note_editor)
        return self._note_tree

    @property
    def api_url_input(self):
        if self._api_url_input is None:
            self._api_url_input = QLineEdit()
            self._api_url_input.setText(self.config.get_api_url())
            self._api_url_input.textChanged.connect(lambda text: self.config.set_api_url(text))
        return self._api_url_input

    @property
    def custom_tag_input(self):
        if self._custom_tag_input is None:
            self._custom_tag_input = QLineEdit()
            self._custom_tag_input.setText(self.config.get('custom_tag', ''))
            self._custom_tag_input.textChanged.connect(lambda text: self.config.set('custom_tag', text))
        return self._custom_tag_input

    @property
    def always_add_default_tag(self):
        if self._always_add_default_tag is None:
            self._always_add_default_tag = QCheckBox("总是添加默认标签")
            self._always_add_default_tag.setChecked(self.config.get('always_add_default_tag', True))
            self._always_add_default_tag.stateChanged.connect(
                lambda state: self.config.set('always_add_default_tag', state == Qt.CheckState.Checked.value)
            )
        return self._always_add_default_tag

    def create_left_panel(self):
        left_widget = QWidget()
        layout = QVBoxLayout()

        # 数据库管理部分
        db_layout = QHBoxLayout()
        self.db_name_label = QLabel(self.config.get('db_path', '未选择数据库'))
        db_layout.addWidget(self.db_name_label)
        rename_btn = QPushButton("重命名")
        rename_btn.clicked.connect(self.rename_database)
        db_layout.addWidget(rename_btn)
        load_btn = QPushButton("加载笔记库")
        load_btn.clicked.connect(self.load_database)
        db_layout.addWidget(load_btn)
        layout.addLayout(db_layout)

        # 笔记操作按钮
        button_layout = QHBoxLayout()
        paste_btn = QPushButton("粘贴读书笔记")
        paste_btn.clicked.connect(self.open_note_splitter)
        button_layout.addWidget(paste_btn)
        new_db_btn = QPushButton("新建笔记库")
        new_db_btn.clicked.connect(self.create_new_database)
        button_layout.addWidget(new_db_btn)
        copy_db_btn = QPushButton("创建库副本")
        copy_db_btn.clicked.connect(self.create_database_copy)
        button_layout.addWidget(copy_db_btn)
        layout.addLayout(button_layout)

        # 笔记管理面板
        layout.addWidget(QLabel("笔记管理面板"))
        self.note_stats_label = QLabel("总数: 0 / 已选中: 0")
        layout.addWidget(self.note_stats_label)

        # 替换原来的 QListWidget
        self._note_tabs = QTabWidget()
        self._unimported_list = QListWidget()
        self._imported_list = QListWidget()
        self._skipped_list = QListWidget()
        
        # 设置选择模式
        for list_widget in [self._unimported_list, self._imported_list, self._skipped_list]:
            list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            list_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        self._note_tabs.addTab(self._unimported_list, "未导入")
        self._note_tabs.addTab(self._imported_list, "已导入")
        self._note_tabs.addTab(self._skipped_list, "已跳过")
        
        # 初始化时为第一个标签页设置信号连接
        self._unimported_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self._note_tabs)

        left_widget.setLayout(layout)
        return left_widget

    def on_selection_changed(self):
        current_tab = self._note_tabs.currentWidget()
        selected_items = current_tab.selectedItems()
        if len(selected_items) == 1:
            self.open_note_editor(selected_items[0])
        self.update_note_stats()

    def create_right_panel(self):
        right_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("笔记导入"))

        import_btn = QPushButton("导入选中笔记")
        import_btn.clicked.connect(self.import_selected_notes)
        layout.addWidget(import_btn)

        layout.addWidget(QLabel("flomo API URL:"))
        self._api_url_input = QLineEdit()
        self._api_url_input.setEchoMode(QLineEdit.EchoMode.Password)  # 设置为密码模式
        layout.addWidget(self._api_url_input)

        layout.addWidget(QLabel("自定义标签:"))
        self._custom_tag_input = QLineEdit()
        self._custom_tag_input.textChanged.connect(self.update_checkbox_state)
        layout.addWidget(self._custom_tag_input)

        self._always_add_default_tag = QCheckBox("总是添加默认标签")
        self._always_add_default_tag.setChecked(True)  # 默认选中
        layout.addWidget(self._always_add_default_tag)

        self.update_checkbox_state()  # 初始化复选框状态

        # Add separator
        layout.addWidget(QLabel("批量操作"))
        
        # Find and Replace section
        find_replace_layout = QHBoxLayout()
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("查找内容")
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("替换为")
        self.use_regex = QCheckBox("使用正则表达式")
        
        find_replace_layout.addWidget(self.find_input)
        find_replace_layout.addWidget(self.replace_input)
        layout.addLayout(find_replace_layout)
        layout.addWidget(self.use_regex)
        
        replace_btn = QPushButton("查找替换")
        replace_btn.clicked.connect(self.perform_find_replace)
        layout.addWidget(replace_btn)
        
        # Remove empty lines button
        remove_empty_btn = QPushButton("删除所有空行")
        remove_empty_btn.clicked.connect(self.remove_empty_lines)
        layout.addWidget(remove_empty_btn)

        # 添加撤销重做按钮
        undo_redo_layout = QHBoxLayout()
        
        self.undo_btn = QPushButton("撤销")
        self.undo_btn.setShortcut("Ctrl+Z")
        self.undo_btn.clicked.connect(self.undo_operation)
        self.undo_btn.setEnabled(False)
        
        self.redo_btn = QPushButton("重做")
        self.redo_btn.setShortcut("Ctrl+Y")
        self.redo_btn.clicked.connect(self.redo_operation)
        self.redo_btn.setEnabled(False)
        
        undo_redo_layout.addWidget(self.undo_btn)
        undo_redo_layout.addWidget(self.redo_btn)
        layout.addLayout(undo_redo_layout)

        right_widget.setLayout(layout)
        return right_widget

    def perform_find_replace(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        use_regex = self.use_regex.isChecked()
        
        if not find_text:
            QMessageBox.warning(self, "警告", "请输入要查找的内容")
            return
            
        reply = QMessageBox.question(self, '确认', 
                                   f'确定要进行全局替换吗？\n查找：{find_text}\n替换为：{replace_text}',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            try:
                modified_count = self.db_manager.find_and_replace(
                    find_text, replace_text, use_regex)
                self.update_note_list()
                self.update_undo_redo_buttons()  # 更新按钮状态
                QMessageBox.information(self, "完成", 
                                      f"已修改 {modified_count} 条笔记")
            except re.error:
                QMessageBox.warning(self, "错误", "正则表达式格式错误")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"操作失败：{str(e)}")

    def remove_empty_lines(self):
        reply = QMessageBox.question(self, '确认', 
                                   '确定要删除所有笔记中的空行吗？',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            try:
                modified_count = self.db_manager.remove_empty_lines()
                self.update_note_list()
                QMessageBox.information(self, "完成", 
                                      f"已修改 {modified_count} 条笔记")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"操作失败：{str(e)}")

    def open_note_splitter(self):
        dialog = NoteSplitterDialog(self)
        if dialog.exec():
            split_notes = dialog.get_split_notes()
            if split_notes:
                progress = QProgressDialog("正在添加笔记...", "取消", 0, len(split_notes), self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                
                notes_to_add = []
                for i, content in enumerate(split_notes):
                    notes_to_add.append({'content': content, 'imported': False})
                    progress.setValue(i)
                    if progress.wasCanceled():
                        break
                
                if notes_to_add:
                    self.db_manager.add_notes(notes_to_add)
                    self.update_note_list()
                    QMessageBox.information(self, "成功", f"已成功拆分并添加 {len(notes_to_add)} 条笔记")
                else:
                    QMessageBox.warning(self, "警告", "操作已取消")
            else:
                QMessageBox.warning(self, "警告", "没有找到有效的笔记")

    def open_note_editor(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id is not None:
            note = self.db_manager.get_note(note_id)
            if note:
                if 'imported' not in note:
                    note['imported'] = False
                self.note_editor.set_note(note)
                self.note_editor.show()
                self.note_editor.raise_()
            else:
                QMessageBox.warning(self, "错误", "无法找到选中的笔记")

    def update_note(self, updated_note):
        self.db_manager.update_note(updated_note)
        self.update_note_list()

    def calculate_visible_chars(self, text, max_width):
        font_metrics = QFontMetrics(self._note_tree.font())
        ellipsis = '...'
        visible_text = text
        while font_metrics.horizontalAdvance(visible_text + ellipsis) > max_width and len(visible_text) > 0:
            visible_text = visible_text[:-1]
        return visible_text + (ellipsis if len(visible_text) < len(text) else '')

    def update_note_list(self):
        self._unimported_list.clear()
        self._imported_list.clear()
        self._skipped_list.clear()
        
        notes = self.db_manager.get_notes_summary()
        for note in notes:
            content = self.truncate_content(note['content'], 100)
            item = QListWidgetItem(content)
            item.setData(Qt.ItemDataRole.UserRole, note['id'])
            
            if note['skipped']:
                self._skipped_list.addItem(item)
            elif note['imported']:
                self._imported_list.addItem(item)
            else:
                self._unimported_list.addItem(item)
        
        # 更新标签页显示
        self._note_tabs.setTabText(0, f"未导入 ({self._unimported_list.count()})")
        self._note_tabs.setTabText(1, f"已导入 ({self._imported_list.count()})")
        self._note_tabs.setTabText(2, f"已跳过 ({self._skipped_list.count()})")
        
        self.update_note_stats()

    def truncate_content(self, content, max_length):
        if len(content) > max_length:
            return content[:max_length] + '...'
        return content

    def update_note_stats(self):
        unimported_count = self._unimported_list.count()
        imported_count = self._imported_list.count()
        total = unimported_count + imported_count
        selected = len(self._unimported_list.selectedItems()) + len(self._imported_list.selectedItems())
        
        self._note_tabs.setTabText(0, f"未导入 ({unimported_count})")
        self._note_tabs.setTabText(1, f"已导入 ({imported_count})")
        self.note_stats_label.setText(f"总数: {total} / 已选中: {selected}")

    def rename_database(self):
        new_name, ok = QInputDialog.getText(self, "重命名笔记库", "新的笔记库名称：", text=os.path.basename(self.db_manager.db_path))
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(self.db_manager.db_path), new_name)
            if new_path.endswith('.db'):
                try:
                    os.rename(self.db_manager.db_path, new_path)
                    self.db_manager.db_path = new_path
                    self.config.set('db_path', new_path)
                    self.db_name_label.setText(os.path.basename(new_path))
                    QMessageBox.information(self, "成", f"笔记库已重命名为：{new_name}")
                except OSError as e:
                    QMessageBox.warning(self, "错误", f"重命名失败：{str(e)}")
            else:
                QMessageBox.warning(self, "错误", "笔记库名称必须以 .db 结尾")

    def load_database(self):
        """加载数据库"""
        file_dialog = QFileDialog()
        db_path, _ = file_dialog.getOpenFileName(
            self,
            "选择数据库文件",
            "",
            "SQLite 数据库 (*.db)"
        )
        
        if db_path:
            try:
                self.db_manager.db_path = db_path
                self.db_manager.ensure_tables_exist()
                self.config.set('db_path', db_path)
                self.update_db_name_display()
                self.enable_features()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载数据库失败：{str(e)}")

    def create_database_copy(self):
        """创建当前数据库的副本并切换到新数据库"""
        try:
            # 保存当前数据库路径作为备份
            old_path = self.db_manager.db_path
            old_name = os.path.basename(old_path)
            
            # 创建副本并获取新路径
            new_path = self.db_manager.create_database_copy()
            new_name = os.path.basename(new_path)
            
            # 更新配置
            self.config.set('db_path', new_path)
            
            # 更新UI显示
            self.update_db_name_display()
            self.update_note_list()
            
            # 显示成功消息
            QMessageBox.information(
                self, 
                "成功", 
                f"已创建并切换到新数据库：\n{new_name}\n\n原数据库：\n{old_name}"
            )
            
            # 启用相关功能
            self.enable_features()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))

    def import_selected_notes(self):
        current_tab = self._note_tabs.currentWidget()
        selected_items = current_tab.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择要导入的笔记")
            return

        api_url = self._api_url_input.text().strip()
        if not api_url:
            QMessageBox.warning(self, "警告", "请输入有效的 flomo API URL")
            return

        custom_tag = self._custom_tag_input.text().strip()
        always_add_default_tag = self._always_add_default_tag.isChecked()

        flomo_api = FlomoAPI(api_url)

        progress = QProgressDialog("正在导入笔记...", "取", 0, len(selected_items), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        imported_count = 0
        for i, item in enumerate(selected_items):
            if progress.wasCanceled():
                break

            note_id = item.data(Qt.ItemDataRole.UserRole)
            note = self.db_manager.get_note(note_id)  # 获取完整的笔记内容
            if not note:
                print(f"无法找到ID为{note_id}的笔记")
                continue

            content = note['content']  # 使用完整的笔记内容

            tags = []
            if custom_tag:
                tags.append(custom_tag)
            if always_add_default_tag or not custom_tag:
                tags.append("#WRead2flomo")

            content_with_tags = content
            if tags:
                content_with_tags += "\n\n" + " ".join(tags)

            try:
                response = flomo_api.create_memo(content_with_tags)
                if response['code'] == 0:
                    self.db_manager.mark_note_as_imported(note_id)
                    imported_count += 1
                else:
                    print(f"导入笔记失败: {response['message']}")
            except Exception as e:
                print(f"导入笔记时发生错误: {str(e)}")

        progress.setValue(len(selected_items))
        self.update_note_list()
        QMessageBox.information(self, "导入完成", f"成功导入 {imported_count} 条笔记")
        self.update_note_stats()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+V"), self, self.open_note_splitter)
        QShortcut(QKeySequence("Ctrl+N"), self, self.create_new_database)
        QShortcut(QKeySequence("Ctrl+O"), self, self.load_database)
        QShortcut(QKeySequence("Ctrl+I"), self, self.import_selected_notes)

    def handle_drop(self, event):
        mime = event.mimeData()
        if mime.hasText():
            text = mime.text()
            self.db_manager.add_notes([text])
            self.update_note_list()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_notes()
        else:
            super().keyPressEvent(event)

    def delete_selected_notes(self):
        selected_items = self._note_list.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, '确', f'确定要删除选中的 {len(selected_items)} 条笔记吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                note_id = item.data(Qt.ItemDataRole.UserRole)
                self.db_manager.delete_note(note_id)
            self.update_note_list()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_note_list()  # 窗口大小改变时更新笔记列表

    def update_checkbox_state(self):
        if not self._custom_tag_input.text().strip():
            self._always_add_default_tag.setChecked(True)
            self._always_add_default_tag.setEnabled(False)
        else:
            self._always_add_default_tag.setEnabled(True)

    def on_note_updated(self, updated_note):
        print(f"Updating note: {updated_note['id']}")
        self.db_manager.update_note(updated_note)
        self.update_note_list()
        print("Note updated successfully")

    def on_tab_changed(self, index):
        current_tab = self._note_tabs.widget(index)
        if isinstance(current_tab, QListWidget):
            # 确保连接当前标签页的信号
            try:
                current_tab.itemSelectionChanged.disconnect(self.on_selection_changed)
            except TypeError:
                pass  # 如果信号未连接，忽略错误
            current_tab.itemSelectionChanged.connect(self.on_selection_changed)

        # 断开其他标签页的连接
        other_index = 1 - index  # 假设只有两个标签页
        other_tab = self._note_tabs.widget(other_index)
        if isinstance(other_tab, QListWidget):
            try:
                other_tab.itemSelectionChanged.disconnect(self.on_selection_changed)
            except TypeError:
                pass  # 如果信号未连接，忽略错误

    def enable_features(self):
        print("启用依赖数据库的功能")
        self.update_note_list()
        self.note_stats_label.setEnabled(True)
        self._note_tabs.setEnabled(True)
        # 启用其他可能依赖数据库的UI元素

    def update_undo_redo_buttons(self):
        """更新撤销重做按钮状态"""
        self.undo_btn.setEnabled(bool(self.db_manager.history))
        self.redo_btn.setEnabled(bool(self.db_manager.future))

    def undo_operation(self):
        """执行撤销操作"""
        if self.db_manager.undo():
            self.update_note_list()
            self.update_undo_redo_buttons()
            QMessageBox.information(self, "完成", "已撤销上一次操作")
        else:
            QMessageBox.warning(self, "提示", "没有可撤销的操作")

    def redo_operation(self):
        """执行重做操作"""
        if self.db_manager.redo():
            self.update_note_list()
            self.update_undo_redo_buttons()
            QMessageBox.information(self, "完成", "已重做操作")
        else:
            QMessageBox.warning(self, "提示", "没有可重做的操作")

    def update_db_name_display(self):
        """更新数据库名称显示"""
        db_path = self.config.get('db_path', '')
        if db_path:
            db_name = os.path.basename(db_path)
            self.db_name_label.setText(db_name)
            # 添加工具提示显示完整路径
            self.db_name_label.setToolTip(db_path)
        else:
            self.db_name_label.setText("未选择数据库")
            self.db_name_label.setToolTip("")

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu()
        current_list = self.sender()
        selected_items = current_list.selectedItems()
        
        if not selected_items:
            return
            
        # 根据当前标签页添加不同的菜单项
        current_tab_index = self._note_tabs.currentIndex()
        if current_tab_index == 0:  # 未导入标签页
            skip_action = menu.addAction("跳过选中笔记")
            skip_action.triggered.connect(lambda: self.skip_selected_notes(selected_items))
        elif current_tab_index == 2:  # 已跳过标签页
            restore_action = menu.addAction("恢复笔记")
            restore_action.triggered.connect(lambda: self.restore_skipped_notes(selected_items))
        
        # 显示菜单
        menu.exec(current_list.mapToGlobal(position))

    def skip_selected_notes(self, selected_items):
        """将选中的笔记标记为已跳过"""
        reply = QMessageBox.question(
            self, 
            '确认', 
            f'确定要跳过选中的 {len(selected_items)} 条笔记吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                note_id = item.data(Qt.ItemDataRole.UserRole)
                self.db_manager.mark_note_as_skipped(note_id)
            self.update_note_list()

    def restore_skipped_notes(self, selected_items):
        """将选中的已跳过笔记恢复到未导入状态"""
        if not selected_items:
            return
        
        reply = QMessageBox.question(
            self, 
            '确认', 
            f'确定要恢复选中的 {len(selected_items)} 条笔记吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            restored_count = 0
            for item in selected_items:
                note_id = item.data(Qt.ItemDataRole.UserRole)
                if self.db_manager.restore_skipped_note(note_id):
                    restored_count += 1
            
            if restored_count > 0:
                self.update_note_list()
                QMessageBox.information(
                    self, 
                    "完成", 
                    f"已恢复 {restored_count} 条笔记到未导入列表"
                )
            else:
                QMessageBox.warning(self, "提示", "没有笔记被恢复")




























































