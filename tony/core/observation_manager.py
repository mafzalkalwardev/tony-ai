from __future__ import annotations

from tony.core.screen_context import ScreenContext
from tony.core.workflow_memory import WorkflowMemory
from tony.tools.vision_tool import VisionTool


class ObservationManager:
    def __init__(self, vision_tool: VisionTool | None = None, workflow_memory: WorkflowMemory | None = None, workspace_path: str = "") -> None:
        self.vision_tool = vision_tool or VisionTool()
        self.workflow_memory = workflow_memory or WorkflowMemory()
        self.workspace_path = workspace_path
        self.mode = "idle"
        self.observations: list[ScreenContext] = []

    def observe_once(self) -> str:
        self.mode = "observe_once"
        context = ScreenContext().capture_context(self.vision_tool, self.workspace_path)
        if context.is_sensitive():
            self.mode = "idle"
            return "I stopped observing because this screen may contain private information."
        context.save_to_memory(self.workflow_memory)
        self.observations.append(context)
        self.mode = "idle"
        return context.summarize_context()

    def start_observe_mode(self) -> str:
        self.mode = "observe_continuous"
        return "Observe Mode is on. Tony will capture low-frequency local screen context only after approval."

    def stop_observe_mode(self) -> str:
        self.mode = "idle"
        return "Observe Mode is off."

    def capture_periodic_context(self) -> str:
        if self.mode != "observe_continuous":
            return "Observe Mode is not running."
        return self.observe_once()

    def is_running(self) -> bool:
        return self.mode == "observe_continuous"
