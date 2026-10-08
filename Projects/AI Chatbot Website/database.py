"""Session-scoped history; legacy chats.db is left untouched."""
import sqlite3
from pathlib import Path


class ConversationChanged(Exception):
    pass


def create_database(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )""")
        con.execute("CREATE INDEX IF NOT EXISTS messages_chat ON messages(chat_id, id)")


def load_messages(path, chat_id):
    with sqlite3.connect(path) as con:
        rows = con.execute(
            "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id", (chat_id,)
        ).fetchall()
    return [{"role": role, "content": content} for role, content in rows]


def save_turn(path, chat_id, message, reply, expected_count):
    # Commit both messages together, only if another request has not changed history.
    with sqlite3.connect(path) as con:
        con.execute("BEGIN IMMEDIATE")
        count = con.execute("SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,)).fetchone()[0]
        if count != expected_count:
            raise ConversationChanged()
        con.executemany(
            "INSERT INTO messages(chat_id, role, content) VALUES (?, ?, ?)",
            [(chat_id, "user", message), (chat_id, "assistant", reply)],
        )