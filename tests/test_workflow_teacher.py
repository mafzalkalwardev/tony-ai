from tony.core.safety import SafetyLevel, SafetySystem
from tony.core.workflow_memory import WorkflowMemory
from tony.tools.workflow_teacher import WorkflowTeacher


class SafeWindow:
    def get_active_window_title(self):
        return "VS Code - tony-ai"

    def check_if_sensitive_window(self, title=None):
        return False


def test_start_teach_mode_needs_approval():
    decision = SafetySystem().classify("Tony watch me", "start_teach_mode")

    assert decision.level == SafetyLevel.NEEDS_APPROVAL


def test_stop_teach_mode_is_safe():
    decision = SafetySystem().classify("Tony stop teach mode", "stop_teach_mode")

    assert decision.level == SafetyLevel.SAFE


def test_workflow_save_works_without_secrets(tmp_path):
    memory = WorkflowMemory(tmp_path / "memory.db")
    teacher = WorkflowTeacher(memory=memory, window_tool=SafeWindow(), workspace=str(tmp_path))

    teacher.start_teaching("demo")
    teacher.record_action({"type": "mouse_click", "x": 1, "y": 2, "pressed": True})
    result = teacher.save_workflow()

    assert "Workflow ID" in result
    assert memory.list_workflows()[0]["steps_count"] == 1


def test_workflow_summary_generated(tmp_path):
    teacher = WorkflowTeacher(memory=WorkflowMemory(tmp_path / "memory.db"), window_tool=SafeWindow(), workspace=str(tmp_path))

    teacher.start_teaching("demo")
    summary = teacher.summarize_workflow()

    assert "Workflow" in summary
    assert "Steps recorded" in summary
