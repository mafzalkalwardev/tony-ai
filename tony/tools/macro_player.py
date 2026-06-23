from __future__ import annotations

import json
import time
from pathlib import Path


class MacroPlayer:
    BLOCKED_MARKERS = ["password", "payment", "bank", "send email", "send message", "delete", "format"]

    def __init__(self) -> None:
        self.last_loaded: dict | None = None

    def load_recorded_macro(self, path: Path | str) -> dict:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.last_loaded = data
        return data

    def preview_macro_summary(self, path: Path | str) -> str:
        data = self.load_recorded_macro(path)
        actions = data.get("actions", [])
        blocked = self._has_blocked_markers(data)
        return f"Macro actions: {len(actions)}\nWorkspace: {data.get('workspace', '')}\nBlocked markers found: {blocked}"

    def replay(self, path: Path | str) -> str:
        data = self.load_recorded_macro(path)
        if self._has_blocked_markers(data):
            return "Macro replay blocked because it may include sensitive or destructive actions."
        try:
            import pyautogui
        except ImportError:
            return "pyautogui is not installed. Macro replay unavailable."
        pyautogui.FAILSAFE = True
        for action in data.get("actions", []):
            if action.get("type") == "mouse_click" and action.get("pressed"):
                pyautogui.click(action.get("x"), action.get("y"))
                time.sleep(0.05)
        return "Macro replay completed."

    def _has_blocked_markers(self, data: dict) -> bool:
        blob = json.dumps(data).lower()
        return any(marker in blob for marker in self.BLOCKED_MARKERS)
