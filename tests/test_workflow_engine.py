from tony.core.workflow_engine import WorkflowEngine
from tony.tools.business_tool import BusinessTool
from tony.tools.report_generator import ReportGenerator
from tony.tools.task_planner import TaskPlanner


class FakeRepoAnalyzer:
    def generate_repo_summary(self, path):
        return "safe repo summary"


class FakeGitHub:
    def repo_view(self, path):
        class Result:
            def as_text(self):
                return "repo info"
        return Result()

    def generate_commit_message(self, status_text=""):
        return "chore: update project"


class Memory:
    def __init__(self):
        self.tasks = []

    def add_task(self, title, description="", priority="medium"):
        self.tasks.append((1, title, priority, "open"))
        return 1

    def list_tasks(self, status=None):
        return self.tasks

    def save_daily_plan(self, content):
        self.plan = content


def engine():
    return WorkflowEngine(FakeRepoAnalyzer(), BusinessTool(), ReportGenerator(), TaskPlanner(Memory()), FakeGitHub())


def test_analyze_workflow_safe():
    result = engine().analyze_project_workflow(".")
    assert result.requires_approval_steps == []
    assert "safe repo summary" in result.summary


def test_github_delivery_workflow_requires_approval_before_commit_push():
    result = engine().github_delivery_workflow(".")
    assert "git_commit" in result.requires_approval_steps
    assert "git_push" in result.requires_approval_steps


def test_client_update_workflow_creates_draft_only():
    result = engine().client_update_workflow("work completed")
    assert "Draft client message" in result.summary
    assert result.requires_approval_steps == []
