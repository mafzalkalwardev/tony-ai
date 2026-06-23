from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LiveStatus(str, Enum):
    IDLE = "idle"
    WAKE_LISTENING = "wake_listening"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class LiveState:
    status: LiveStatus = LiveStatus.IDLE
    last_transcript: str = ""
    last_audio_level: float = 0.0
    wake_mode_enabled: bool = False
    live_voice_enabled: bool = False

    def set_status(self, status: LiveStatus) -> None:
        self.status = status

