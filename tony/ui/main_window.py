from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtCore import QThreadPool
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from tony.core.assistant_brain import AssistantBrain
from tony.core.agent import TonyAgent
from tony.core.task_runner import AgentWorker, BrainWorker, VoiceWorker, WakeWorker
from tony.voice.debug_log import voice_debug
from tony.voice.audio_waveform import AudioWaveformWidget
from tony.voice.voice_setup import get_voice_setup_status


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tony AI")
        self.resize(1120, 760)
        icon_path = Path(__file__).resolve().parents[2] / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.agent = TonyAgent(Path.cwd())
        self.brain = AssistantBrain(self.agent)
        self.thread_pool = QThreadPool.globalInstance()
        self.current_worker = None
        self.wake_worker = None
        self.last_response = ""

        self.status = QLabel("Online")
        self.status.setObjectName("statusBadge")
        self.workspace_label = QLabel(self._workspace_text())
        self.status_title = QLabel("Tony is online")
        self.status_title.setObjectName("heroStatus")
        self.transcript_label = QLabel("You said: ...")
        self.transcript_label.setObjectName("transcript")
        self.reply_box = QTextEdit()
        self.reply_box.setReadOnly(True)
        self.reply_box.setObjectName("replyBox")
        self.reply_box.setText("Tony: Welcome back, Muhammad Afzal. Tony is online.")
        self.audio_wave = AudioWaveformWidget(max_bars=40)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a command, e.g. repo status dikhao")
        self.run_button = QPushButton("Run")
        self.voice_button = QPushButton("Push to Talk")
        self.wake_mode_button = QPushButton("Wake Mode")
        self.stop_button = QPushButton("Stop")
        self.settings_button = QPushButton("Settings")

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.task_output = QTextEdit()
        self.task_output.setReadOnly(True)
        self.voice_setup_output = QTextEdit()
        self.voice_setup_output.setReadOnly(True)
        self.advanced_tabs = QTabWidget()
        self.advanced_tabs.setVisible(False)

        self._build_layout()
        self._connect_signals()
        self._load_styles()
        self.speak_startup()

    def _build_layout(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)

        top = QHBoxLayout()
        title = QLabel("Tony AI")
        title.setObjectName("appTitle")
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.workspace_label)
        top.addWidget(self.status)

        center = QVBoxLayout()
        center.addWidget(self.audio_wave)
        center.addWidget(self.status_title)
        center.addWidget(self.transcript_label)
        center.addWidget(self.reply_box)

        command_row = QHBoxLayout()
        command_row.addWidget(self.input)
        command_row.addWidget(self.run_button)
        command_row.addWidget(self.voice_button)
        command_row.addWidget(self.wake_mode_button)
        command_row.addWidget(self.stop_button)
        command_row.addWidget(self.settings_button)

        self._build_advanced_tabs()

        layout.addLayout(top)
        layout.addLayout(center)
        layout.addLayout(command_row)
        layout.addWidget(self.advanced_tabs)
        self.setCentralWidget(root)

    def _build_advanced_tabs(self) -> None:
        self.advanced_tabs.addTab(self._workspace_tab(), "Workspace")
        self.advanced_tabs.addTab(self._github_tab(), "Git/GitHub")
        self.advanced_tabs.addTab(self._recorder_tab(), "Recorder")
        self.advanced_tabs.addTab(self._logs_tab(), "Logs")
        self.advanced_tabs.addTab(self._settings_tab(), "Settings")

    def _workspace_tab(self) -> QWidget:
        tab = QWidget()
        row = QHBoxLayout(tab)
        self._add_button(row, "Set Workspace", self.choose_folder)
        self._add_button(row, "Analyze Project", lambda: self.run_command("project analyze karo"))
        self._add_button(row, "Run Project", lambda: self.run_command("project run karo"))
        self._add_button(row, "Run Tests", lambda: self.run_command("tests chalao"))
        self._add_button(row, "Open Terminal", lambda: self.run_command("terminal kholo"))
        return tab

    def _github_tab(self) -> QWidget:
        tab = QWidget()
        row = QHBoxLayout(tab)
        self._add_button(row, "Git Status", lambda: self.run_command("repo status dikhao"))
        self._add_button(row, "GitHub Status", lambda: self.run_command("GitHub status dikhao"))
        self._add_button(row, "Issues", lambda: self.run_command("issues dikhao"))
        self._add_button(row, "PRs", lambda: self.run_command("PRs dikhao"))
        self._add_button(row, "Commit Message", lambda: self.run_command("commit message banao"))
        return tab

    def _recorder_tab(self) -> QWidget:
        tab = QWidget()
        row = QHBoxLayout(tab)
        self._add_button(row, "Screen Record", lambda: self.run_command("screen record karo"))
        self._add_button(row, "Action Record", lambda: self.run_command("meri actions record karo"))
        self._add_button(row, "Stop Recording", lambda: self.run_command("recording band karo"))
        self._add_button(row, "Replay Macro", lambda: self.run_command("last macro replay karo"))
        return tab

    def _logs_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Conversation"))
        layout.addWidget(self.chat_log)
        layout.addWidget(QLabel("Task Output"))
        layout.addWidget(self.task_output)
        return tab

    def _settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self._add_button(row, "Check Voice Setup", self.on_check_voice_setup)
        self._add_button(row, "Mic Test", self.on_mic_test)
        self._add_button(row, "Speak Last Reply", self.on_speak_last_response)
        self._add_button(row, "Voice On/Off", self.on_toggle_voice)
        self._add_button(row, "TTS On/Off", self.on_toggle_tts)
        self._add_button(row, "Open Recordings", lambda: self.run_command("open recordings folder"))
        layout.addLayout(row)
        vision_row = QHBoxLayout()
        self._add_button(vision_row, "Observe Screen Once", lambda: self.run_command("Tony screen dekho"))
        self._add_button(vision_row, "Start Observe Mode", lambda: self.run_command("Tony observe mode start karo"))
        self._add_button(vision_row, "Stop Observe Mode", lambda: self.run_command("Tony observe mode stop karo"))
        self._add_button(vision_row, "Open Screenshot Folder", self.on_open_screenshot_folder)
        layout.addWidget(QLabel("Vision / Observe"))
        layout.addLayout(vision_row)
        teach_row = QHBoxLayout()
        self._add_button(teach_row, "Start Teaching", lambda: self.run_command("Tony watch me"))
        self._add_button(teach_row, "Stop Teaching", lambda: self.run_command("Tony stop teach mode"))
        self._add_button(teach_row, "Save Workflow", lambda: self.run_command("Tony workflow save karo"))
        self._add_button(teach_row, "List Workflows", lambda: self.run_command("Tony workflows dikhao"))
        self._add_button(teach_row, "Preview Workflow", lambda: self.run_command("Tony preview workflow"))
        self._add_button(teach_row, "Replay Workflow", lambda: self.run_command("Tony last workflow replay karo"))
        layout.addWidget(QLabel("Teach Mode"))
        layout.addLayout(teach_row)
        layout.addWidget(QLabel(f"Whisper model: {self.agent.stt.model_name}"))
        layout.addWidget(QLabel("Mic device: Windows default input device"))
        layout.addWidget(self.voice_setup_output)
        return tab

    def _add_button(self, layout, text: str, callback) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def _connect_signals(self) -> None:
        self.run_button.clicked.connect(self.on_run)
        self.input.returnPressed.connect(self.on_run)
        self.voice_button.clicked.connect(self.on_voice_input)
        self.wake_mode_button.clicked.connect(self.on_toggle_wake_mode)
        self.stop_button.clicked.connect(self.on_stop_task)
        self.settings_button.clicked.connect(lambda: self.advanced_tabs.setVisible(not self.advanced_tabs.isVisible()))

    def _load_styles(self) -> None:
        style_path = Path(__file__).with_name("styles.qss")
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))

    def _workspace_text(self) -> str:
        path = str(self.agent.workspace.get_workspace())
        return f"Workspace: ...{path[-48:]}" if len(path) > 52 else f"Workspace: {path}"

    def set_status(self, text: str) -> None:
        self.status.setText(text)
        self.status_title.setText(f"Tony is {text.lower()}")
        self.audio_wave.set_state(text)

    def set_reply(self, text: str) -> None:
        self.last_response = text
        self.reply_box.setText(f"Tony: {text}")
        self.chat_log.append(f"<b>Tony:</b> {text.replace(chr(10), '<br>')}")

    def set_transcript(self, text: str) -> None:
        self.transcript_label.setText(f"You said: {text}")
        self.chat_log.append(f"<b>You:</b> {text}")

    def on_run(self) -> None:
        command = self.input.text().strip()
        if not command:
            return
        self.input.clear()
        self.run_command(command, command_source="text")

    def on_voice_input(self) -> None:
        if not self.agent.voice_enabled:
            self.set_reply("Voice input is off. Turn it on from Settings.")
            return
        self.set_status("Listening")
        self.set_reply("Yes, Muhammad Afzal. I'm listening.")
        self.voice_button.setEnabled(False)
        worker = VoiceWorker(self.agent)
        self.current_worker = worker
        worker.signals.started.connect(lambda: self.set_status("Listening"))
        worker.signals.level.connect(self.audio_wave.set_level)
        worker.signals.finished.connect(self.on_voice_transcribed)
        worker.signals.failed.connect(self.on_voice_failed)
        worker.signals.cancelled.connect(lambda: self.set_status("Cancelled"))
        self.thread_pool.start(worker)

    def on_mic_test(self) -> None:
        original_seconds = self.agent.stt.record_seconds
        self.agent.stt.record_seconds = 3
        self.set_reply("Mic test started. Speak for three seconds.")
        worker = VoiceWorker(self.agent)
        self.current_worker = worker
        worker.signals.started.connect(lambda: self.set_status("Listening"))
        worker.signals.level.connect(self.audio_wave.set_level)
        worker.signals.finished.connect(lambda text: self._finish_mic_test(text, original_seconds))
        worker.signals.failed.connect(lambda error: self._fail_mic_test(error, original_seconds))
        self.thread_pool.start(worker)

    def _finish_mic_test(self, text: str, original_seconds: int) -> None:
        self.agent.stt.record_seconds = original_seconds
        self.set_status("Online")
        self.set_transcript(text)
        self.set_reply(f"I heard: {text}. Last audio was saved to tony/logs/voice/last_command.wav.")

    def _fail_mic_test(self, error: str, original_seconds: int) -> None:
        self.agent.stt.record_seconds = original_seconds
        self.on_voice_failed(error)

    def on_voice_transcribed(self, text: str) -> None:
        self.voice_button.setEnabled(True)
        self.input.setText(text)
        self.process_voice_transcript(text, source="voice")

    def process_voice_transcript(self, transcript: str, source: str = "voice") -> None:
        text = (transcript or "").strip()
        voice_debug(f"transcript emitted to UI source={source} text={self._safe_voice_debug_text(text)}")
        self.set_status("Thinking")
        if not text:
            self.set_transcript("")
            self.set_reply("I could not hear a clear command. Please try again.")
            self.set_status("Online")
            return
        self.set_transcript(text)
        self.task_output.append(f"> {text}")
        worker = BrainWorker(self.brain, text, command_source=source)
        self.current_worker = worker
        worker.signals.started.connect(lambda: self.set_status("Working"))
        worker.signals.status.connect(self.set_status)
        worker.signals.finished.connect(self.on_brain_finished)
        worker.signals.failed.connect(self.on_failed)
        worker.signals.cancelled.connect(lambda: self.set_status("Cancelled"))
        voice_debug("AssistantBrain called")
        self.thread_pool.start(worker)

    def on_voice_failed(self, error: str) -> None:
        self.voice_button.setEnabled(True)
        self.set_status("Online")
        if "Voice transcription is not installed" in error or "Microphone recording is not installed" in error:
            self.set_reply(f"Voice is not ready yet, Muhammad Afzal. {error}. Text commands still work.")
        elif "recording is too quiet" in error:
            self.set_reply(error)
        elif "I could not hear" in error:
            self.set_reply(error)
        else:
            self.set_reply(f"Microphone problem: {error}")

    def on_toggle_wake_mode(self) -> None:
        if self.agent.live_state.wake_mode_enabled:
            self.on_stop_task()
            self.agent.disable_wake_mode()
            self.set_status("Online")
            self.set_reply("Wake Mode is off.")
            return

        self.set_status("Wake Listening")
        self.set_reply("Wake Mode is on. Say: Wake Up, Tony.")
        self.wake_worker = WakeWorker(self.agent)
        self.current_worker = self.wake_worker
        self.wake_worker.signals.started.connect(lambda: self.set_status("Wake Listening"))
        self.wake_worker.signals.level.connect(self.audio_wave.set_level)
        self.wake_worker.signals.status.connect(self.set_status)
        self.wake_worker.signals.wake_transcript_ready.connect(lambda text: voice_debug(f"wake_transcript_ready signal text={self._safe_voice_debug_text(text)}"))
        self.wake_worker.signals.finished.connect(self.on_wake_detected)
        self.wake_worker.signals.failed.connect(self.on_voice_failed)
        self.wake_worker.signals.error_ready.connect(self.on_voice_failed)
        self.thread_pool.start(self.wake_worker)

    def on_wake_detected(self, transcript: str) -> None:
        self.set_status("Listening")
        self.set_transcript(transcript)
        self.set_reply("Welcome back, Muhammad Afzal. I'm listening.")
        self.agent.disable_wake_mode()
        self.agent.speak("Welcome back, Muhammad Afzal. I'm listening.")
        self.on_voice_input()

    def speak_startup(self) -> None:
        if not self.agent.tts_enabled:
            return
        worker = AgentWorker(self.agent, "__speak_startup__", approved=True)
        worker.signals.finished.connect(lambda _result: None)
        worker.signals.failed.connect(lambda _error: None)
        self.thread_pool.start(worker)

    def on_speak_last_response(self) -> None:
        if self.last_response:
            result = self.agent.speak(self.last_response)
            if result != "Spoken.":
                self.set_reply(result)

    def on_toggle_voice(self) -> None:
        self.agent.set_voice_enabled(not self.agent.voice_enabled)
        state = "on" if self.agent.voice_enabled else "off"
        self.set_reply(f"Voice input is now {state}.")

    def on_toggle_tts(self) -> None:
        self.agent.set_tts_enabled(not self.agent.tts_enabled)
        state = "on" if self.agent.tts_enabled else "off"
        self.set_reply(f"Tony speech output is now {state}.")

    def on_check_voice_setup(self) -> None:
        status = get_voice_setup_status()
        message = status.as_text()
        self.voice_setup_output.setText(message)
        if status.ok:
            self.set_reply("Voice setup looks ready, Muhammad Afzal.")
        else:
            self.set_reply("Voice is not ready yet, Muhammad Afzal. Install requirements, then restart Tony. Text commands still work.")

    def on_open_screenshot_folder(self) -> None:
        path = Path("tony/logs/screenshots").resolve()
        path.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(path)
            self.set_reply(f"Opening screenshot folder: {path}")
        except Exception as exc:
            self.set_reply(f"Could not open screenshot folder: {exc}")

    def on_stop_task(self) -> None:
        if self.current_worker and hasattr(self.current_worker, "cancel"):
            self.current_worker.cancel()
        if self.wake_worker and hasattr(self.wake_worker, "cancel"):
            self.wake_worker.cancel()
        self.agent.disable_wake_mode()
        self.set_status("Online")
        self.set_reply("Stopped.")

    def run_command(self, command: str, approved: bool = False, command_source: str = "text", voice_transcript: str | None = None) -> None:
        if command_source not in {"voice", "wake"}:
            self.set_transcript(command)
        self.task_output.append(f"> {command}")
        worker = BrainWorker(self.brain, command, command_source=command_source)
        self.current_worker = worker
        worker.signals.started.connect(lambda: self.set_status("Working"))
        worker.signals.status.connect(self.set_status)
        worker.signals.finished.connect(self.on_brain_finished)
        worker.signals.failed.connect(self.on_failed)
        worker.signals.cancelled.connect(lambda: self.set_status("Cancelled"))
        self.thread_pool.start(worker)

    def on_brain_finished(self, response: dict) -> None:
        status = response.get("status", "completed")
        result = response.get("result", "")
        reply = response.get("reply", "")
        self.set_status(self._display_status(status))
        if response.get("normalized_text"):
            self.task_output.append(f"normalized: {response['normalized_text']}")
        if response.get("intent"):
            self.task_output.append(f"intent: {response['intent']} | safety: {response.get('safety', '')}")
        if result:
            self.task_output.append(result)
        self.set_reply(reply or "Done.")
        voice_debug(f"AssistantBrain response status={status} reply={self._safe_voice_debug_text(reply)}")
        if status not in {"waiting_for_approval", "blocked"}:
            self.set_status("Online")
        if response.get("should_speak") and self.agent.tts_enabled:
            self.agent.speak(reply.split("\n", 1)[0])

    def _display_status(self, status: str) -> str:
        labels = {
            "waiting_for_approval": "Waiting for Approval",
            "clarification": "Clarifying",
            "completed": "Replying",
            "blocked": "Blocked",
            "observing": "Observing",
            "teaching": "Teaching",
            "replaying": "Replaying",
            "screen_analysis": "Screen Analysis",
            "sensitive_screen_blocked": "Sensitive Screen Blocked",
            "cancelled": "Online",
            "error": "Online",
        }
        return labels.get(status, status.title())

    def on_finished(self, result: str) -> None:
        self.set_status("Replying")
        self.task_output.append(result or "Done.")
        self.set_reply(f"Done. Here is what I found.\n\n{result or 'Done.'}")
        self.set_status("Online")
        if self.agent.tts_enabled:
            self.agent.speak("Done.")

    def on_failed(self, error: str) -> None:
        self.task_output.append(error)
        self.set_status("Online")
        self.set_reply(f"I hit a problem: {error}")

    def _safe_voice_debug_text(self, text: str) -> str:
        lowered = (text or "").lower()
        if any(marker in lowered for marker in ["password", "secret", "token", ".env", "api key"]):
            return "[redacted]"
        return (text or "")[:200]

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose project folder", str(self.agent.project_dir))
        if folder:
            try:
                result = self.agent.set_workspace(Path(folder))
                self.workspace_label.setText(self._workspace_text())
                self.set_reply(result)
            except ValueError as exc:
                self.set_reply(f"Workspace blocked: {exc}")
