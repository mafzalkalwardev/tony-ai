from __future__ import annotations

from datetime import datetime
from pathlib import Path


class ReportGenerator:
    def __init__(self, output_dir: Path | str = "tony/logs/reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_work_report(self) -> str:
        return self._report("Daily Work Report", "Summary of today's completed work, issues, commands, and next steps.")

    def generate_project_delivery_report(self, path: Path | str) -> str:
        return self._report("Project Delivery Report", f"Project: {Path(path).resolve()}\nWork done:\n- Implementation updates\n- Safety checks\n- Tests")

    def generate_repo_analysis_report(self, path: Path | str) -> str:
        return self._report("Repo Analysis Report", f"Project: {Path(path).resolve()}\nSummary: repository analyzed locally.")

    def generate_bug_fix_report(self, error: str, fix: str) -> str:
        return self._report("Bug Fix Report", f"Problem:\n{error}\n\nFix/Suggestion:\n{fix}")

    def generate_testing_report(self, test_output: str) -> str:
        return self._report("Testing Report", f"Test output:\n{test_output}")

    def save_report_markdown(self, title: str, content: str) -> str:
        path = self.output_dir / f"{self._slug(title)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        path.write_text(content, encoding="utf-8")
        return str(path.resolve())

    def export_report_txt(self, title: str, content: str) -> str:
        path = self.output_dir / f"{self._slug(title)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path.write_text(content, encoding="utf-8")
        return str(path.resolve())

    def _report(self, title: str, body: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"# {title}\n\nDate/time: {now}\n\n## Summary\n{body}\n\n## Problems Found\n- Review details above\n\n## Next Steps\n- Confirm scope\n- Run tests\n- Share draft if needed"

    def _slug(self, title: str) -> str:
        return "_".join(title.lower().split())

