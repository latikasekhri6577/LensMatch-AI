import sqlite3
from datetime import datetime
from src.auth import DB_PATH  # reuse the same database file


def init_favorites_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            frame_name TEXT NOT NULL,
            frame_style TEXT,
            added_at TEXT NOT NULL,
            UNIQUE(username, frame_name),
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    conn.commit()
    conn.close()


def add_favorite(username, frame_name, frame_style=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO favorites (username, frame_name, frame_style, added_at) VALUES (?, ?, ?, ?)",
            (username, frame_name, frame_style, datetime.now().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # already favorited, do nothing
    finally:
        conn.close()


def remove_favorite(username, frame_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM favorites WHERE username = ? AND frame_name = ?",
        (username, frame_name)
    )
    conn.commit()
    conn.close()


def get_favorites(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT frame_name, frame_style, added_at FROM favorites WHERE username = ? ORDER BY added_at DESC",
        (username,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def is_favorited(username, frame_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM favorites WHERE username = ? AND frame_name = ?",
        (username, frame_name)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None