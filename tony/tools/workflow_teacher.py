from __future__ import annotations

from datetime import datetime

from tony.core.workflow_memory import WorkflowMemory
from tony.tools.window_tool import WindowTool


class WorkflowTeacher:
    PRIVACY_WARNING = "Teaching mode may capture private information. Do not type passwords or private data."

    def __init__(self, memory: WorkflowMemory | None = None, window_tool: WindowTool | None = None, workspace: str = "") -> None:
        self.memory = memory or WorkflowMemory()
        self.window_tool = window_tool or WindowTool()
        self.workspace = workspace
        self.is_teaching = False
        self.workflow_id: int | None = None
        self.workflow_name = ""
        self.steps: list[dict] = []
        self.notes: list[str] = []

    def start_teaching(self, workflow_name: str = "Tony learned workflow") -> str:
        if self.is_teaching:
            return "Teaching mode is already on."
        title = self.window_tool.get_active_window_title()
        if self.window_tool.check_if_sensitive_window(title):
            return "I paused recording because this screen may contain private information."
        self.workflow_name = workflow_name or "Tony learned workflow"
        self.workflow_id = self.memory.create_workflow(self.workflow_name, self.PRIVACY_WARNING, self.workspace, "NEEDS_APPROVAL")
        self.steps = []
        self.notes = []
        self.is_teaching = True
        return f"Teaching mode is on. Show me the process slowly, and I'll remember the steps.\n{self.PRIVACY_WARNING}"

    def stop_teaching(self) -> str:
        if not self.is_teaching:
            return "Teaching mode is not running."
        self.is_teaching = False
        return f"I recorded {len(self.steps)} steps. Should I save this workflow?"

    def record_action(self, action: dict) -> str:
        if not self.is_teaching or self.workflow_id is None:
            return "Teaching mode is not running."
        blob = str(action).lower()
        if any(marker in blob for marker in WorkflowMemory.BLOCKED_MARKERS):
            return "I paused recording because this action may contain private information."
        title = self.window_tool.get_active_window_title()
        if self.window_tool.check_if_sensitive_window(title):
            return "I paused recording because this screen may contain private information."
        step = {"step": len(self.steps) + 1, "action": action, "time": datetime.now().isoformat(), "window_title": title}
        self.steps.append(step)
        self.memory.add_step(self.workflow_id, step["step"], action.get("type", "action"), action, title, notes="")
        return f"Recorded step {step['step']}."

    def add_note(self, note: str) -> str:
        if any(marker in note.lower() for marker in WorkflowMemory.BLOCKED_MARKERS):
            return "I did not save that note because it may contain private information."
        self.notes.append(note)
        return "Note added."

    def save_workflow(self) -> str:
        if self.workflow_id is None:
            self.workflow_id = self.memory.create_workflow(self.workflow_name or "Tony learned workflow", "Saved workflow", self.workspace, "SAFE")
        self.is_teaching = False
        return f"I saved this workflow. Next time you can say: Tony, run this workflow. Workflow ID: {self.workflow_id}"

    def summarize_workflow(self) -> str:
        if self.workflow_id is None:
            return "No workflow has been recorded yet."
        return f"Workflow {self.workflow_id}: {self.workflow_name}. Steps recorded: {len(self.steps)}."

    def discard_workflow(self) -> str:
        self.is_teaching = False
        self.workflow_id = None
        self.steps = []
        self.notes = []
        return "Workflow discarded."
