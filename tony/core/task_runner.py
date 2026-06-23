from __future__ import annotations

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

from tony.voice.debug_log import voice_debug


class WorkerSignals(QObject):
    started = pyqtSignal()
    status = pyqtSignal(str)
    level = pyqtSignal(float)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()


class WakeSignals(QObject):
    started = pyqtSignal()
    status = pyqtSignal(str)
    level = pyqtSignal(float)
    wake_transcript_ready = pyqtSignal(str)
    command_transcript_ready = pyqtSignal(str)
    reply_ready = pyqtSignal(str)
    error_ready = pyqtSignal(str)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()


class BrainSignals(QObject):
    started = pyqtSignal()
    status = pyqtSignal(str)
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()


class BrainWorker(QRunnable):
    def __init__(self, brain, command: str, command_source: str = "text") -> None:
        super().__init__()
        self.brain = brain
        self.command = command
        self.command_source = command_source
        self.cancel_requested = False
        self.signals = BrainSignals()

    def cancel(self) -> None:
        self.cancel_requested = True

    @pyqtSlot()
    def run(self) -> None:
        self.signals.started.emit()
        self.signals.status.emit("thinking")
        if self.cancel_requested:
            self.signals.cancelled.emit()
            return
        try:
            response = self.brain.handle_command(self.command, source=self.command_source)
            if self.cancel_requested:
                self.signals.cancelled.emit()
                return
            self.signals.finished.emit(response)
        except Exception as exc:
            self.signals.failed.emit(f"Tony hit an error: {exc}")


class AgentWorker(QRunnable):
    def __init__(
        self,
        agent,
        command: str,
        approved: bool = False,
        command_source: str = "text",
        voice_transcript: str | None = None,
    ) -> None:
        super().__init__()
        self.agent = agent
        self.command = command
        self.approved = approved
        self.command_source = command_source
        self.voice_transcript = voice_transcript
        self.cancel_requested = False
        self.signals = WorkerSignals()

    def cancel(self) -> None:
        self.cancel_requested = True

    @pyqtSlot()
    def run(self) -> None:
        self.signals.started.emit()
        self.signals.status.emit("running")
        if self.cancel_requested:
            self.signals.cancelled.emit()
            return
        try:
            result = self.agent.handle(
                self.command,
                approved=self.approved,
                command_source=self.command_source,
                voice_transcript=self.voice_transcript,
            )
            if self.cancel_requested:
                self.signals.cancelled.emit()
                return
            self.signals.finished.emit(result)
        except Exception as exc:
            self.signals.failed.emit(f"Tony hit an error: {exc}")


class VoiceWorker(QRunnable):
    def __init__(self, agent) -> None:
        super().__init__()
        self.agent = agent
        self.cancel_requested = False
        self.signals = WorkerSignals()

    def cancel(self) -> None:
        self.cancel_requested = True

    @pyqtSlot()
    def run(self) -> None:
        self.signals.started.emit()
        self.signals.status.emit("listening")
        if self.cancel_requested:
            self.signals.cancelled.emit()
            return
        try:
            voice_debug("command listening started")
            result = self.agent.transcribe_voice_command(
                level_callback=self.signals.level.emit,
                status_callback=self.signals.status.emit,
            )
            if result.error:
                voice_debug(f"command transcription error={result.error}")
                self.signals.failed.emit(result.error)
                return
            voice_debug(f"command transcript result={_safe_debug_text(result.text)}")
            self.signals.finished.emit(result.text)
        except Exception as exc:
            self.signals.failed.emit(f"Voice input failed: {exc}")


class WakeWorker(QRunnable):
    def __init__(self, agent) -> None:
        super().__init__()
        self.agent = agent
        self.cancel_requested = False
        self.signals = WakeSignals()

    def cancel(self) -> None:
        self.cancel_requested = True

    @pyqtSlot()
    def run(self) -> None:
        self.signals.started.emit()
        self.signals.status.emit("Wake Listening")
        voice_debug("wake mode started")
        try:
            self.agent.enable_wake_mode()
            while not self.cancel_requested and self.agent.live_state.wake_mode_enabled:
                self.signals.status.emit("Wake Listening")
                result = self.agent.transcribe_wake_phrase_chunk(
                    level_callback=self.signals.level.emit,
                    status_callback=self.signals.status.emit,
                )
                if self.cancel_requested:
                    self.signals.cancelled.emit()
                    return
                if result.error:
                    voice_debug(f"wake chunk transcription result error={result.error}")
                    lowered_error = result.error.lower()
                    if "could not hear a clear command" in lowered_error or "recording is too quiet" in lowered_error:
                        continue
                    self.signals.failed.emit(result.error)
                    return
                transcript = result.text.strip()
                voice_debug(f"wake chunk transcription result={_safe_debug_text(transcript)}")
                if transcript and self.agent.wake_engine.detect_wake_phrase(text=transcript):
                    voice_debug("wake phrase matched true")
                    self.agent.memory.log_wake_event(transcript)
                    self.signals.wake_transcript_ready.emit(transcript)
                    self.signals.finished.emit(transcript)
                    return
                voice_debug("wake phrase matched false")
        except Exception as exc:
            voice_debug(f"wake mode failed={exc}")
            self.signals.failed.emit(f"Wake mode failed: {exc}")


def _safe_debug_text(text: str) -> str:
    lowered = (text or "").lower()
    if any(marker in lowered for marker in ["password", "secret", "token", ".env", "api key"]):
        return "[redacted]"
    return (text or "")[:200]
