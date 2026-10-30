from __future__ import annotations

import csv
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Lead:
    chat_id: str
    name: str
    phone: str
    comment: str = ""
    created_at: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


class LeadStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                comment TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def add(self, lead: Lead) -> int:
        created_at = lead.created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
        cursor = self.connection.execute(
            "INSERT INTO leads (chat_id, name, phone, comment, created_at) VALUES (?, ?, ?, ?, ?)",
            (lead.chat_id, lead.name, lead.phone, lead.comment, created_at),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def count(self) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM leads").fetchone()[0])

    def export_csv(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = self.connection.execute(
            "SELECT chat_id, name, phone, comment, created_at FROM leads ORDER BY id"
        ).fetchall()
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["chat_id", "name", "phone", "comment", "created_at"])
            writer.writerows([tuple(row) for row in rows])

    def close(self) -> None:
        self.connection.close()
