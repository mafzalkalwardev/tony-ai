from __future__ import annotations


class TextToSpeech:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._engine = None

    def speak(self, text: str) -> str:
        if not self.enabled:
            return "Text-to-speech is disabled."

        try:
            import pyttsx3
        except ImportError:
            return "pyttsx3 is not installed. Tony will continue without speech output."

        try:
            if self._engine is None:
                self._engine = pyttsx3.init()
            self._engine.say(text)
            self._engine.runAndWait()
            return "Spoken."
        except Exception as exc:
            return f"Text-to-speech unavailable: {exc}"

    def stop(self) -> str:
        if self._engine is None:
            return "Text-to-speech is not running."
        try:
            self._engine.stop()
            return "Stopped."
        except Exception as exc:
            return f"Text-to-speech stop unavailable: {exc}"
