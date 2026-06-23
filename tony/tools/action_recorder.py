from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ActionRecorder:
    PRIVACY_WARNING = "Action recording may capture private information. Use only on safe screens."

    def __init__(self, output_dir: Path | str = "tony/logs/action_recordings") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.is_recording = False
        self.actions: list[dict] = []
        self.started_at = ""
        self._mouse_listener = None
        self._keyboard_listener = None
        self.last_recording_path: Path | None = None

    def start_recording(self, workspace: str = "") -> str:
        if self.is_recording:
            return "Action recording is already running."
        self.is_recording = True
        self.actions = []
        self.started_at = datetime.now().isoformat()
        self.workspace = workspace
        try:
            from pynput import keyboard, mouse
            self._mouse_listener = mouse.Listener(on_click=self._on_click)
            self._keyboard_listener = keyboard.Listener(on_press=self._on_key)
            self._mouse_listener.start()
            self._keyboard_listener.start()
        except Exception as exc:
            self.is_recording = False
            return f"Action recording unavailable: {exc}"
        return f"{self.PRIVACY_WARNING}\nAction recording started locally."

    def stop_recording(self) -> str:
        if not self.is_recording:
            return "No action recording is running."
        self.is_recording = False
        for listener in [self._mouse_listener, self._keyboard_listener]:
            try:
                if listener:
                    listener.stop()
            except Exception:
                pass
        stopped_at = datetime.now().isoformat()
        path = self.output_dir / f"actions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        payload = {
            "started_at": self.started_at,
            "stopped_at": stopped_at,
            "workspace": getattr(self, "workspace", ""),
            "actions": self.actions,
            "screenshots": [],
            "notes": self.PRIVACY_WARNING,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.last_recording_path = path
        return f"Action recording saved locally: {path.resolve()}"

    def pause(self) -> str:
        self.is_recording = False
        return "Action recording paused."

    def resume(self) -> str:
        self.is_recording = True
        return "Action recording resumed."

    def _on_click(self, x, y, button, pressed) -> None:
        if self.is_recording:
            self.actions.append({"type": "mouse_click", "x": x, "y": y, "button": str(button), "pressed": pressed, "time": datetime.now().isoformat()})

    def _on_key(self, key) -> None:
        if self.is_recording:
            text = str(key)
            if any(word in text.lower() for word in ["password", "secret", "token"]):
                return
            self.actions.append({"type": "key_press", "key": text, "time": datetime.now().isoformat()})

