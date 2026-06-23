from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class WorkflowMemory:
    BLOCKED_MARKERS = ("password", "otp", "2fa", "api key", "secret", "token", "payment", "card", "bank")

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
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    workspace TEXT,
                    safety_level TEXT,
                    steps_count INTEGER DEFAULT 0,
                    last_run_at TEXT
                );
                CREATE TABLE IF NOT EXISTS workflow_steps (
                    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER NOT NULL,
                    step_number INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    action_data TEXT,
                    window_title TEXT,
                    screenshot_path TEXT,
                    timestamp TEXT,
                    notes TEXT,
                    requires_approval INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER NOT NULL,
                    run_at TEXT NOT NULL,
                    status TEXT,
                    notes TEXT
                );
                CREATE TABLE IF NOT EXISTS screen_observations (
                    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    active_window_title TEXT,
                    process_name TEXT,
                    screenshot_path TEXT,
                    timestamp TEXT,
                    workspace_path TEXT,
                    visible_text TEXT,
                    safety_flags TEXT,
                    notes TEXT
                );
                """
            )

    def create_workflow(self, name: str, description: str = "", workspace: str = "", safety_level: str = "SAFE") -> int:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO workflows (name, description, created_at, updated_at, workspace, safety_level, steps_count) VALUES (?, ?, ?, ?, ?, ?, 0)",
                (name, description, now, now, workspace, safety_level),
            )
            return int(cursor.lastrowid)

    def add_step(
        self,
        workflow_id: int,
        step_number: int,
        action_type: str,
        action_data: dict | str = "",
        window_title: str = "",
        screenshot_path: str = "",
        notes: str = "",
        requires_approval: bool = False,
    ) -> None:
        blob = json.dumps(action_data) if isinstance(action_data, dict) else str(action_data)
        if self._contains_blocked(blob + " " + notes + " " + window_title):
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO workflow_steps
                (workflow_id, step_number, action_type, action_data, window_title, screenshot_path, timestamp, notes, requires_approval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (workflow_id, step_number, action_type, blob, window_title, screenshot_path, datetime.now().isoformat(), notes, int(requires_approval)),
            )
            conn.execute("UPDATE workflows SET steps_count = steps_count + 1, updated_at = ? WHERE workflow_id = ?", (datetime.now().isoformat(), workflow_id))

    def list_workflows(self) -> list[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM workflows ORDER BY updated_at DESC").fetchall()
        return [dict(row) for row in rows]

    def get_workflow(self, workflow_id: int) -> dict | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM workflows WHERE workflow_id = ?", (workflow_id,)).fetchone()
            if not row:
                return None
            steps = conn.execute("SELECT * FROM workflow_steps WHERE workflow_id = ? ORDER BY step_number", (workflow_id,)).fetchall()
        data = dict(row)
        data["steps"] = [dict(step) for step in steps]
        return data

    def log_run(self, workflow_id: int, status: str, notes: str = "") -> None:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute("INSERT INTO workflow_runs (workflow_id, run_at, status, notes) VALUES (?, ?, ?, ?)", (workflow_id, now, status, notes))
            conn.execute("UPDATE workflows SET last_run_at = ? WHERE workflow_id = ?", (now, workflow_id))

    def save_screen_observation(self, observation: dict[str, Any]) -> None:
        visible_text = str(observation.get("visible_text", ""))
        if self._contains_blocked(visible_text):
            visible_text = ""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO screen_observations
                (active_window_title, process_name, screenshot_path, timestamp, workspace_path, visible_text, safety_flags, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation.get("active_window_title", ""),
                    observation.get("process_name", ""),
                    observation.get("screenshot_path", ""),
                    observation.get("timestamp", datetime.now().isoformat()),
                    observation.get("workspace_path", ""),
                    visible_text,
                    json.dumps(observation.get("safety_flags", [])),
                    observation.get("notes", ""),
                ),
            )

    def _contains_blocked(self, text: str) -> bool:
        lowered = text.lower()
        return any(marker in lowered for marker in self.BLOCKED_MARKERS)
