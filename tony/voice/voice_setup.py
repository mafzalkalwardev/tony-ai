from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass


REQUIRED_PACKAGES = {
    "faster_whisper": "faster-whisper",
    "sounddevice": "sounddevice",
    "numpy": "numpy",
    "pyttsx3": "pyttsx3",
}


@dataclass(frozen=True)
class VoiceSetupStatus:
    ok: bool
    missing_packages: list[str]
    microphone_available: bool
    python_executable: str
    install_command: str
    microphone_error: str = ""

    def as_text(self) -> str:
        lines = [
            f"Python: {self.python_executable}",
            f"faster-whisper installed: {'yes' if 'faster-whisper' not in self.missing_packages else 'no'}",
            f"sounddevice installed: {'yes' if 'sounddevice' not in self.missing_packages else 'no'}",
            f"numpy installed: {'yes' if 'numpy' not in self.missing_packages else 'no'}",
            f"pyttsx3 installed: {'yes' if 'pyttsx3' not in self.missing_packages else 'no'}",
            f"Microphone available: {'yes' if self.microphone_available else 'no'}",
        ]
        if self.microphone_error:
            lines.append(f"Microphone error: {self.microphone_error}")
        if not self.ok:
            lines.append(f"Install/fix command: {self.install_command}")
        return "\n".join(lines)


def check_voice_dependencies() -> list[str]:
    missing = []
    for import_name, package_name in REQUIRED_PACKAGES.items():
        if importlib.util.find_spec(import_name) is None:
            missing.append(package_name)
    return missing


def check_microphone_available() -> tuple[bool, str]:
    if importlib.util.find_spec("sounddevice") is None:
        return False, "sounddevice is not installed"

    try:
        import sounddevice as sd

        devices = sd.query_devices()
        default_input = sd.default.device[0] if sd.default.device else None
        has_input = any(device.get("max_input_channels", 0) > 0 for device in devices)
        if not has_input:
            return False, "No input microphone device was reported by sounddevice"
        if default_input is None or default_input < 0:
            return False, "No default input microphone is selected"
        return True, ""
    except Exception as exc:
        return False, str(exc)


def get_voice_setup_status() -> VoiceSetupStatus:
    missing = check_voice_dependencies()
    mic_available, mic_error = check_microphone_available()
    ok = not missing and mic_available
    return VoiceSetupStatus(
        ok=ok,
        missing_packages=missing,
        microphone_available=mic_available,
        python_executable=sys.executable,
        install_command="python -m pip install -r requirements.txt",
        microphone_error=mic_error,
    )
