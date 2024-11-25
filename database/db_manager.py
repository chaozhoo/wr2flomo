import sqlite3
from contextlib import contextmanager
import os

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.db_path = self.config.get('db_path')
        if self.is_initialized():
            self.ensure_tables_exist()

    def is_initialized(self):
        return bool(self.db_path) and os.path.exists(self.db_path)

    def initialize_database(self, path):
        print(f"Initializing database at {path}")
        self.db_path = path
        self.config.set('db_path', path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.ensure_tables_exist()
        print("Database initialization complete.")

    def ensure_tables_exist(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    imported BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            conn.commit()

    @contextmanager
    def get_connection(self):
        if not self.db_path:
            raise ValueError("数据库路径未设置")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def add_notes(self, notes):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("INSERT INTO notes (content, imported) VALUES (?, ?)",
                               [(note['content'], note.get('imported', False)) for note in notes])
            conn.commit()

    def update_note(self, note):
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE notes
                SET content = ?, imported = ?
                WHERE id = ?
            ''', (note['content'], note.get('imported', False), note['id']))
            conn.commit()
        print(f"Note {note['id']} updated in database")

    def get_notes(self, imported=False):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, content FROM notes WHERE imported = ?", (imported,))
                return [{'id': row[0], 'content': row[1]} for row in cursor.fetchall()]
        except sqlite3.OperationalError as e:
            print(f"数据库操作错误: {e}")
            return []

    def clear_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes")
            conn.commit()

    def rename_database(self, new_path):
        os.rename(self.db_path, new_path)
        self.db_path = new_path
        self.config.set('db_path', new_path)

    def delete_note(self, note_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()

    def get_note(self, note_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, content, imported FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'content': row[1], 'imported': bool(row[2])}
            return None

    def get_notes_summary(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, substr(content, 1, 100) as content, imported FROM notes")
            return [{'id': row[0], 'content': row[1], 'imported': bool(row[2])} for row in cursor.fetchall()]

    def add_note(self, content, imported=False):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (content, imported) VALUES (?, ?)",
                           (content, imported))
            conn.commit()

    def mark_note_as_imported(self, note_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notes SET imported = ? WHERE id = ?", (True, note_id))
            conn.commit()
