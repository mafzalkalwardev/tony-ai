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
                    command_source TEXT DEFAULT 'text',
                    safety_level TEXT,
                    voice_transcript TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS voice_transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcript TEXT NOT NULL,
                    safety_level TEXT,
                    intent TEXT,
                    auto_ran INTEGER NOT NULL DEFAULT 0,
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
                CREATE TABLE IF NOT EXISTS workspaces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace_path TEXT NOT NULL,
                    project_type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS task_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    status TEXT NOT NULL,
                    output TEXT,
                    error TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS app_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    target TEXT,
                    result TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS voice_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcript TEXT,
                    source TEXT,
                    safety_decision TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS wake_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phrase TEXT,
                    confidence REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS screen_recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_path TEXT,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS action_recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_path TEXT,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS macro_replays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    macro_path TEXT,
                    result TEXT,
                    approved INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS live_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT,
                    note TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            self._ensure_column(conn, "tasks", "command_source", "TEXT DEFAULT 'text'")
            self._ensure_column(conn, "tasks", "safety_level", "TEXT")
            self._ensure_column(conn, "tasks", "voice_transcript", "TEXT")

    def log_conversation(self, user_command: str, assistant_response: str) -> None:
        self._insert("conversations", user_command=user_command, assistant_response=assistant_response)

    def log_task(
        self,
        user_command: str,
        intent: str,
        action_taken: str,
        result: str,
        command_source: str = "text",
        safety_level: str | None = None,
        voice_transcript: str | None = None,
    ) -> None:
        self._insert(
            "tasks",
            user_command=user_command,
            intent=intent,
            action_taken=action_taken,
            result=result,
            command_source=command_source,
            safety_level=safety_level,
            voice_transcript=voice_transcript,
        )

    def log_voice_transcript(self, transcript: str, safety_level: str, intent: str, auto_ran: bool) -> None:
        self._insert(
            "voice_transcripts",
            transcript=transcript,
            safety_level=safety_level,
            intent=intent,
            auto_ran=int(auto_ran),
        )

    def log_approval(self, user_command: str, intent: str, approved: bool) -> None:
        self._insert("approvals", user_command=user_command, intent=intent, approved=int(approved))

    def log_project(self, project_path: str, note: str) -> None:
        self._insert("project_history", project_path=project_path, note=note)

    def log_workspace(self, workspace_path: str, project_type: str = "") -> None:
        self._insert("workspaces", workspace_path=workspace_path, project_type=project_type)

    def log_task_output(self, command: str, status: str, output: str = "", error: str = "") -> None:
        self._insert("task_outputs", command=command, status=status, output=output, error=error)

    def log_app_action(self, action: str, target: str, result: str) -> None:
        self._insert("app_actions", action=action, target=target, result=result)

    def log_voice_event(self, transcript: str, source: str, safety_decision: str) -> None:
        self._insert("voice_events", transcript=transcript, source=source, safety_decision=safety_decision)

    def log_wake_event(self, phrase: str, confidence: float = 1.0) -> None:
        self._insert("wake_events", phrase=phrase, confidence=confidence)

    def log_screen_recording(self, recording_path: str, status: str) -> None:
        self._insert("screen_recordings", recording_path=recording_path, status=status)

    def log_action_recording(self, recording_path: str, status: str) -> None:
        self._insert("action_recordings", recording_path=recording_path, status=status)

    def log_macro_replay(self, macro_path: str, result: str, approved: bool) -> None:
        self._insert("macro_replays", macro_path=macro_path, result=result, approved=int(approved))

    def log_live_session(self, status: str, note: str = "") -> None:
        self._insert("live_sessions", status=status, note=note)

    def _insert(self, table: str, **values: Any) -> None:
        columns = ", ".join(values.keys())
        placeholders = ", ".join("?" for _ in values)
        with self._connect() as conn:
            conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(values.values()))

    def _ensure_column(self, conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
        columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
        if column not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
