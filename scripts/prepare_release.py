from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    report_dir = ROOT / "tony" / "logs" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    health = subprocess.run([sys.executable, "scripts/health_check.py"], cwd=ROOT, text=True, capture_output=True)
    tests = subprocess.run([sys.executable, "-m", "pytest", "tests"], cwd=ROOT, text=True, capture_output=True)

    release_notes = report_dir / f"release_notes_v{version}.md"
    release_notes.write_text(
        "\n".join(
            [
                f"# Tony AI v{version} Release Notes Draft",
                "",
                "## Summary",
                "- Local voice-first Windows laptop assistant",
                "- Approval-gated safety system",
                "- Git/project/workflow/vision foundations",
                "- Local logs, memory, and test reports",
                "",
                "## Validation",
                f"- Health check exit code: {health.returncode}",
                f"- Pytest exit code: {tests.returncode}",
                "",
                "## Publishing",
                "This script does not commit, tag, push, or publish releases.",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Saved release notes draft: {release_notes}")
    print(f"pytest exit code: {tests.returncode}")
    return tests.returncode


if __name__ == "__main__":
    raise SystemExit(run())
