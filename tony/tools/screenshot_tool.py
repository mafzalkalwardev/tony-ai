from __future__ import annotations

from datetime import datetime
from pathlib import Path


class ScreenshotTool:
    def __init__(self, output_dir: Path | str = "tony/logs/screenshots") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def take_screenshot(self) -> str:
        try:
            import pyautogui
        except ImportError:
            return "pyautogui is not installed. Install requirements.txt to enable screenshots."

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"screenshot_{timestamp}.png"
        try:
            image = pyautogui.screenshot()
            image.save(path)
            return f"Screenshot saved locally: {path.resolve()}"
        except Exception as exc:
            return f"Screenshot failed: {exc}"
