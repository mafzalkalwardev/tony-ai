from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ContextManager:
    memory: Any | None = None
    current_workspace: Path | None = None
    last_command: str = ""
    last_transcript: str = ""
    last_intent: str = ""
    last_result: str = ""
    last_error: str = ""
    pending_approval: dict | None = None
    current_mode: str = "idle"
    extras: dict = field(default_factory=dict)

    def set_mode(self, mode: str) -> None:
        self.current_mode = mode
        self._log_context("mode", mode)

    def save_input(self, raw_text: str, source: str) -> None:
        self.last_command = raw_text
        if source in {"voice", "wake"}:
            self.last_transcript = raw_text
        self._log_context("input", f"{source}: {raw_text}")

    def save_result(self, intent: str, result: str) -> None:
        self.last_intent = intent
        self.last_result = result
        self.last_error = ""
        self._log_context("result", result)

    def save_error(self, intent: str, error: str) -> None:
        self.last_intent = intent
        self.last_error = error
        self._log_context("error", error)

    def set_pending_approval(self, pending: dict) -> None:
        self.pending_approval = pending
        self.set_mode("waiting_for_approval")

    def clear_pending_approval(self) -> dict | None:
        pending = self.pending_approval
        self.pending_approval = None
        self.set_mode("idle")
        return pending

    def _log_context(self, status: str, output: str) -> None:
        if not self.memory:
            return
        try:
            self.memory.log_task_output("assistant_context", status, output=str(output))
        except Exception:
            pass
