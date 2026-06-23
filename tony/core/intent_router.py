from __future__ import annotations

from tony.core.command_normalizer import CommandNormalizer


class IntentRouter:
    def __init__(self, normalizer: CommandNormalizer | None = None, workspace=None) -> None:
        self.normalizer = normalizer or CommandNormalizer()
        self.workspace = workspace

    def route(self, command: str) -> dict:
        text = self.normalizer.normalize(command)
        if not text:
            return self._route("unknown", "unknown", "unknown", text, confidence=0.0)

        clarification = self._clarification(text)
        if clarification:
            return {
                "intent": "unknown",
                "skill": "unknown",
                "action": "clarify",
                "parameters": {},
                "confidence": 0.4,
                "needs_clarification": True,
                "clarifying_question": clarification,
                "normalized_text": text,
            }

        rules = (
            ("observe screen", "observe_screen", "vision", "observe screen"),
            ("analyze screen", "analyze_screen", "vision", "analyze screen"),
            ("describe screen", "describe_screen", "vision", "describe screen"),
            ("start observe mode", "start_observe_mode", "vision", "start observe mode"),
            ("stop observe mode", "stop_observe_mode", "vision", "stop observe mode"),
            ("start teach mode", "start_teach_mode", "workflow", "start teach mode"),
            ("stop teach mode", "stop_teach_mode", "workflow", "stop teach mode"),
            ("save workflow", "save_workflow", "workflow", "save workflow"),
            ("discard workflow", "discard_workflow", "workflow", "discard workflow"),
            ("list workflows", "list_workflows", "workflow", "list workflows"),
            ("preview workflow", "preview_workflow", "workflow", "preview workflow"),
            ("replay workflow", "replay_workflow", "workflow", "replay workflow"),
            ("dry run workflow", "dry_run_workflow", "workflow", "dry run workflow"),
            ("stop replay", "stop_replay", "workflow", "stop replay"),
            ("summarize workflow", "summarize_workflow", "workflow", "summarize workflow"),
            ("repo status", "git_status", "git", "git status"),
            ("git diff", "git_diff", "git", "git diff"),
            ("git log", "git_log", "git", "git log"),
            ("git commit", "git_commit", "git", "git commit"),
            ("git push", "git_push", "git", "git push"),
            ("github status", "github_status", "github", "github status"),
            ("list issues", "list_issues", "github", "list issues"),
            ("list prs", "list_prs", "github", "list prs"),
            ("open vscode", "open_vscode", "workspace", "open vscode"),
            ("open terminal", "open_terminal", "system", "open terminal"),
            ("open file explorer", "open_file_explorer", "system", "open file explorer"),
            ("analyze project", "analyze_project", "project", "analyze project"),
            ("run project", "run_project", "project", "run project"),
            ("run tests", "run_tests", "project", "run tests"),
            ("start screen recording", "start_screen_recording", "recorder", "start screen recording"),
            ("stop recording", "stop_screen_recording", "recorder", "stop recording"),
            ("start action recording", "start_action_recording", "recorder", "start action recording"),
            ("replay macro", "replay_macro", "recorder", "replay macro"),
            ("take screenshot", "take_screenshot", "recorder", "take screenshot"),
            ("read .env", "read_file", "file", "read .env"),
            ("read file", "read_file", "file", "read file"),
            ("create file", "create_file", "file", "create file"),
            ("client message", "generate_client_message", "business", "generate client message"),
            ("delivery note", "generate_delivery_note", "business", "generate delivery note"),
            ("daily report", "generate_daily_report", "business", "generate daily report"),
            ("codex prompt", "generate_codex_prompt", "prompt", "generate codex prompt"),
            ("start wake mode", "start_wake_mode", "voice", "start wake mode"),
            ("stop wake mode", "stop_wake_mode", "voice", "stop wake mode"),
            ("push to talk", "push_to_talk", "voice", "push to talk"),
            ("stop task", "stop_task", "system", "stop task"),
        )
        for phrase, intent, skill, action in rules:
            if phrase in text:
                return self._route(intent, skill, action, text)

        return self._route("unknown", "unknown", "unknown", text, confidence=0.15)

    def _clarification(self, text: str) -> str:
        if text in {"open website", "website open", "open site"}:
            return "Which website should I open?"
        if text in {"run it", "start it", "chalao"}:
            if not self._workspace_exists():
                return "Which project folder should I run?"
            return "What should I run in this workspace?"
        if text in {"message create", "message banao", "message"}:
            return "What should the message be about?"
        if text in {"watch this"}:
            return "What should I name this workflow?"
        return ""

    def _workspace_exists(self) -> bool:
        if self.workspace is None:
            return False
        try:
            return self.workspace.get_workspace().exists()
        except Exception:
            return False

    def _route(self, intent: str, skill: str, action: str, normalized_text: str, confidence: float = 0.95) -> dict:
        return {
            "intent": intent,
            "skill": skill,
            "action": action,
            "parameters": {},
            "confidence": confidence,
            "needs_clarification": False,
            "clarifying_question": "",
            "normalized_text": normalized_text,
        }
