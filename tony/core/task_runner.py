from __future__ import annotations

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    started = pyqtSignal()
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)


class AgentWorker(QRunnable):
    def __init__(self, agent, command: str, approved: bool = False) -> None:
        super().__init__()
        self.agent = agent
        self.command = command
        self.approved = approved
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self) -> None:
        self.signals.started.emit()
        try:
            result = self.agent.handle(self.command, approved=self.approved)
            self.signals.finished.emit(result)
        except Exception as exc:
            self.signals.failed.emit(f"Tony hit an error: {exc}")


class VoiceWorker(QRunnable):
    def __init__(self, agent) -> None:
        super().__init__()
        self.agent = agent
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self) -> None:
        self.signals.started.emit()
        try:
            result = self.agent.transcribe_voice_command()
            if result.error:
                self.signals.failed.emit(result.error)
                return
            self.signals.finished.emit(result.text)
        except Exception as exc:
            self.signals.failed.emit(f"Voice input failed: {exc}")
