import sqlite3
from contextlib import closing
from datetime import datetime, timezone


class Storage:
    """История отправок. Для каждой операции открывается своё соединение,
    поэтому класс безопасно работает из потоков планировщика."""

    def __init__(self, path):
        self.path = path
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS sends (
                    day TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    random_id INTEGER,
                    vk_message_id INTEGER,
                    error TEXT,
                    updated_at TEXT NOT NULL
                )"""
            )
            conn.commit()

    def is_sent(self, day: str) -> bool:
        with closing(sqlite3.connect(self.path)) as conn:
            row = conn.execute(
                "SELECT status FROM sends WHERE day = ?", (day,)
            ).fetchone()
        return bool(row and row[0] == "sent")

    def record(self, day: str, status: str, random_id: int,
               vk_message_id: int | None = None, error: str | None = None):
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                """INSERT INTO sends (day, status, random_id, vk_message_id, error, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(day) DO UPDATE SET
                     status = excluded.status,
                     vk_message_id = excluded.vk_message_id,
                     error = excluded.error,
                     updated_at = excluded.updated_at""",
                (day, status, random_id, vk_message_id, error,
                 datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
