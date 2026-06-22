from __future__ import annotations


class TextToSpeech:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def speak(self, text: str) -> str:
        if not self.enabled:
            return "Text-to-speech is disabled."

        try:
            import pyttsx3
        except ImportError:
            return "pyttsx3 is not installed. Tony will continue without speech output."

        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return "Spoken."
        except Exception as exc:
            return f"Text-to-speech unavailable: {exc}"
