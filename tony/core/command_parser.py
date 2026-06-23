from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedCommand:
    intent: str
    original_text: str
    argument: str = ""


class CommandParser:
    def parse(self, text: str) -> ParsedCommand:
        raw = text.strip()
        lowered = raw.lower()

        if not raw:
            return ParsedCommand("unknown", raw)

        if self._has_any(lowered, ["debugging workflow", "github delivery workflow", "client update workflow", "daily work workflow", "workflow start"]):
            return ParsedCommand("run_workflow", raw)

        if self._has_any(lowered, ["repo analyze", "analyze repo", "repository analyze"]):
            return ParsedCommand("analyze_repo", raw)

        if self._has_any(lowered, ["code analyze", "code errors find", "todos find", "todo find"]):
            return ParsedCommand("analyze_code", raw)

        if self._has_any(lowered, ["errors explain", "error explain", "simple words", "error kya hai"]):
            return ParsedCommand("explain_error", raw)

        if self._has_any(lowered, ["fix suggest", "suggest fix"]):
            return ParsedCommand("suggest_fix", raw)

        if self._has_any(lowered, ["commit message banao", "commit message"]):
            return ParsedCommand("generate_commit_message", raw)

        if self._has_any(lowered, ["github status", "github status dikhao"]):
            return ParsedCommand("github_status", raw)

        if self._has_any(lowered, ["issues dikhao", "list issues", "github issues"]):
            return ParsedCommand("list_issues", raw)

        if self._has_any(lowered, ["prs dikhao", "list prs", "pull requests", "pr list"]):
            return ParsedCommand("list_prs", raw)

        if self._has_any(lowered, ["issue create", "create issue"]):
            return ParsedCommand("create_issue", raw)

        if self._has_any(lowered, ["pr create", "create pr"]):
            return ParsedCommand("create_pr", raw)

        if self._has_any(lowered, ["client ko", "client message", "update message", "follow up message", "delay ka professional message"]):
            return ParsedCommand("generate_client_message", raw)

        if self._has_any(lowered, ["delivery note", "delivery report"]):
            return ParsedCommand("generate_delivery_note", raw)

        if self._has_any(lowered, ["daily report", "project report", "testing report", "repo report", "aaj ka kaam summarize"]):
            return ParsedCommand("generate_report", raw)

        if self._has_any(lowered, ["aaj ka plan", "daily plan"]):
            return ParsedCommand("create_daily_plan", raw)

        if self._has_any(lowered, ["task add", "add task"]):
            return ParsedCommand("add_task", raw)

        if self._has_any(lowered, ["tasks dikhao", "list tasks", "urgent tasks"]):
            return ParsedCommand("list_tasks", raw)

        if self._has_any(lowered, ["task done", "complete task"]):
            return ParsedCommand("complete_task", raw, self._extract_port(lowered))

        if self._has_any(lowered, ["codex ke liye prompt", "debug prompt", "cline prompt", "cursor prompt", "error ka prompt"]):
            return ParsedCommand("generate_codex_prompt", raw)

        if self._has_any(lowered, ["wake up tony", "wake up, tony"]):
            return ParsedCommand("start_live_voice", raw)

        if self._has_any(lowered, ["screen dekho", "meri screen dekho", "look at my screen", "look at screen", "observe screen"]):
            return ParsedCommand("observe_screen", raw)

        if self._has_any(lowered, ["analyze screen", "screen issue", "screen par issue", "kya issue hai screen"]):
            return ParsedCommand("analyze_screen", raw)

        if self._has_any(lowered, ["describe screen", "screen summary"]):
            return ParsedCommand("describe_screen", raw)

        if self._has_any(lowered, ["observe mode start", "observe mode on", "observe mode start karo"]):
            return ParsedCommand("start_observe_mode", raw)

        if self._has_any(lowered, ["observe mode stop", "observe band", "observe mode off"]):
            return ParsedCommand("stop_observe_mode", raw)

        if self._has_any(lowered, ["watch me", "learn this workflow", "record this process", "mujhe dekh ke seekho"]):
            return ParsedCommand("start_teach_mode", raw)

        if self._has_any(lowered, ["stop teach mode", "teach mode stop", "teaching stop"]):
            return ParsedCommand("stop_teach_mode", raw)

        if self._has_any(lowered, ["workflow save", "save workflow", "ye steps yaad rakho", "ye workflow yaad rakho"]):
            return ParsedCommand("save_workflow", raw)

        if self._has_any(lowered, ["discard workflow", "workflow discard"]):
            return ParsedCommand("discard_workflow", raw)

        if self._has_any(lowered, ["workflows dikhao", "list workflows", "workflow list"]):
            return ParsedCommand("list_workflows", raw)

        if self._has_any(lowered, ["preview workflow", "workflow preview"]):
            return ParsedCommand("preview_workflow", raw)

        if self._has_any(lowered, ["workflow replay", "replay workflow", "last workflow replay"]):
            return ParsedCommand("replay_workflow", raw)

        if self._has_any(lowered, ["dry run workflow", "dry run karo"]):
            return ParsedCommand("dry_run_workflow", raw)

        if self._has_any(lowered, ["stop replay", "replay band"]):
            return ParsedCommand("stop_replay", raw)

        if self._has_any(lowered, ["summarize workflow", "workflow summary"]):
            return ParsedCommand("summarize_workflow", raw)

        if self._has_any(lowered, ["wake mode on", "wake mode start", "wake mode enable", "wake mode on karo"]):
            return ParsedCommand("enable_wake_mode", raw)

        if self._has_any(lowered, ["wake mode off", "wake mode stop", "wake mode disable", "wake mode band"]):
            return ParsedCommand("disable_wake_mode", raw)

        if self._has_any(lowered, ["live listening start", "live voice start", "sunna start", "listening start"]):
            return ParsedCommand("start_live_voice", raw)

        if self._has_any(lowered, ["live listening stop", "live voice stop", "sunna band", "listening stop"]):
            return ParsedCommand("stop_live_voice", raw)

        if self._has_any(lowered, ["screen record", "screen recording start", "screen record karo"]):
            return ParsedCommand("start_screen_recording", raw)

        if self._has_any(lowered, ["actions record", "action recording start", "record my actions", "meri actions record", "process ka macro"]):
            return ParsedCommand("start_action_recording", raw)

        if self._has_any(lowered, ["recording band", "recording stop", "stop recording", "screen recording stop", "action recording stop"]):
            return ParsedCommand("stop_recording", raw)

        if self._has_any(lowered, ["last macro replay", "replay macro", "replay actions", "last recording replay"]):
            return ParsedCommand("replay_macro", raw)

        if self._has_any(lowered, ["waves dikhao", "audio settings", "mic check", "microphone check"]):
            return ParsedCommand("show_audio_settings", raw)

        if self._has_any(lowered, ["recordings folder", "open recordings"]):
            return ParsedCommand("open_recordings_folder", raw)

        if self._has_any(lowered, ["notepad", "calculator", "calc", "chrome", "browser"]) and self._has_any(lowered, ["khol", "kholo", "open"]):
            return ParsedCommand("open_app", raw, raw)

        if self._has_any(lowered, ["terminal", "powershell", "windows terminal"]) and self._has_any(lowered, ["khol", "kholo", "open"]):
            return ParsedCommand("open_terminal", raw)

        if self._has_any(lowered, ["file explorer", "explorer"]) and self._has_any(lowered, ["khol", "kholo", "open"]):
            return ParsedCommand("open_file_explorer", raw)

        if self._has_any(lowered, ["workspace banao", "workspace set", "current folder set", "folder workspace", "set workspace"]):
            return ParsedCommand("set_workspace", raw)

        if self._has_any(lowered, ["dependencies install", "install dependencies", "npm install", "pip install"]):
            return ParsedCommand("install_dependencies", raw)

        if self._has_any(lowered, ["tests chalao", "test chalao", "run tests", "project test", "tests run"]):
            return ParsedCommand("run_tests", raw)

        if self._has_any(lowered, ["project run", "run project", "project chalao", "project start", "project run karo"]):
            return ParsedCommand("run_project", raw)

        if "localhost" in lowered and self._has_any(lowered, ["khol", "kholo", "open", "check"]):
            return ParsedCommand("open_localhost", raw, self._extract_port(lowered))

        if self._has_any(lowered, ["screenshot", "screen shot"]) and self._has_any(lowered, ["lo", "take", "capture", "karo"]):
            return ParsedCommand("take_screenshot", raw)

        if self._has_any(lowered, ["processes", "running processes", "process list"]):
            return ParsedCommand("check_running_processes", raw)

        if self._has_any(lowered, ["push", "push karo"]):
            return ParsedCommand("git_push", raw)

        if "commit" in lowered:
            return ParsedCommand("git_commit", raw, self._after_keyword(raw, "commit"))

        if "git diff" in lowered or ("repo" in lowered and "diff" in lowered):
            return ParsedCommand("git_diff", raw)

        if "status" in lowered and self._has_any(lowered, ["git", "repo", "github"]):
            return ParsedCommand("git_status", raw)

        if self._has_any(lowered, ["vs code", "vscode", "visual studio code"]) and self._has_any(lowered, ["khol", "kholo", "open"]):
            return ParsedCommand("open_vscode", raw)

        if self._has_any(lowered, ["folder", "directory"]) and self._has_any(lowered, ["khol", "kholo", "open"]):
            return ParsedCommand("open_folder", raw)

        if self._has_any(lowered, ["error check", "masla", "issue", "analyze", "analyse", "project analyze", "analyze project"]):
            return ParsedCommand("analyze_project", raw)

        if self._has_any(lowered, ["file banao", "create file", "nayi file", "new file"]):
            return ParsedCommand("create_file", raw)

        if self._has_any(lowered, ["read", "parho", "parhna", "file parho"]):
            return ParsedCommand("read_file", raw)

        if self._has_any(lowered, ["summarize", "summary", "khulasa"]):
            return ParsedCommand("summarize", raw)

        if self._has_any(lowered, ["run", "chalao", "start karo"]):
            return ParsedCommand("run_shell_command", raw, self._strip_tony_prefix(raw))

        return ParsedCommand("unknown", raw)

    def _has_any(self, text: str, terms: list[str]) -> bool:
        return any(term in text for term in terms)

    def _after_keyword(self, text: str, keyword: str) -> str:
        index = text.lower().find(keyword)
        if index == -1:
            return ""
        return text[index + len(keyword):].strip(" :\"'")

    def _strip_tony_prefix(self, text: str) -> str:
        cleaned = text.strip()
        for prefix in ["Tony,", "tony,", "Tony", "tony"]:
            if cleaned.startswith(prefix):
                return cleaned[len(prefix):].strip()
        return cleaned

    def _extract_port(self, text: str) -> str:
        for word in text.replace(":", " ").split():
            if word.isdigit():
                return word
        return "3000"
