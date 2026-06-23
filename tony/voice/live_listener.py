from __future__ import annotations

import threading
import time
from collections.abc import Callable

from tony.voice.debug_log import voice_debug
from tony.voice.wake_engine import WakeEngine


class LiveVoiceListener:
    def __init__(self, agent, wake_engine: WakeEngine, poll_seconds: float = 0.25) -> None:
        self.agent = agent
        self.wake_engine = wake_engine
        self.poll_seconds = poll_seconds
        self._running = False
        self._thread: threading.Thread | None = None
        self.on_status: Callable[[str], None] | None = None
        self.on_audio_level: Callable[[float], None] | None = None
        self.on_transcript: Callable[[str], None] | None = None
        self.on_error: Callable[[str], None] | None = None

    def start_live_mode(self) -> str:
        if self._running:
            return "Live voice mode is already running."
        self._running = True
        self.wake_engine.start()
        self._thread = threading.Thread(target=self.listen_for_wake, daemon=True)
        self._thread.start()
        voice_debug("live voice mode started")
        return "Live voice mode started. Wake phrase detection uses local fallback if openwakeword is unavailable."

    def stop_live_mode(self) -> str:
        self._running = False
        self.wake_engine.stop()
        voice_debug("live voice mode stopped")
        return "Live voice mode stopped."

    def listen_for_wake(self) -> None:
        if self.on_status:
            self.on_status("wake_listening")
        while self._running:
            voice_debug("wake chunk transcription started")
            result = self.agent.transcribe_wake_phrase_chunk(
                level_callback=self.emit_audio_level,
                status_callback=self._emit_status,
            )
            if not self._running:
                return
            if result.error:
                voice_debug(f"wake chunk transcription result error={result.error}")
                lowered_error = result.error.lower()
                if "could not hear a clear command" in lowered_error or "recording is too quiet" in lowered_error:
                    time.sleep(self.poll_seconds)
                    continue
                if self.on_error:
                    self.on_error(result.error)
                time.sleep(self.poll_seconds)
                continue
            transcript = result.text.strip()
            voice_debug(f"wake chunk transcription result={_safe_text(transcript)}")
            matched = self.wake_engine.detect_wake_phrase(text=transcript)
            voice_debug(f"wake phrase matched {matched}")
            if matched:
                if self.on_transcript:
                    self.on_transcript(transcript)
                self.listen_for_command()
            time.sleep(self.poll_seconds)

    def listen_for_command(self) -> None:
        if self.on_status:
            self.on_status("listening")
        result = self.agent.transcribe_voice_command()
        if result.error:
            if self.on_error:
                self.on_error(result.error)
            return
        if self.on_transcript:
            voice_debug(f"command transcript result={_safe_text(result.text)}")
            self.on_transcript(result.text)

    def emit_audio_level(self, level: float) -> None:
        if self.on_audio_level:
            self.on_audio_level(level)

    def _emit_status(self, status: str) -> None:
        if self.on_status:
            self.on_status(status)


def _safe_text(text: str) -> str:
    lowered = (text or "").lower()
    if any(marker in lowered for marker in ["password", "secret", "token", ".env", "api key"]):
        return "[redacted]"
    return (text or "")[:200]
