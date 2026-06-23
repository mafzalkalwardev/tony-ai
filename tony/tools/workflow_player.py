from __future__ import annotations

import json
import time

from tony.core.workflow_memory import WorkflowMemory
from tony.tools.window_tool import WindowTool


class WorkflowPlayer:
    BLOCKED_ACTIONS = ("password", "payment", "bank", "send email", "send message", "submit", "delete", "format")

    def __init__(self, memory: WorkflowMemory | None = None, window_tool: WindowTool | None = None, speed: str = "normal") -> None:
        self.memory = memory or WorkflowMemory()
        self.window_tool = window_tool or WindowTool()
        self.speed = speed
        self.is_replaying = False

    def list_workflows(self) -> str:
        workflows = self.memory.list_workflows()
        if not workflows:
            return "No saved workflows yet."
        lines = ["Saved workflows:"]
        for item in workflows:
            lines.append(f"- {item['workflow_id']}: {item['name']} ({item.get('steps_count', 0)} steps)")
        return "\n".join(lines)

    def preview_workflow(self, workflow_id: int | None = None) -> str:
        workflow = self._get_workflow(workflow_id)
        if not workflow:
            return "No workflow found to preview."
        return f"I found this workflow. It has {len(workflow.get('steps', []))} steps.\nName: {workflow.get('name')}\nSafety: {workflow.get('safety_level')}"

    def dry_run_workflow(self, workflow_id: int | None = None) -> str:
        workflow = self._get_workflow(workflow_id)
        if not workflow:
            return "No workflow found for dry run."
        blocked = self._has_blocked_markers(workflow)
        return f"Dry run only. Workflow: {workflow.get('name')}. Steps: {len(workflow.get('steps', []))}. Blocked markers found: {blocked}."

    def replay_workflow(self, workflow_id: int | None = None) -> str:
        workflow = self._get_workflow(workflow_id)
        if not workflow:
            return "No workflow found to replay."
        if self.window_tool.check_if_sensitive_window():
            return "I blocked replay because the current screen may contain private information."
        if self._has_blocked_markers(workflow):
            return "I blocked replay because it contains risky actions."
        try:
            import pyautogui
        except ImportError:
            return "pyautogui is not installed. Workflow replay unavailable."
        pyautogui.FAILSAFE = True
        self.is_replaying = True
        for step in workflow.get("steps", []):
            if not self.is_replaying:
                break
            action_data = self._loads(step.get("action_data", "{}"))
            if step.get("action_type") == "mouse_click" and action_data.get("pressed"):
                pyautogui.click(action_data.get("x"), action_data.get("y"))
                time.sleep(0.05 if self.speed == "fast" else 0.15)
        self.is_replaying = False
        self.memory.log_run(int(workflow["workflow_id"]), "completed", "Replay completed.")
        return "Workflow replay completed."

    def stop_replay(self) -> str:
        self.is_replaying = False
        return "Workflow replay stopped."

    def _get_workflow(self, workflow_id: int | None) -> dict | None:
        if workflow_id is None:
            workflows = self.memory.list_workflows()
            if not workflows:
                return None
            workflow_id = int(workflows[0]["workflow_id"])
        return self.memory.get_workflow(int(workflow_id))

    def _has_blocked_markers(self, workflow: dict) -> bool:
        return any(marker in json.dumps(workflow).lower() for marker in self.BLOCKED_ACTIONS)

    def _loads(self, value: str) -> dict:
        try:
            return json.loads(value)
        except Exception:
            return {}
