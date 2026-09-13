"""
Tiny SQLite wrapper for remembering the last price we saw for each
tracked product, so we can detect a *change* rather than just report
whatever the current price is on every run.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "prices.db"


def init_db(db_path: Path = DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prices (
                product_id   TEXT PRIMARY KEY,
                label        TEXT NOT NULL,
                last_price   REAL,
                last_checked TEXT
            )
            """
        )
        conn.commit()


@contextmanager
def _connect(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def get_last_price(product_id: str, db_path: Path = DB_PATH):
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT last_price FROM prices WHERE product_id = ?", (product_id,)
        ).fetchone()
        return row[0] if row else None


def upsert_price(product_id: str, label: str, price: float, checked_at: str, db_path: Path = DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO prices (product_id, label, last_price, last_checked)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                last_price = excluded.last_price,
                last_checked = excluded.last_checked
            """,
            (product_id, label, price, checked_at),
        )
        conn.commit()
