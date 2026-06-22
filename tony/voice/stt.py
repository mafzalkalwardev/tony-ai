from __future__ import annotations

import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    error: str = ""

    @property
    def ok(self) -> bool:
        return bool(self.text.strip()) and not self.error


class SpeechToText:
    def __init__(
        self,
        model_name: str = "small",
        sample_rate: int = 16000,
        record_seconds: int = 5,
        language: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.sample_rate = sample_rate
        self.record_seconds = record_seconds
        self.language = language
        self._model = None

    def transcribe_from_microphone(self) -> TranscriptionResult:
        try:
            wav_path = self._record_temp_wav()
        except ImportError as exc:
            return TranscriptionResult("", f"Voice input dependency missing: {exc.name}. Install requirements.txt.")
        except Exception as exc:
            return TranscriptionResult("", f"Microphone recording unavailable: {exc}")

        try:
            return self.transcribe_file(wav_path)
        finally:
            try:
                wav_path.unlink(missing_ok=True)
            except OSError:
                pass

    def transcribe_file(self, audio_path: Path) -> TranscriptionResult:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            return TranscriptionResult("", "faster-whisper is not installed. Install requirements.txt.")

        try:
            if self._model is None:
                self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
            segments, _info = self._model.transcribe(
                str(audio_path),
                language=self.language,
                vad_filter=True,
                beam_size=5,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            if not text:
                return TranscriptionResult("", "Tony did not hear clear speech. Try again closer to the microphone.")
            return TranscriptionResult(text)
        except Exception as exc:
            return TranscriptionResult("", f"Speech-to-text unavailable: {exc}")

    def _record_temp_wav(self) -> Path:
        import numpy as np
        import sounddevice as sd

        frames = int(self.sample_rate * self.record_seconds)
        audio = sd.rec(frames, samplerate=self.sample_rate, channels=1, dtype="int16")
        sd.wait()

        handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        path = Path(handle.name)
        handle.close()

        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(np.asarray(audio, dtype=np.int16).tobytes())

        return path
