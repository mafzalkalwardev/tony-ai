from __future__ import annotations

import os
import json
from pathlib import Path

from tony.core.command_parser import CommandParser
from tony.core.memory import MemoryStore
from tony.core.ollama_client import OllamaClient
from tony.core.planner import Planner
from tony.core.safety import SafetyLevel, SafetySystem
from tony.tools.file_tool import FileTool
from tony.tools.git_tool import GitTool
from tony.tools.github_tool import GitHubTool
from tony.tools.shell_tool import ShellTool
from tony.tools.vscode_tool import VSCodeTool
from tony.voice.stt import SpeechToText
from tony.voice.tts import TextToSpeech


class TonyAgent:
    def __init__(self, project_dir: Path | str | None = None) -> None:
        self.project_dir = Path(project_dir or os.getcwd()).resolve()
        self.settings = self._load_settings()
        self.parser = CommandParser()
        self.safety = SafetySystem()
        self.memory = MemoryStore()
        self.planner = Planner()
        self.ollama = OllamaClient()
        self.shell = ShellTool(self.safety)
        self.git = GitTool(self.shell)
        self.github = GitHubTool(self.shell)
        self.vscode = VSCodeTool(self.shell)
        self.files = FileTool()
        self.voice_enabled = bool(self.settings.get("voice_enabled", False))
        self.stt = SpeechToText(
            model_name=self.settings.get("whisper_model", "small"),
            sample_rate=int(self.settings.get("voice_sample_rate", 16000)),
            record_seconds=int(self.settings.get("voice_record_seconds", 5)),
        )
        self.tts = TextToSpeech(enabled=self.voice_enabled)

    def _load_settings(self) -> dict:
        settings_path = Path("config/settings.json")
        if settings_path.exists():
            return json.loads(settings_path.read_text(encoding="utf-8"))
        return {}

    def speak_startup(self) -> str:
        return self.tts.speak("Welcome back, Muhammad Afzal. Tony is online.")

    def transcribe_voice_command(self):
        if not self.voice_enabled:
            from tony.voice.stt import TranscriptionResult

            return TranscriptionResult("", "Voice input is disabled in config/settings.json.")
        return self.stt.transcribe_from_microphone()

    def preview(self, command: str) -> tuple[str, str, str]:
        parsed = self.parser.parse(command)
        plan = self.planner.describe_action(parsed)
        decision = self.safety.classify(command, parsed.intent)
        return parsed.intent, plan, decision.level.value

    def handle(self, command: str, approved: bool = False) -> str:
        if command == "__speak_startup__":
            return self.speak_startup()

        parsed = self.parser.parse(command)
        decision = self.safety.classify(command, parsed.intent)
        plan = self.planner.describe_action(parsed)

        if decision.level == SafetyLevel.BLOCKED:
            result = f"Blocked: {decision.reason}"
            self.memory.log_task(command, parsed.intent, plan, result)
            return result

        if decision.level == SafetyLevel.NEEDS_APPROVAL and not approved:
            result = f"{plan}\nApprove this action? yes/no"
            self.memory.log_approval(command, parsed.intent, False)
            return result

        if decision.level == SafetyLevel.NEEDS_APPROVAL and approved:
            self.memory.log_approval(command, parsed.intent, True)

        result = self._execute(parsed, command)
        self.memory.log_task(command, parsed.intent, plan, result)
        self.memory.log_conversation(command, result)
        return result

    def _execute(self, parsed, command: str) -> str:
        if parsed.intent == "open_vscode":
            return self.vscode.open_folder(self.project_dir).as_text()
        if parsed.intent == "open_folder":
            os.startfile(self.project_dir)
            return f"Opened folder: {self.project_dir}"
        if parsed.intent == "git_status":
            return self.git.git_status(self.project_dir).as_text()
        if parsed.intent == "git_diff":
            return self.git.git_diff(self.project_dir).as_text()
        if parsed.intent == "git_commit":
            message = parsed.argument or "Tony update"
            return self.git.git_commit(self.project_dir, message).as_text()
        if parsed.intent == "git_push":
            return self.git.git_push(self.project_dir).as_text()
        if parsed.intent == "run_shell_command":
            shell_command = parsed.argument or command
            return self.shell.run(shell_command, self.project_dir, require_safe=False).as_text()
        if parsed.intent == "analyze_project":
            status = self.git.git_status(self.project_dir).as_text()
            log = self.git.git_log(self.project_dir).as_text()
            return f"Project check:\n\nGit status:\n{status}\n\nRecent commits:\n{log}"
        if parsed.intent == "summarize":
            return self.ollama.generate(f"Summarize this for Muhammad Afzal:\n\n{command}")
        if parsed.intent == "read_file":
            return "Tell Tony the exact file path to read. Tony will not read .env or secret files."
        if parsed.intent == "create_file":
            return "File creation is available after approval, but V1 needs an exact path and content."
        return self.ollama.generate(
            "You are Tony, a local Windows laptop assistant. Help classify or answer this command:\n\n"
            + command
        )
