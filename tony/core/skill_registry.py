from __future__ import annotations


class SkillRegistry:
    def __init__(self, agent=None) -> None:
        self.agent = agent
        self.intent_commands = {
            "open_vscode": "VS Code kholo",
            "open_terminal": "terminal kholo",
            "open_file_explorer": "file explorer kholo",
            "analyze_project": "project analyze karo",
            "run_project": "project run karo",
            "run_tests": "tests chalao",
            "git_status": "repo status dikhao",
            "git_diff": "git diff dikhao",
            "git_log": "git log dikhao",
            "git_commit": "git commit karo",
            "git_push": "git push karo",
            "github_status": "github status dikhao",
            "list_issues": "issues dikhao",
            "list_prs": "prs dikhao",
            "start_screen_recording": "screen record karo",
            "stop_screen_recording": "recording band karo",
            "start_action_recording": "meri actions record karo",
            "stop_action_recording": "recording band karo",
            "replay_macro": "last macro replay karo",
            "take_screenshot": "screenshot lo",
            "read_file": "read file",
            "create_file": "create file",
            "generate_client_message": "client message banao",
            "generate_delivery_note": "delivery note banao",
            "generate_daily_report": "daily report banao",
            "generate_codex_prompt": "codex ke liye prompt banao",
            "start_wake_mode": "wake mode on karo",
            "stop_wake_mode": "wake mode off karo",
            "push_to_talk": "push to talk",
            "stop_task": "stop task",
            "observe_screen": "screen dekho",
            "analyze_screen": "analyze screen",
            "describe_screen": "describe screen",
            "start_observe_mode": "observe mode start karo",
            "stop_observe_mode": "observe mode stop karo",
            "start_teach_mode": "watch me",
            "stop_teach_mode": "stop teach mode",
            "save_workflow": "workflow save karo",
            "discard_workflow": "discard workflow",
            "list_workflows": "workflows dikhao",
            "preview_workflow": "preview workflow",
            "replay_workflow": "workflow replay karo",
            "dry_run_workflow": "dry run workflow",
            "stop_replay": "stop replay",
            "summarize_workflow": "summarize workflow",
        }

    def is_ready(self, route: dict) -> bool:
        return bool(self.agent and route.get("intent") in self.intent_commands)

    def execute(self, route: dict, normalized_text: str, source: str = "text", raw_text: str = "", approved: bool = False) -> str:
        if not self.agent:
            return "That skill is not ready yet, Muhammad Afzal."
        command = self.intent_commands.get(route.get("intent"))
        if not command:
            return "That skill is not ready yet, Muhammad Afzal."
        if route.get("intent") == "read_file" and normalized_text:
            command = normalized_text
        if route.get("intent") == "create_file" and normalized_text:
            command = normalized_text
        return self.agent.handle(
            command,
            approved=approved,
            command_source=source,
            voice_transcript=raw_text if source in {"voice", "wake"} else None,
        )
