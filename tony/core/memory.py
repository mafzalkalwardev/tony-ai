from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, db_path: Path | str = "tony/logs/tony_memory.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_command TEXT NOT NULL,
                    assistant_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_command TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    action_taken TEXT,
                    result TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_command TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    approved INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS project_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    note TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def log_conversation(self, user_command: str, assistant_response: str) -> None:
        self._insert("conversations", user_command=user_command, assistant_response=assistant_response)

    def log_task(self, user_command: str, intent: str, action_taken: str, result: str) -> None:
        self._insert("tasks", user_command=user_command, intent=intent, action_taken=action_taken, result=result)

    def log_approval(self, user_command: str, intent: str, approved: bool) -> None:
        self._insert("approvals", user_command=user_command, intent=intent, approved=int(approved))

    def log_project(self, project_path: str, note: str) -> None:
        self._insert("project_history", project_path=project_path, note=note)

    def _insert(self, table: str, **values: Any) -> None:
        columns = ", ".join(values.keys())
        placeholders = ", ".join("?" for _ in values)
        with self._connect() as conn:
            conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(values.values()))

