from __future__ import annotations

import math


class VoiceActivityDetector:
    def __init__(self, silence_threshold: float = 0.015, silence_stop_seconds: float = 1.2, sample_rate: int = 16000) -> None:
        self.silence_threshold = silence_threshold
        self.silence_stop_seconds = silence_stop_seconds
        self.sample_rate = sample_rate
        self._silent_seconds = 0.0

    def is_speech(self, audio_chunk) -> bool:
        try:
            import numpy as np
            samples = np.asarray(audio_chunk, dtype="float32")
            if samples.size == 0:
                return False
            rms = math.sqrt(float(np.mean(samples * samples)))
            return rms >= self.silence_threshold
        except Exception:
            return False

    def should_stop_for_silence(self, audio_chunk, chunk_seconds: float) -> bool:
        if self.is_speech(audio_chunk):
            self._silent_seconds = 0.0
            return False
        self._silent_seconds += chunk_seconds
        return self._silent_seconds >= self.silence_stop_seconds

    def reset(self) -> None:
        self._silent_seconds = 0.0

