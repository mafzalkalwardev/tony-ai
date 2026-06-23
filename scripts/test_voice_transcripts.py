from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tony.core.assistant_brain import AssistantBrain
from tony.core.command_normalizer import CommandNormalizer
from tony.core.intent_router import IntentRouter
from tony.core.safety import SafetySystem
from tony.voice.wake_word import is_wake_phrase


TRANSCRIPTS = [
    "Wake Up Tony",
    "repo status dikhao",
    "Tony VS Code kholo",
    "Tony git push karo",
    "Tony rm rf project",
    "Tony dot env read karo",
    "Tony project analyze karo",
]


class DryRunRegistry:
    def is_ready(self, route: dict) -> bool:
        return route.get("intent") != "unknown"

    def execute(self, route: dict, normalized_text: str, source: str = "voice", raw_text: str = "", approved: bool = False) -> str:
        return f"Dry run only. Would execute {route.get('intent')} from voice."


def run() -> int:
    report_dir = ROOT / "tony" / "logs" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "voice_transcript_test_report.md"

    lines = ["# Tony Voice Transcript Simulation Report", ""]
    for transcript in TRANSCRIPTS:
        normalizer = CommandNormalizer()
        brain = AssistantBrain(
            agent=None,
            normalizer=normalizer,
            router=IntentRouter(normalizer),
            safety=SafetySystem(),
            registry=DryRunRegistry(),
        )
        response = brain.handle_command(transcript, source="voice")
        lines.extend(
            [
                f"## `{transcript}`",
                "",
                f"- Wake phrase: `{is_wake_phrase(transcript)}`",
                f"- Normalized: `{response['normalized_text']}`",
                f"- Intent: `{response['intent']}`",
                f"- Safety: `{response['safety']}`",
                f"- Status: `{response['status']}`",
                f"- Reply: {response['reply'].splitlines()[0] if response['reply'] else ''}",
                "",
            ]
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved voice transcript report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
