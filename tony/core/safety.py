from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SafetyLevel(str, Enum):
    SAFE = "SAFE"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class SafetyDecision:
    level: SafetyLevel
    reason: str


class SafetySystem:
    def __init__(self, permissions_path: Path | str = "config/permissions.json") -> None:
        self.permissions_path = Path(permissions_path)
        self.permissions = self._load_permissions()

    def _load_permissions(self) -> dict:
        if self.permissions_path.exists():
            return json.loads(self.permissions_path.read_text(encoding="utf-8"))
        return {"safe_commands": [], "blocked_patterns": [], "approval_patterns": []}

    def classify(self, command: str, action: str | None = None) -> SafetyDecision:
        text = f"{action or ''} {command}".lower().strip()

        for pattern in self.permissions.get("blocked_patterns", []):
            if pattern.lower() in text:
                return SafetyDecision(SafetyLevel.BLOCKED, f"Blocked pattern detected: {pattern}")

        destructive_patterns = ["remove-item -recurse", "rd /s", "erase /s", "format.com"]
        if any(pattern in text for pattern in destructive_patterns):
            return SafetyDecision(SafetyLevel.BLOCKED, "Destructive command pattern detected.")

        for pattern in self.permissions.get("approval_patterns", []):
            if pattern.lower() in text:
                return SafetyDecision(SafetyLevel.NEEDS_APPROVAL, f"Approval required for: {pattern}")

        if action in {"git_commit", "git_push", "create_file"}:
            return SafetyDecision(SafetyLevel.NEEDS_APPROVAL, f"Approval required for {action}.")

        safe_commands = [cmd.lower() for cmd in self.permissions.get("safe_commands", [])]
        if any(text == cmd or text.startswith(f"{cmd} ") for cmd in safe_commands):
            return SafetyDecision(SafetyLevel.SAFE, "Command is on the safe list.")

        if action in {"open_vscode", "open_folder", "git_status", "git_diff", "read_file", "summarize", "analyze_project"}:
            return SafetyDecision(SafetyLevel.SAFE, f"{action} is safe.")

        if action == "run_shell_command":
            return SafetyDecision(SafetyLevel.NEEDS_APPROVAL, "Unknown shell command requires approval.")

        return SafetyDecision(SafetyLevel.SAFE, "No risky pattern detected.")

    def is_approved_text(self, text: str) -> bool:
        cleaned = text.strip().lower().strip(".!? ")
        return cleaned in {"yes", "y", "approve", "approved", "haan", "han", "ji", "ok", "theek hai"}

    def is_rejected_text(self, text: str) -> bool:
        cleaned = text.strip().lower().strip(".!? ")
        return cleaned in {"no", "n", "nahin", "nahi", "cancel", "stop"}
