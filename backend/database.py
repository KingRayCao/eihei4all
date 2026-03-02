import sqlite3
from contextlib import contextmanager
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    # Import here to avoid circular import
    from auth import hash_password
    from config import SUPER_ADMIN_USERNAME, SUPER_ADMIN_PASSWORD

    with db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_approved INTEGER NOT NULL DEFAULT 0,
                is_admin INTEGER NOT NULL DEFAULT 0,
                is_super_admin INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                source TEXT,
                original_path TEXT,
                processed_path TEXT,
                is_placeholder INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Migration: add is_compressed column (safe to run on existing DB)
        try:
            conn.execute("ALTER TABLE images ADD COLUMN is_compressed INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass  # Column already exists

        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (SUPER_ADMIN_USERNAME,)
        ).fetchone()

        if not existing:
            conn.execute(
                """INSERT INTO users (username, password_hash, is_approved, is_admin, is_super_admin)
                   VALUES (?, ?, 1, 1, 1)""",
                (SUPER_ADMIN_USERNAME, hash_password(SUPER_ADMIN_PASSWORD))
            )
