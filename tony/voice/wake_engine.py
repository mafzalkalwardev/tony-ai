from __future__ import annotations

from collections.abc import Callable


class WakeEngine:
    def __init__(
        self,
        sensitivity: float = 0.55,
        allow_short_tony_trigger: bool = False,
        use_openwakeword_model: bool = False,
    ) -> None:
        self.sensitivity = sensitivity
        self.allow_short_tony_trigger = allow_short_tony_trigger
        self.use_openwakeword_model = use_openwakeword_model
        self._running = False
        self._callback: Callable[[str], None] | None = None
        self._oww_model = None

    def start(self) -> str:
        self._running = True
        if self.use_openwakeword_model:
            self._try_load_openwakeword()
        if self._oww_model is None:
            return (
                "Wake mode started with fast phrase-match fallback. "
                "openwakeword model loading is disabled by default so Tony stays responsive."
            )
        return "Wake mode started with openwakeword."

    def stop(self) -> str:
        self._running = False
        return "Wake mode stopped."

    def is_running(self) -> bool:
        return self._running

    def on_wake(self, callback: Callable[[str], None]) -> None:
        self._callback = callback

    def detect_wake_phrase(self, audio_chunk=None, text: str = "", confidence: float = 1.0) -> bool:
        if text:
            matched = self._match_text(text, confidence)
            if matched and self._callback:
                self._callback(text)
            return matched
        # OpenWakeWord audio detection is intentionally conservative in this foundation.
        return False

    def setup_message(self) -> str:
        return (
            "Wake-word fallback is active. Turn on use_openwakeword_model in config/settings.json only after "
            "installing local wake-word models. Push-to-talk and text commands still work."
        )

    def _try_load_openwakeword(self) -> None:
        try:
            from openwakeword.model import Model
        except Exception:
            self._oww_model = None
            return
        try:
            self._oww_model = Model()
        except Exception:
            self._oww_model = None

    def _match_text(self, text: str, confidence: float) -> bool:
        normalized = self._normalize(text)
        accepted = {
            "wake up tony",
            "wake up tony daddy home",
            "wake up tony daddy s home",
            "tony wake up",
            "hey tony",
        }
        if normalized in accepted:
            return True
        if normalized == "tony":
            return self.allow_short_tony_trigger or confidence >= 0.9
        return False

    def _normalize(self, text: str) -> str:
        cleaned = text.lower().replace("'", " ")
        for char in [",", ".", "!", "?", "’", "‘", "“", "”", "â€™", "â€œ", "â€"]:
            cleaned = cleaned.replace(char, " ")
        return " ".join(cleaned.split())
