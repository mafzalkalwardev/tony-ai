from __future__ import annotations

from datetime import datetime
from pathlib import Path


class ScreenRecorder:
    def __init__(self, output_dir: Path | str = "tony/logs/screen_recordings", fps: int = 1) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = max(1, int(fps))
        self.is_recording = False
        self.frames: list[Path] = []
        self.session_dir: Path | None = None

    def start_recording(self) -> str:
        if self.is_recording:
            return "Screen recording is already running."
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"screen_{timestamp}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.frames = []
        self.is_recording = True
        path = self.take_screenshot()
        return f"Screen recording started locally: {self.session_dir}\nFirst frame: {path}"

    def stop_recording(self) -> str:
        if not self.is_recording:
            return "No screen recording is running."
        self.is_recording = False
        return f"Screen recording stopped. Frames saved: {len(self.frames)} in {self.session_dir}"

    def take_screenshot(self) -> str:
        target_dir = self.session_dir or self.output_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = target_dir / f"frame_{timestamp}.png"
        try:
            import mss
            import mss.tools
            with mss.mss() as sct:
                monitor = sct.monitors[0]
                shot = sct.grab(monitor)
                mss.tools.to_png(shot.rgb, shot.size, output=str(path))
        except Exception:
            try:
                import pyautogui
                image = pyautogui.screenshot()
                image.save(path)
            except Exception as exc:
                return f"Screen capture unavailable: {exc}"
        self.frames.append(path)
        return str(path.resolve())

