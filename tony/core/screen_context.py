from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from tony.core.workflow_memory import WorkflowMemory
from tony.tools.vision_tool import VisionTool


@dataclass
class ScreenContext:
    active_window_title: str = ""
    process_name: str = ""
    screenshot_path: str = ""
    timestamp: str = ""
    workspace_path: str = ""
    visible_text: str = ""
    safety_flags: list[str] = field(default_factory=list)
    notes: str = ""

    SENSITIVE_KEYWORDS = ("password", "secret", "token", "api key", "otp", "2fa", "bank", "payment", "card", ".env")

    def capture_context(self, vision_tool: VisionTool | None = None, workspace_path: str | Path = "") -> "ScreenContext":
        vision = vision_tool or VisionTool()
        data = vision.analyze_screenshot_basic()
        self.active_window_title = data.get("active_window_title", "")
        self.process_name = data.get("process_name", "")
        self.screenshot_path = data.get("screenshot_path", "")
        self.timestamp = datetime.now().isoformat()
        self.workspace_path = str(workspace_path or "")
        self.visible_text = data.get("visible_text", "")
        self.safety_flags = ["sensitive"] if data.get("sensitive") or self.is_sensitive() else []
        self.notes = data.get("note", "")
        return self

    def summarize_context(self) -> str:
        if self.is_sensitive():
            return "I stopped observing because this screen may contain private information."
        title = self.active_window_title or "unknown window"
        return f"Active window: {title}. Process: {self.process_name or 'unknown'}. Screenshot saved locally: {self.screenshot_path}."

    def is_sensitive(self) -> bool:
        blob = f"{self.active_window_title} {self.process_name} {self.visible_text}".lower()
        return any(keyword in blob for keyword in self.SENSITIVE_KEYWORDS) or "sensitive" in self.safety_flags

    def save_to_memory(self, memory: WorkflowMemory | None = None) -> None:
        store = memory or WorkflowMemory()
        store.save_screen_observation(
            {
                "active_window_title": self.active_window_title,
                "process_name": self.process_name,
                "screenshot_path": self.screenshot_path,
                "timestamp": self.timestamp,
                "workspace_path": self.workspace_path,
                "visible_text": self.visible_text,
                "safety_flags": self.safety_flags,
                "notes": self.notes,
            }
        )
