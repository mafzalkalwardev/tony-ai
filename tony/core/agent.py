from __future__ import annotations

import os
import json
from pathlib import Path

from tony.core.command_parser import CommandParser
from tony.core.business_memory import BusinessMemory
from tony.core.memory import MemoryStore
from tony.core.ollama_client import OllamaClient
from tony.core.planner import Planner
from tony.core.project_profile import ProjectProfile
from tony.core.project_detector import ProjectDetector
from tony.core.observation_manager import ObservationManager
from tony.core.safety import SafetyLevel, SafetySystem
from tony.core.workflow_memory import WorkflowMemory
from tony.core.workspace import WorkspaceManager
from tony.core.live_state import LiveState, LiveStatus
from tony.core.workflow_engine import WorkflowEngine
from tony.tools.app_tool import AppTool
from tony.tools.action_recorder import ActionRecorder
from tony.tools.business_tool import BusinessTool
from tony.tools.browser_tool import BrowserTool
from tony.tools.code_analyzer import CodeAnalyzer
from tony.tools.file_tool import FileTool
from tony.tools.git_tool import GitTool
from tony.tools.github_tool import GitHubTool
from tony.tools.github_operator import GitHubOperator
from tony.tools.macro_player import MacroPlayer
from tony.tools.prompt_generator import PromptGenerator
from tony.tools.project_tool import ProjectTool
from tony.tools.repo_analyzer import RepoAnalyzer
from tony.tools.report_generator import ReportGenerator
from tony.tools.screen_recorder import ScreenRecorder
from tony.tools.screenshot_tool import ScreenshotTool
from tony.tools.shell_tool import ShellTool
from tony.tools.task_planner import TaskPlanner
from tony.tools.vscode_tool import VSCodeTool
from tony.tools.vision_tool import VisionTool
from tony.tools.window_tool import WindowTool
from tony.tools.workflow_player import WorkflowPlayer
from tony.tools.workflow_teacher import WorkflowTeacher
from tony.voice.live_listener import LiveVoiceListener
from tony.voice.stt import SpeechToText
from tony.voice.tts import TextToSpeech
from tony.voice.wake_engine import WakeEngine


