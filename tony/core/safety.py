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


_PERMISSIONS_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "permissions.json"


class SafetySystem:
    def __init__(self, permissions_path: Path | str = _PERMISSIONS_PATH) -> None:
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

        destructive_patterns = ["remove-item -recurse", "rd /s", "erase /s", "format.com", "rm rf", "rm - r"]
        if any(pattern in text for pattern in destructive_patterns):
            return SafetyDecision(SafetyLevel.BLOCKED, "Destructive command pattern detected.")

        for pattern in self.permissions.get("approval_patterns", []):
            if pattern.lower() in text:
                return SafetyDecision(SafetyLevel.NEEDS_APPROVAL, f"Approval required for: {pattern}")

        if action in {"git_commit", "git_push", "create_file"}:
            return SafetyDecision(SafetyLevel.NEEDS_APPROVAL, f"Approval required for {action}.")

        if action in {
            "run_project",
            "run_tests",
            "install_dependencies",
            "take_screenshot",
            "observe_screen",
            "analyze_screen",
            "describe_screen",
            "start_observe_mode",
            "start_teach_mode",
            "save_workflow",
            "replay_workflow",
            "control_mouse",
            "control_keyboard",
            "focus_window",
            "open_external_url",
            "start_screen_recording",
            "start_action_recording",
            "replay_macro",
            "screen_control",
            "browser_automation",
            "create_issue",
            "create_pr",
            "prepare_commit",
            "push_branch",
            "apply_code_fix",
        }:
            return SafetyDecision(SafetyLevel.NEEDS_APPROVAL, f"Approval required for {action}.")

        safe_commands = [cmd.lower() for cmd in self.permissions.get("safe_commands", [])]
        if any(text == cmd or text.startswith(f"{cmd} ") for cmd in safe_commands):
            return SafetyDecision(SafetyLevel.SAFE, "Command is on the safe list.")

        if action in {
            "open_vscode",
            "open_folder",
            "open_app",
            "open_terminal",
            "open_file_explorer",
            "git_status",
            "git_diff",
            "read_file",
            "summarize",
            "analyze_project",
            "set_workspace",
            "open_localhost",
            "check_localhost",
            "detect_project_type",
            "check_running_processes",
            "start_live_voice",
            "stop_live_voice",
            "enable_wake_mode",
            "disable_wake_mode",
            "show_audio_settings",
            "open_recordings_folder",
            "stop_recording",
            "analyze_repo",
            "analyze_code",
            "explain_error",
            "suggest_fix",
            "generate_commit_message",
            "github_status",
            "list_issues",
            "list_prs",
            "generate_client_message",
            "generate_delivery_note",
            "generate_report",
            "create_daily_plan",
            "add_task",
            "list_tasks",
            "complete_task",
            "generate_codex_prompt",
            "run_workflow",
            "list_workflows",
            "preview_workflow",
            "dry_run_workflow",
            "stop_observe_mode",
            "stop_teach_mode",
            "stop_replay",
            "summarize_workflow",
            "discard_workflow",
        }:
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
