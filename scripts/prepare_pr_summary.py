from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_output(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return result.stdout.strip() or result.stderr.strip()


def run() -> int:
    report_dir = ROOT / "tony" / "logs" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "pr_summary.md"
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8") if (ROOT / "CHANGELOG.md").exists() else ""
    path.write_text(
        "\n".join(
            [
                "# PR Summary Draft",
                "",
                "## Git Status",
                "```text",
                git_output("status", "--short"),
                "```",
                "",
                "## Diff Stat",
                "```text",
                git_output("diff", "--stat"),
                "```",
                "",
                "## Changelog",
                changelog[:4000],
                "",
                "## Validation",
                "- Run `python -m pytest tests` before opening the PR.",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Saved PR summary draft: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
