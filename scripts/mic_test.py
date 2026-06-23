from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run() -> int:
    output = ROOT / "tony" / "logs" / "voice" / "mic_test.wav"
    output.parent.mkdir(parents=True, exist_ok=True)

    if importlib.util.find_spec("sounddevice") is None or importlib.util.find_spec("scipy") is None:
        print("Microphone test needs sounddevice and scipy.")
        print("Install command: python -m pip install -r requirements.txt")
        return 0

    try:
        import sounddevice as sd
        from scipy.io import wavfile

        print("Available input devices:")
        for index, device in enumerate(sd.query_devices()):
            if device.get("max_input_channels", 0) > 0:
                print(f"- {index}: {device.get('name')}")
        print("Recording 3 seconds...")
        sample_rate = 16000
        audio = sd.rec(int(3 * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
        sd.wait()
        rms = float(np.sqrt(np.mean(np.square(audio)))) if audio.size else 0.0
        wavfile.write(output, sample_rate, np.clip(audio[:, 0] * 32767, -32768, 32767).astype(np.int16))
        print(f"Saved: {output}")
        print(f"RMS level: {rms:.6f}")
    except Exception as exc:
        print(f"Microphone test failed safely: {exc}")
        return 0

    if importlib.util.find_spec("faster_whisper") is None:
        print("faster-whisper is not installed. Install command: python -m pip install -r requirements.txt")
        return 0

    try:
        from faster_whisper import WhisperModel

        print("Transcribing with faster-whisper tiny model...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(output), vad_filter=True)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        print(f"Detected language: {getattr(info, 'language', 'unknown')}")
        print(f"Transcript: {text or '[empty]'}")
    except Exception as exc:
        print(f"Transcription skipped safely: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