class TonyAgent:
    def __init__(self, project_dir: Path | str | None = None) -> None:
        self.project_dir = Path(project_dir or os.getcwd()).resolve()
        self.settings = self._load_settings()
        self.parser = CommandParser()
        self.safety = SafetySystem()
        self.memory = MemoryStore()
        self.business_memory = BusinessMemory()
        self.workspace = WorkspaceManager(self.project_dir, self.memory)
        self.planner = Planner()
        self.ollama = OllamaClient()
        self.shell = ShellTool(self.safety)
        self.git = GitTool(self.shell)
        self.github = GitHubTool(self.shell)
        self.github_operator = GitHubOperator(self.shell)
        self.vscode = VSCodeTool(self.shell)
        self.files = FileTool()
        self.app_tool = AppTool()
        self.browser = BrowserTool()
        self.detector = ProjectDetector()
        self.repo_analyzer = RepoAnalyzer(self.detector, self.git)
        self.code_analyzer = CodeAnalyzer()
        self.business_tool = BusinessTool()
        self.report_generator = ReportGenerator()
        self.prompt_generator = PromptGenerator()
        self.project_profile = ProjectProfile()
        self.task_planner = TaskPlanner(self.business_memory)
        self.project_tool = ProjectTool(
            self.detector,
            self.shell,
            self.git,
            timeout_seconds=int(self.settings.get("project_command_timeout_seconds", 120)),
        )
        self.screenshot_tool = ScreenshotTool()
        self.screen_recorder = ScreenRecorder(fps=int(self.settings.get("screen_recording_fps", 1)))
        self.action_recorder = ActionRecorder()
        self.macro_player = MacroPlayer()
        self.workflow_memory = WorkflowMemory()
        self.window_tool = WindowTool()
        self.vision_tool = VisionTool(
            local_vision_provider=self.settings.get("local_vision_provider", "none"),
            ocr_enabled=bool(self.settings.get("ocr_enabled", False)),
        )
        self.observation_manager = ObservationManager(
            self.vision_tool,
            self.workflow_memory,
            workspace_path=str(self.workspace.get_workspace()),
        )
        self.workflow_teacher = WorkflowTeacher(
            self.workflow_memory,
            self.window_tool,
            workspace=str(self.workspace.get_workspace()),
        )
        self.workflow_player = WorkflowPlayer(
            self.workflow_memory,
            self.window_tool,
            speed=self.settings.get("workflow_replay_speed", "normal"),
        )
        self.live_state = LiveState(
            live_voice_enabled=bool(self.settings.get("live_voice_enabled", False)),
            wake_mode_enabled=bool(self.settings.get("wake_mode_enabled", False)),
        )
        self.wake_engine = WakeEngine(
            sensitivity=float(self.settings.get("wake_sensitivity", 0.55)),
            allow_short_tony_trigger=bool(self.settings.get("short_tony_trigger_enabled", False)),
            use_openwakeword_model=bool(self.settings.get("use_openwakeword_model", False)),
        )
        self.live_listener = LiveVoiceListener(self, self.wake_engine)
        self.workflow_engine = WorkflowEngine(
            self.repo_analyzer,
            self.business_tool,
            self.report_generator,
            self.task_planner,
            self.github_operator,
        )
        self.voice_enabled = bool(self.settings.get("voice_enabled", False))
        self.tts_enabled = bool(self.settings.get("tts_enabled", self.voice_enabled))
        self.stt = SpeechToText(
            model_name=self.settings.get("stt_model_size", self.settings.get("whisper_model", "small")),
            sample_rate=int(self.settings.get("voice_sample_rate", 16000)),
            record_seconds=int(self.settings.get("command_max_seconds", self.settings.get("record_seconds", self.settings.get("voice_record_seconds", 5)))),
            compute_type=self.settings.get("stt_compute_type", "int8"),
        )
        self.tts = TextToSpeech(enabled=self.tts_enabled)

    def _load_settings(self) -> dict:
        settings_path = Path(__file__).resolve().parent.parent.parent / "config" / "settings.json"
        if settings_path.exists():
            return json.loads(settings_path.read_text(encoding="utf-8"))
        return {}

    def speak_startup(self) -> str:
        return self.tts.speak("Welcome back, Muhammad Afzal. Tony is online.")

    def transcribe_voice_command(self, level_callback=None, status_callback=None):
        if not self.voice_enabled:
            from tony.voice.stt import TranscriptionResult

            return TranscriptionResult("", "Voice input is disabled in config/settings.json.")
        return self.stt.transcribe_from_microphone(
            level_callback=level_callback,
            status_callback=status_callback,
            record_seconds=float(self.settings.get("command_max_seconds", self.settings.get("record_seconds", 5))),
            output_path=self.stt.last_audio_path,
        )

    def transcribe_wake_phrase_chunk(self, level_callback=None, status_callback=None):
        if not self.voice_enabled:
            from tony.voice.stt import TranscriptionResult

            return TranscriptionResult("", "Voice input is disabled in config/settings.json.")
        return self.stt.transcribe_from_microphone(
            level_callback=level_callback,
            status_callback=status_callback,
            record_seconds=float(self.settings.get("wake_chunk_seconds", 2.5)),
            output_path=self.stt.last_wake_audio_path,
        )

    def set_voice_enabled(self, enabled: bool) -> None:
        self.voice_enabled = enabled

    def set_tts_enabled(self, enabled: bool) -> None:
        self.tts_enabled = enabled
        self.tts.enabled = enabled

    def speak(self, text: str) -> str:
        return self.tts.speak(text)

    def start_live_voice(self) -> str:
        self.live_state.live_voice_enabled = True
        self.live_state.set_status(LiveStatus.WAKE_LISTENING)
        result = self.live_listener.start_live_mode()
        self.memory.log_live_session("wake_listening", result)
        return result

    def stop_live_voice(self) -> str:
        self.live_state.live_voice_enabled = False
        self.live_state.set_status(LiveStatus.IDLE)
        result = self.live_listener.stop_live_mode()
        self.memory.log_live_session("idle", result)
        return result

    def enable_wake_mode(self) -> str:
        self.live_state.wake_mode_enabled = True
        result = self.wake_engine.start()
        self.memory.log_live_session("wake_listening", result)
        return result

    def disable_wake_mode(self) -> str:
        self.live_state.wake_mode_enabled = False
        result = self.wake_engine.stop()
        self.memory.log_live_session("idle", result)
        return result

    def set_workspace(self, path: Path | str) -> str:
        new_path = self.workspace.set_workspace(path)
        self.project_dir = new_path
        detection = self.detector.detect(new_path)
        self.memory.log_workspace(str(new_path), detection.project_type)
        return f"Workspace set to: {new_path}\nDetected project type: {detection.project_type}"

    def preview(self, command: str) -> tuple[str, str, str]:
        parsed = self.parser.parse(command)
        plan = self.planner.describe_action(parsed)
        decision = self.safety.classify(command, parsed.intent)
        return parsed.intent, plan, decision.level.value

    def handle(
        self,
        command: str,
        approved: bool = False,
        command_source: str = "text",
        voice_transcript: str | None = None,
    ) -> str:
        if command == "__speak_startup__":
            return self.speak_startup()

        parsed = self.parser.parse(command)
        decision = self.safety.classify(command, parsed.intent)
        plan = self.planner.describe_action(parsed)

        if decision.level == SafetyLevel.BLOCKED:
            result = f"Blocked: {decision.reason}"
            self.live_state.set_status(LiveStatus.BLOCKED)
            self.memory.log_task_output(command, "blocked", error=result)
            self.memory.log_task(
                command,
                parsed.intent,
                plan,
                result,
                command_source=command_source,
                safety_level=decision.level.value,
                voice_transcript=voice_transcript,
            )
            return result

        if decision.level == SafetyLevel.NEEDS_APPROVAL and not approved:
            result = f"{plan}\nApprove this action? yes/no"
            self.live_state.set_status(LiveStatus.WAITING_FOR_APPROVAL)
            self.memory.log_approval(command, parsed.intent, False)
            self.memory.log_task_output(command, "waiting_for_approval", output=result)
            return result

        if decision.level == SafetyLevel.NEEDS_APPROVAL and approved:
            self.memory.log_approval(command, parsed.intent, True)

        self.live_state.set_status(LiveStatus.RUNNING)
        result = self._execute(parsed, command)
        self.live_state.set_status(LiveStatus.COMPLETED)
        self.memory.log_task_output(command, "completed", output=result)
        self.memory.log_task(
            command,
            parsed.intent,
            plan,
            result,
            command_source=command_source,
            safety_level=decision.level.value,
            voice_transcript=voice_transcript,
        )
        self.memory.log_conversation(command, result)
        return result

    def _execute(self, parsed, command: str) -> str:
        if parsed.intent == "open_vscode":
            result = self.app_tool.open_vscode(self.workspace.get_workspace())
            self.memory.log_app_action("open_vscode", str(self.workspace.get_workspace()), result)
            return result
        if parsed.intent == "open_app":
            result = self.app_tool.open_app(parsed.argument, self.workspace.get_workspace())
            self.memory.log_app_action("open_app", parsed.argument, result)
            return result
        if parsed.intent == "open_terminal":
            result = self.app_tool.open_terminal(self.workspace.get_workspace())
            self.memory.log_app_action("open_terminal", str(self.workspace.get_workspace()), result)
            return result
        if parsed.intent == "open_file_explorer":
            result = self.app_tool.open_file_explorer(self.workspace.get_workspace())
            self.memory.log_app_action("open_file_explorer", str(self.workspace.get_workspace()), result)
            return result
        if parsed.intent == "open_folder":
            os.startfile(self.workspace.get_workspace())
            return f"Opened folder: {self.workspace.get_workspace()}"
        if parsed.intent == "set_workspace":
            return self.set_workspace(self.workspace.get_workspace())
        if parsed.intent == "git_status":
            return self.git.git_status(self.workspace.get_workspace()).as_text()
        if parsed.intent == "git_diff":
            return self.git.git_diff(self.workspace.get_workspace()).as_text()
        if parsed.intent == "git_commit":
            message = parsed.argument or "Tony update"
            return self.git.git_commit(self.workspace.get_workspace(), message).as_text()
        if parsed.intent == "git_push":
            return self.git.git_push(self.workspace.get_workspace()).as_text()
        if parsed.intent == "run_shell_command":
            shell_command = parsed.argument or command
            return self.shell.run(shell_command, self.workspace.get_workspace(), require_safe=False).as_text()
        if parsed.intent == "analyze_project":
            return self.project_tool.analyze_project(self.workspace.get_workspace())
        if parsed.intent == "run_project":
            return self.project_tool.run_project(self.workspace.get_workspace()).as_text()
        if parsed.intent == "run_tests":
            return self.project_tool.run_tests(self.workspace.get_workspace()).as_text()
        if parsed.intent == "install_dependencies":
            return self.project_tool.install_dependencies(self.workspace.get_workspace()).as_text()
        if parsed.intent == "open_localhost":
            port = int(parsed.argument or "3000")
            return self.browser.open_localhost(port)
        if parsed.intent == "take_screenshot":
            return self.screenshot_tool.take_screenshot()
        if parsed.intent in {"observe_screen", "analyze_screen", "describe_screen"}:
            return self.observation_manager.observe_once()
        if parsed.intent == "start_observe_mode":
            return self.observation_manager.start_observe_mode()
        if parsed.intent == "stop_observe_mode":
            return self.observation_manager.stop_observe_mode()
        if parsed.intent == "start_teach_mode":
            return self.workflow_teacher.start_teaching()
        if parsed.intent == "stop_teach_mode":
            return self.workflow_teacher.stop_teaching()
        if parsed.intent == "save_workflow":
            return self.workflow_teacher.save_workflow()
        if parsed.intent == "discard_workflow":
            return self.workflow_teacher.discard_workflow()
        if parsed.intent == "list_workflows":
            return self.workflow_player.list_workflows()
        if parsed.intent == "preview_workflow":
            return self.workflow_player.preview_workflow()
        if parsed.intent == "replay_workflow":
            return self.workflow_player.replay_workflow()
        if parsed.intent == "dry_run_workflow":
            return self.workflow_player.dry_run_workflow()
        if parsed.intent == "stop_replay":
            return self.workflow_player.stop_replay()
        if parsed.intent == "summarize_workflow":
            return self.workflow_teacher.summarize_workflow()
        if parsed.intent == "start_live_voice":
            return self.start_live_voice()
        if parsed.intent == "stop_live_voice":
            return self.stop_live_voice()
        if parsed.intent == "enable_wake_mode":
            return self.enable_wake_mode()
        if parsed.intent == "disable_wake_mode":
            return self.disable_wake_mode()
        if parsed.intent == "start_screen_recording":
            result = self.screen_recorder.start_recording()
            self.memory.log_screen_recording(str(self.screen_recorder.session_dir or ""), "running")
            return result
        if parsed.intent == "start_action_recording":
            result = self.action_recorder.start_recording(str(self.workspace.get_workspace()))
            self.memory.log_action_recording("", "running")
            return result
        if parsed.intent in {"stop_recording", "stop_screen_recording", "stop_action_recording"}:
            parts = [self.screen_recorder.stop_recording(), self.action_recorder.stop_recording()]
            if self.action_recorder.last_recording_path:
                self.memory.log_action_recording(str(self.action_recorder.last_recording_path), "completed")
            self.memory.log_screen_recording(str(self.screen_recorder.session_dir or ""), "completed")
            return "\n".join(parts)
        if parsed.intent == "replay_macro":
            path = self._last_macro_path()
            if not path:
                return "No recorded macro found yet."
            result = self.macro_player.replay(path)
            self.memory.log_macro_replay(str(path), result, True)
            return result
        if parsed.intent == "show_audio_settings":
            return self._audio_settings_summary()
        if parsed.intent == "open_recordings_folder":
            path = Path("tony/logs").resolve()
            os.startfile(path)
            return f"Opening recordings folder: {path}"
        if parsed.intent == "check_running_processes":
            return self._check_running_processes()
        if parsed.intent == "analyze_repo":
            return self.repo_analyzer.generate_repo_summary(self.workspace.get_workspace())
        if parsed.intent == "analyze_code":
            return self.code_analyzer.scan_code(self.workspace.get_workspace())
        if parsed.intent == "explain_error":
            return self.code_analyzer.explain_error_simple(command)
        if parsed.intent == "suggest_fix":
            return self.code_analyzer.suggest_fix(command)
        if parsed.intent == "generate_commit_message":
            status = self.git.git_status(self.workspace.get_workspace()).as_text()
            return self.github_operator.generate_commit_message(status)
        if parsed.intent == "github_status":
            auth = self.github_operator.auth_status(self.workspace.get_workspace()).as_text()
            repo = self.github_operator.repo_view(self.workspace.get_workspace()).as_text()
            return f"GitHub auth:\n{auth}\n\nRepo:\n{repo}"
        if parsed.intent == "list_issues":
            return self.github_operator.list_issues(self.workspace.get_workspace()).as_text()
        if parsed.intent == "list_prs":
            return self.github_operator.list_prs(self.workspace.get_workspace()).as_text()
        if parsed.intent == "create_issue":
            return self.github_operator.create_issue(self.workspace.get_workspace(), "Tony draft issue", "Created by Tony after approval.").as_text()
        if parsed.intent == "create_pr":
            return self.github_operator.create_pr(self.workspace.get_workspace(), "Tony draft PR", "Created by Tony after approval.").as_text()
        if parsed.intent == "generate_client_message":
            draft = self.business_tool.generate_client_message(command, self.settings.get("preferred_client_message_style", "professional, clear, friendly"))
            self.business_memory.save_client_draft(draft)
            return draft + "\n\nDraft only. Tony did not send anything."
        if parsed.intent == "generate_delivery_note":
            note = self.business_tool.generate_delivery_note(self.repo_analyzer.generate_repo_summary(self.workspace.get_workspace()))
            self.business_memory.save_client_draft(note)
            return note
        if parsed.intent == "generate_report":
            report = self.report_generator.generate_project_delivery_report(self.workspace.get_workspace())
            path = self.report_generator.save_report_markdown("project_report", report)
            self.business_memory.save_report("project_report", report)
            return f"{report}\n\nSaved locally: {path}"
        if parsed.intent == "create_daily_plan":
            return self.task_planner.create_daily_plan()
        if parsed.intent == "add_task":
            return self.task_planner.create_task(command.replace("task add", "").strip() or "New Tony task")
        if parsed.intent == "list_tasks":
            return self.task_planner.list_tasks()
        if parsed.intent == "complete_task":
            return self.task_planner.mark_task_done(int(parsed.argument or "1"))
        if parsed.intent == "generate_codex_prompt":
            prompt = self.prompt_generator.generate_codex_prompt(command, self.repo_analyzer.generate_repo_summary(self.workspace.get_workspace()))
            self.business_memory.save_prompt(prompt)
            return prompt
        if parsed.intent == "run_workflow":
            result = self.workflow_engine.run_workflow(command, self.workspace.get_workspace(), context=command)
            approval_note = ""
            if result.requires_approval_steps:
                approval_note = "\n\nApproval required before: " + ", ".join(result.requires_approval_steps)
            return f"# {result.name} Workflow\n\n{result.summary}{approval_note}"
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

    def _check_running_processes(self) -> str:
        try:
            import psutil
        except ImportError:
            return "psutil is not installed. Install requirements.txt to check running processes."

        names = []
        for proc in psutil.process_iter(["name"]):
            name = proc.info.get("name")
            if name and name not in names:
                names.append(name)
            if len(names) >= 20:
                break
        return "Running processes:\n" + "\n".join(f"- {name}" for name in names)

    def _last_macro_path(self) -> Path | None:
        recordings = sorted(Path("tony/logs/action_recordings").glob("actions_*.json"))
        return recordings[-1] if recordings else self.action_recorder.last_recording_path

    def _audio_settings_summary(self) -> str:
        return (
            f"Voice enabled: {self.voice_enabled}\n"
            f"Live voice enabled: {self.live_state.live_voice_enabled}\n"
            f"Wake mode enabled: {self.live_state.wake_mode_enabled}\n"
            f"Primary wake phrase: {self.settings.get('primary_wake_phrase', 'Wake Up, Tony!')}\n"
            f"Secondary wake phrase: {self.settings.get('secondary_wake_phrase', self.settings.get('wake_phrase'))}\n"
            f"STT model: {self.settings.get('stt_model_size', self.settings.get('whisper_model', 'small'))}\n"
            f"Wake sensitivity: {self.settings.get('wake_sensitivity', 0.55)}"
        )
