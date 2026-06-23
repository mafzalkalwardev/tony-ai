from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tony.core.agent import TonyAgent


def run() -> int:
    report_dir = ROOT / "tony" / "logs" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / "wake_phrase_live_test.md"
    audio_path = ROOT / "tony" / "logs" / "voice" / "wake_phrase_test.wav"
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    agent = TonyAgent(ROOT)
    print("Say: Wake Up, Tony.")
    result = agent.stt.transcribe_from_microphone(
        status_callback=lambda status: print(f"Status: {status}"),
        record_seconds=3,
        output_path=audio_path,
    )
    matched = bool(result.text and agent.wake_engine.detect_wake_phrase(text=result.text))
    lines = [
        "# Wake Phrase Live Test",
        "",
        f"- Audio: `{audio_path}`",
        f"- Transcript: `{result.text}`",
        f"- Error: `{result.error}`",
        f"- Matched: `{matched}`",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Transcript: {result.text or '[empty]'}")
    print(f"Matched: {matched}")
    print(f"Saved report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
