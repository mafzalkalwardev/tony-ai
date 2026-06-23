from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkflowResult:
    name: str
    summary: str
    requires_approval_steps: list[str]


class WorkflowEngine:
    def __init__(self, repo_analyzer, business_tool, report_generator, task_planner, github_operator) -> None:
        self.repo_analyzer = repo_analyzer
        self.business_tool = business_tool
        self.report_generator = report_generator
        self.task_planner = task_planner
        self.github_operator = github_operator

    def analyze_project_workflow(self, path: Path | str) -> WorkflowResult:
        summary = self.repo_analyzer.generate_repo_summary(path)
        return WorkflowResult("Analyze Project", summary, [])

    def debug_project_workflow(self, path: Path | str) -> WorkflowResult:
        summary = self.repo_analyzer.generate_repo_summary(path)
        return WorkflowResult("Debug Project", summary + "\n\nNext risky step: run tests/project after approval.", ["run_tests", "run_project", "apply_fix"])

    def github_delivery_workflow(self, path: Path | str) -> WorkflowResult:
        status = self.github_operator.repo_view(path).as_text()
        msg = self.github_operator.generate_commit_message(status)
        note = self.business_tool.generate_delivery_note("GitHub delivery draft prepared locally.")
        return WorkflowResult("GitHub Delivery", f"Commit message draft: {msg}\n\n{note}", ["git_commit", "git_push", "create_pr"])

    def client_update_workflow(self, context: str) -> WorkflowResult:
        draft = self.business_tool.generate_client_message(context)
        return WorkflowResult("Client Update", draft, [])

    def daily_work_workflow(self) -> WorkflowResult:
        plan = self.task_planner.create_daily_plan()
        report = self.report_generator.generate_daily_work_report()
        return WorkflowResult("Daily Work", f"{plan}\n\n{report}", [])

    def run_workflow(self, name: str, path: Path | str, context: str = "") -> WorkflowResult:
        lowered = name.lower()
        if "debug" in lowered:
            return self.debug_project_workflow(path)
        if "github" in lowered or "delivery" in lowered:
            return self.github_delivery_workflow(path)
        if "client" in lowered:
            return self.client_update_workflow(context or "project work update")
        if "daily" in lowered:
            return self.daily_work_workflow()
        return self.analyze_project_workflow(path)
