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
    report = report_dir / "push_to_talk_live_test.md"
    audio_path = ROOT / "tony" / "logs" / "voice" / "push_to_talk_live_test.wav"
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    agent = TonyAgent(ROOT)
    print("Say: repo status dikhao.")
    result = agent.stt.transcribe_from_microphone(
        status_callback=lambda status: print(f"Status: {status}"),
        record_seconds=5,
        output_path=audio_path,
    )
    response = AssistantBrain(agent).handle_command(result.text, source="voice") if result.text else None
    lines = [
        "# Push To Talk Live Test",
        "",
        f"- Audio: `{audio_path}`",
        f"- Transcript: `{result.text}`",
        f"- Error: `{result.error}`",
    ]
    if response:
        lines.extend(
            [
                f"- Intent: `{response['intent']}`",
                f"- Safety: `{response['safety']}`",
                f"- Status: `{response['status']}`",
                f"- Reply: {response['reply'].splitlines()[0] if response['reply'] else ''}",
            ]
        )
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Transcript: {result.text or '[empty]'}")
    if response:
        print(f"Intent: {response['intent']} | Safety: {response['safety']} | Status: {response['status']}")
    else:
        print(result.error or "No transcript.")
    print(f"Saved report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
