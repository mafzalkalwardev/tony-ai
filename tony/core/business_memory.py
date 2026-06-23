from __future__ import annotations

import sqlite3
from pathlib import Path


class BusinessMemory:
    BLOCKED = ["password", "api key", "secret", "token", "payment"]

    def __init__(self, db_path: Path | str = "tony/logs/business_memory.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS business_notes (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS client_drafts (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS project_reports (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS generated_prompts (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS daily_plans (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS task_items (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, priority TEXT, status TEXT DEFAULT 'open', timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
                """
            )

    def save_client_draft(self, content: str) -> None:
        self._safe_insert("client_drafts", content=content)

    def save_report(self, title: str, content: str) -> None:
        self._safe_insert("project_reports", title=title, content=content)

    def save_prompt(self, content: str) -> None:
        self._safe_insert("generated_prompts", content=content)

    def save_daily_plan(self, content: str) -> None:
        self._safe_insert("daily_plans", content=content)

    def add_task(self, title: str, description: str = "", priority: str = "medium") -> int:
        self._safe_insert("task_items", title=title, description=description, priority=priority, status="open")
        with self._connect() as conn:
            return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])

    def list_tasks(self, status: str | None = None) -> list[tuple]:
        query = "SELECT id, title, priority, status FROM task_items"
        params: tuple = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY id DESC"
        with self._connect() as conn:
            return list(conn.execute(query, params).fetchall())

    def mark_task_done(self, task_id: int) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE task_items SET status = 'done' WHERE id = ?", (task_id,))

    def _safe_insert(self, table: str, **values: str) -> None:
        blob = " ".join(str(v).lower() for v in values.values())
        if any(marker in blob for marker in self.BLOCKED):
            raise ValueError("Refusing to save sensitive business memory.")
        columns = ", ".join(values.keys())
        placeholders = ", ".join("?" for _ in values)
        with self._connect() as conn:
            conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(values.values()))

