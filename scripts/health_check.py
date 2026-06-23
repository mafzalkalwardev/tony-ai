from __future__ import annotations

import importlib.util
import platform
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


REQUIRED = ["PyQt6", "requests", "pytest", "numpy"]
OPTIONAL = ["faster_whisper", "sounddevice", "scipy", "pyttsx3", "mss", "PIL", "psutil", "pygetwindow", "pynput", "pyautogui", "cv2", "pytesseract"]


def package_status(name: str) -> str:
    return "installed" if importlib.util.find_spec(name) is not None else "missing"


def run() -> int:
    report_dir = ROOT / "tony" / "logs" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "health_check_report.md"
    logs_dir = ROOT / "tony" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    checks = [
        ("Python", platform.python_version()),
        ("Config settings", "ok" if (ROOT / "config" / "settings.json").exists() else "missing"),
        ("Config permissions", "ok" if (ROOT / "config" / "permissions.json").exists() else "missing"),
        ("Logs writable", _writable(logs_dir)),
        ("Database writable", _db_writable(logs_dir / "health_check.db")),
        ("Git", shutil.which("git") or "missing"),
        ("GitHub CLI", shutil.which("gh") or "missing"),
        ("Ollama", _ollama_status()),
        ("Tests folder", "ok" if (ROOT / "tests").exists() else "missing"),
        ("Microphone", _microphone_status()),
    ]
    lines = ["# Tony Health Check", "", "## Environment", ""]
    for name, value in checks:
        lines.append(f"- {name}: {value}")
    lines.extend(["", "## Required Packages", ""])
    for package in REQUIRED:
        lines.append(f"- {package}: {package_status(package)}")
    lines.extend(["", "## Optional Packages", ""])
    for package in OPTIONAL:
        lines.append(f"- {package}: {package_status(package)}")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved health check report: {report_path}")
    return 0


def _writable(path: Path) -> str:
    try:
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return "ok"
    except Exception as exc:
        return f"failed: {exc}"


def _db_writable(path: Path) -> str:
    try:
        with sqlite3.connect(path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS health (ok INTEGER)")
        return "ok"
    except Exception as exc:
        return f"failed: {exc}"


def _ollama_status() -> str:
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return f"reachable ({response.status_code})"
    except Exception:
        return "not reachable"


def _microphone_status() -> str:
    if importlib.util.find_spec("sounddevice") is None:
        return "sounddevice missing"
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        return "available" if any(device.get("max_input_channels", 0) > 0 for device in devices) else "no input device"
    except Exception as exc:
        return f"unavailable: {exc}"


if __name__ == "__main__":
    raise SystemExit(run())
