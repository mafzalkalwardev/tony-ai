from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from tony.core.agent import TonyAgent
from tony.core.safety import SafetyLevel
from tony.core.task_runner import AgentWorker, VoiceWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Tony AI Control Center")
        self.resize(980, 680)
        self.agent = TonyAgent(Path.cwd())
        self.thread_pool = QThreadPool.globalInstance()
        self.pending_command: str | None = None

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Tony, repo status dikhao...")
        self.status = QLabel("Tony Online")
        self.status.setObjectName("statusBadge")

        self.run_button = QPushButton("Run")
        self.open_folder_button = QPushButton("Open Folder")
        self.git_status_button = QPushButton("Git Status")
        self.run_command_button = QPushButton("Run Command")
        self.voice_button = QPushButton("Voice Input")
        self.clear_button = QPushButton("Clear Logs")

        self._build_layout()
        self._connect_signals()
        self._load_styles()
        self.append("Tony", "Welcome back, Muhammad Afzal. Tony is online.")
        self.speak_startup()

    def _build_layout(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        top = QHBoxLayout()
        buttons = QHBoxLayout()
        command_row = QHBoxLayout()

        top.addWidget(QLabel("Tony AI Control Center"))
        top.addStretch()
        top.addWidget(self.status)

        buttons.addWidget(self.open_folder_button)
        buttons.addWidget(self.git_status_button)
        buttons.addWidget(self.run_command_button)
        buttons.addWidget(self.voice_button)
        buttons.addWidget(self.clear_button)

        command_row.addWidget(self.input)
        command_row.addWidget(self.run_button)

        layout.addLayout(top)
        layout.addWidget(self.chat)
        layout.addLayout(buttons)
        layout.addLayout(command_row)
        self.setCentralWidget(root)

    def _connect_signals(self) -> None:
        self.run_button.clicked.connect(self.on_run)
        self.input.returnPressed.connect(self.on_run)
        self.open_folder_button.clicked.connect(lambda: self.run_command("open folder kholo"))
        self.git_status_button.clicked.connect(lambda: self.run_command("repo status dikhao"))
        self.run_command_button.clicked.connect(self.on_run)
        self.voice_button.clicked.connect(self.on_voice_input)
        self.clear_button.clicked.connect(self.chat.clear)

    def _load_styles(self) -> None:
        style_path = Path(__file__).with_name("styles.qss")
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))

    def append(self, speaker: str, text: str) -> None:
        self.chat.append(f"<b>{speaker}:</b> {text.replace(chr(10), '<br>')}")

    def set_status(self, text: str) -> None:
        self.status.setText(text)

    def on_run(self) -> None:
        command = self.input.text().strip()
        if not command:
            return
        self.input.clear()

        if self.pending_command and self.agent.safety.is_approved_text(command):
            approved_command = self.pending_command
            self.pending_command = None
            self.append("You", "yes")
            self.run_command(approved_command, approved=True)
            return

        if self.pending_command and self.agent.safety.is_rejected_text(command):
            self.append("You", command)
            self.append("Tony", "Action cancelled.")
            self.pending_command = None
            self.set_status("Tony Online")
            return

        self.run_command(command)

    def on_voice_input(self) -> None:
        self.append("Tony", "Listening for 5 seconds...")
        self.voice_button.setEnabled(False)
        worker = VoiceWorker(self.agent)
        worker.signals.started.connect(lambda: self.set_status("Listening"))
        worker.signals.finished.connect(self.on_voice_transcribed)
        worker.signals.failed.connect(self.on_voice_failed)
        self.thread_pool.start(worker)

    def on_voice_transcribed(self, text: str) -> None:
        self.voice_button.setEnabled(True)
        self.set_status("Tony Online")
        self.append("Recognized", text)

        if self.pending_command and self.agent.safety.is_approved_text(text):
            approved_command = self.pending_command
            self.pending_command = None
            self.run_command(approved_command, approved=True)
            return

        if self.pending_command and self.agent.safety.is_rejected_text(text):
            self.append("Tony", "Action cancelled.")
            self.pending_command = None
            return

        self.run_command(text)

    def on_voice_failed(self, error: str) -> None:
        self.voice_button.setEnabled(True)
        self.append("Tony", error)
        self.set_status("Tony Online")

    def speak_startup(self) -> None:
        if not self.agent.voice_enabled:
            return
        worker = AgentWorker(self.agent, "__speak_startup__", approved=True)
        worker.signals.finished.connect(lambda _result: None)
        worker.signals.failed.connect(lambda _error: None)
        self.thread_pool.start(worker)

    def run_command(self, command: str, approved: bool = False) -> None:
        self.append("You", command)
        intent, plan, safety_level = self.agent.preview(command)
        if safety_level == SafetyLevel.NEEDS_APPROVAL.value and not approved:
            self.pending_command = command
            self.set_status("Waiting for Approval")
            self.append("Tony", f"{plan}<br>Approve this action? yes/no")
            return

        worker = AgentWorker(self.agent, command, approved=approved)
        worker.signals.started.connect(lambda: self.set_status("Working"))
        worker.signals.finished.connect(self.on_finished)
        worker.signals.failed.connect(self.on_failed)
        self.thread_pool.start(worker)

    def on_finished(self, result: str) -> None:
        self.append("Tony", result or "Done.")
        self.set_status("Tony Online")

    def on_failed(self, error: str) -> None:
        self.append("Tony", error)
        self.set_status("Tony Online")

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose project folder", str(self.agent.project_dir))
        if folder:
            self.agent.project_dir = Path(folder)
            self.append("Tony", f"Project folder set to: {folder}")
