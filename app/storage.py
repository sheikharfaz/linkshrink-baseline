import sqlite3
from contextlib import contextmanager

DB_PATH = "linkshrink.db"


@contextmanager
def get_conn(db_path=None):
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path=None):
    with get_conn(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS links (
                code TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def insert_link(code, url, created_at, db_path=None):
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT INTO links (code, url, created_at) VALUES (?, ?, ?)",
            (code, url, created_at),
        )
        conn.commit()


def get_link(code, db_path=None):
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
        return dict(row) if row else None
