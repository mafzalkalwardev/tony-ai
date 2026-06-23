from __future__ import annotations

import os
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from tony.voice.debug_log import voice_debug


def _configure_hf_env() -> None:
    """Ensure HuggingFace Hub can use an existing token (avoids unauthenticated warnings / slowdowns)."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if token:
        os.environ.setdefault("HF_TOKEN", token)
        os.environ.setdefault("HUGGINGFACE_HUB_TOKEN", token)


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
        model_name: str = "base",
        sample_rate: int = 16000,
        record_seconds: int = 5,
        language: str | None = None,
        compute_type: str = "int8",
    ) -> None:
        self.model_name = model_name
        self.sample_rate = sample_rate
        self.record_seconds = record_seconds
        self.language = language
        self.compute_type = compute_type
        self._model = None
        self.last_audio_path = Path("tony/logs/voice/last_command.wav")
        self.last_wake_audio_path = Path("tony/logs/voice/last_wake_chunk.wav")
        self.last_audio_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_rms: float | None = None
        self.last_peak: float | None = None

    def transcribe_from_microphone(
        self,
        level_callback: Callable[[float], None] | None = None,
        status_callback: Callable[[str], None] | None = None,
        record_seconds: float | None = None,
        output_path: Path | str | None = None,
    ) -> TranscriptionResult:
        try:
            wav_path = self._record_temp_wav(
                level_callback=level_callback,
                record_seconds=record_seconds,
                output_path=output_path,
            )
        except ImportError as exc:
            if exc.name == "sounddevice":
                return TranscriptionResult("", "Microphone recording is not installed. Run: python -m pip install sounddevice")
            return TranscriptionResult("", f"Voice dependency is missing: {exc.name}. Run: python -m pip install -r requirements.txt")
        except Exception as exc:
            return TranscriptionResult("", f"Microphone not detected. Check Windows microphone permission and input device. Details: {exc}")

        if self.last_peak is not None and self.last_rms is not None and (0 <= self.last_peak < 0.01 or self.last_rms < 0.004):
            voice_debug(f"recording too quiet rms={self.last_rms:.6f} peak={self.last_peak:.6f}")
            return TranscriptionResult("", "I can hear the microphone level, but the recording is too quiet. Check your input volume.")

        try:
            if status_callback:
                status_callback("Loading Voice Model" if self._model is None else "Transcribing")
            voice_debug(f"command transcription started path={wav_path}")
            return self.transcribe_file(wav_path)
        finally:
            try:
                wav_path.unlink(missing_ok=True)
            except OSError:
                pass

    def transcribe_file(self, audio_path: Path) -> TranscriptionResult:
        _configure_hf_env()
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            return TranscriptionResult("", "Voice transcription is not installed. Run: python -m pip install -r requirements.txt")

        try:
            if self._model is None:
                voice_debug(f"Loading Whisper model: {self.model_name}")
                self._model = WhisperModel(self.model_name, device="cpu", compute_type=self.compute_type)
            segments, _info = self._model.transcribe(
                str(audio_path),
                language=self.language,
                vad_filter=True,
                beam_size=5,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            voice_debug(f"transcription result text={_safe_text(text)}")
            if not text:
                return TranscriptionResult("", "I could not hear a clear command. Please try again.")
            return TranscriptionResult(text)
        except Exception as exc:
            voice_debug(f"transcription error={exc}")
            return TranscriptionResult("", f"Voice transcription could not start. Run: python -m pip install -r requirements.txt. Details: {exc}")

    def _record_temp_wav(
        self,
        level_callback: Callable[[float], None] | None = None,
        record_seconds: float | None = None,
        output_path: Path | str | None = None,
    ) -> Path:
        import math
        import shutil

        import numpy as np
        import sounddevice as sd

        chunks = []
        block_seconds = 0.1
        block_frames = int(self.sample_rate * block_seconds)
        seconds = float(record_seconds if record_seconds is not None else self.record_seconds)
        total_blocks = max(1, int(seconds / block_seconds))
        voice_debug(f"microphone stream opening sample_rate={self.sample_rate} channels=1 seconds={seconds}")

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32", blocksize=block_frames) as stream:
                for _ in range(total_blocks):
                    chunk, _overflowed = stream.read(block_frames)
                    samples = np.asarray(chunk, dtype="float32").reshape(-1)
                    rms = math.sqrt(float(np.mean(samples * samples))) if samples.size else 0.0
                    voice_debug(f"audio chunk received rms={rms:.6f} speech_detected={rms >= 0.015}")
                    if level_callback:
                        level_callback(min(1.0, rms * 8.0))
                    chunks.append(samples)
        except Exception as exc:
            raise RuntimeError(f"{exc}. Check Windows microphone permissions and selected input device.") from exc

        audio_float = np.concatenate(chunks) if chunks else np.zeros(block_frames, dtype="float32")
        peak = float(np.max(np.abs(audio_float))) if audio_float.size else 0.0
        rms = math.sqrt(float(np.mean(audio_float * audio_float))) if audio_float.size else 0.0
        self.last_rms = rms
        self.last_peak = peak
        voice_debug(f"recording complete rms={rms:.6f} peak={peak:.6f}")
        if peak > 0:
            audio_float = audio_float / peak * 0.85
        audio = np.clip(audio_float * 32767, -32768, 32767).astype("int16")

        handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        path = Path(handle.name)
        handle.close()

        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio.tobytes())
        target = Path(output_path) if output_path else self.last_audio_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        voice_debug(f"audio saved path={target}")
        return path


def _safe_text(text: str) -> str:
    cleaned = (text or "").strip()
    blocked = ["password", "secret", "token", "api key", ".env"]
    lowered = cleaned.lower()
    if any(marker in lowered for marker in blocked):
        return "[redacted]"
    return cleaned[:200]
