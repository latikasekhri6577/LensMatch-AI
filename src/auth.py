import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join("data", "users.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            face_shape TEXT NOT NULL,
            confidence REAL NOT NULL,
            face_width REAL,
            face_height REAL,
            aspect_ratio REAL,
            recommended_frames TEXT,
            scanned_at TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    conn.commit()
    conn.close()


def _hash_password(password):
    """Turns a plain password into a secure hash before storing it."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, email, password):
    """
    Adds a new user. Returns (True, "Success") or (False, "error message").
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    password_hash = _hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

    finally:
        conn.close()


def verify_user(username, password):
    """
    Checks login credentials. Returns True if valid, False otherwise.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    password_hash = _hash_password(password)

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    user = cursor.fetchone()
    conn.close()

    return user is not None


def save_scan(username, face_shape, confidence, measurements, recommended_frames):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        frames_str = ", ".join(recommended_frames)
        scanned_at = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO scans (username, face_shape, confidence, face_width, face_height, aspect_ratio, recommended_frames, scanned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, face_shape, confidence,
            measurements.get("face_width"), measurements.get("face_height"), measurements.get("aspect_ratio"),
            frames_str, scanned_at
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: failed to save scan history: {e}")  # logged, doesn't crash the app


def get_scan_history(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT face_shape, confidence, face_width, face_height, aspect_ratio, recommended_frames, scanned_at
        FROM scans
        WHERE username = ?
        ORDER BY scanned_at DESC
    """, (username,))

    rows = cursor.fetchall()
    conn.close()
    return rows