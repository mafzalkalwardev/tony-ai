from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tony.core.assistant_brain import AssistantBrain
from tony.core.command_normalizer import CommandNormalizer
from tony.core.intent_router import IntentRouter
from tony.core.safety import SafetySystem


COMMANDS = [
    "repo status dikhao",
    "VS Code kholo",
    "terminal kholo",
    "project analyze karo",
    "git push karo",
    "screen record karo",
    "recording band karo",
    "rm -rf project",
    ".env read karo",
    "client message banao",
    "delivery report banao",
    "Codex prompt banao",
    "Wake Up Tony repo status dikhao",
]


class DryRunRegistry:
    def is_ready(self, route: dict) -> bool:
        return route.get("intent") != "unknown"

    def execute(self, route: dict, normalized_text: str, source: str = "text", raw_text: str = "", approved: bool = False) -> str:
        return f"Dry run only. Would execute {route.get('intent')} from {source}."


def run() -> int:
    report_dir = ROOT / "tony" / "logs" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "command_test_report.md"

    lines = ["# Tony Command Simulation Report", ""]
    for command in COMMANDS:
        normalizer = CommandNormalizer()
        brain = AssistantBrain(
            agent=None,
            normalizer=normalizer,
            router=IntentRouter(normalizer),
            safety=SafetySystem(),
            registry=DryRunRegistry(),
        )
        response = brain.handle_command(command, source="text")
        lines.extend(
            [
                f"## `{command}`",
                "",
                f"- Normalized: `{response['normalized_text']}`",
                f"- Intent: `{response['intent']}`",
                f"- Safety: `{response['safety']}`",
                f"- Status: `{response['status']}`",
                f"- Reply: {response['reply'].splitlines()[0] if response['reply'] else ''}",
                "",
            ]
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved command simulation report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
