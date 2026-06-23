from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tony.core.agent import TonyAgent
from tony.core.assistant_brain import AssistantBrain


def run() -> int:
    report_dir = ROOT / "tony" / "logs" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / "live_voice_smoke_test.md"
    audio_path = ROOT / "tony" / "logs" / "voice" / "live_voice_smoke_test.wav"
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    agent = TonyAgent(ROOT)
    lines = ["# Live Voice Smoke Test", "", f"- Python: `{sys.executable}`", f"- Model: `{agent.stt.model_name}`"]
    print("Speak any Tony command for 5 seconds.")
    levels: list[float] = []
    result = agent.stt.transcribe_from_microphone(
        level_callback=levels.append,
        status_callback=lambda status: print(f"Status: {status}"),
        record_seconds=5,
        output_path=audio_path,
    )
    lines.append(f"- Audio: `{audio_path}`")
    lines.append(f"- RMS avg: `{sum(levels) / len(levels) if levels else 0:.6f}`")
    lines.append(f"- RMS max: `{max(levels) if levels else 0:.6f}`")
    lines.append(f"- STT error: `{result.error}`")
    lines.append(f"- Transcript: `{result.text}`")

    if result.text:
        response = AssistantBrain(agent).handle_command(result.text, source="voice")
        lines.extend(
            [
                f"- Intent: `{response['intent']}`",
                f"- Safety: `{response['safety']}`",
                f"- Status: `{response['status']}`",
                f"- Reply: {response['reply'].splitlines()[0] if response['reply'] else ''}",
            ]
        )
        print(f"Transcript: {result.text}")
        print(f"Intent: {response['intent']} | Safety: {response['safety']} | Status: {response['status']}")
        print(response["reply"].splitlines()[0])
    else:
        print(result.error or "No transcript.")

    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
