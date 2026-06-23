from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tony.tools.window_tool import WindowTool


class VisionTool:
    SENSITIVE_TEXT = ("password", "secret", "api key", "token", "otp", "2fa", "bank", "payment", "card", ".env")

    def __init__(
        self,
        screenshot_dir: Path | str = "tony/logs/screenshots",
        window_tool: WindowTool | None = None,
        local_vision_provider: str = "none",
        ocr_enabled: bool = False,
    ) -> None:
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.window_tool = window_tool or WindowTool()
        self.local_vision_provider = local_vision_provider or "none"
        self.ocr_enabled = bool(ocr_enabled)

    def take_screenshot(self) -> str:
        return self.save_screenshot_locally()

    def save_screenshot_locally(self) -> str:
        path = self.screenshot_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
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
        return str(path.resolve())

    def analyze_screenshot_basic(self, screenshot_path: str = "") -> dict:
        path = screenshot_path or self.save_screenshot_locally()
        if path.startswith("Screen capture unavailable"):
            return {"ok": False, "error": path, "screenshot_path": ""}

        title = self.window_tool.get_active_window_title()
        process = self.window_tool.get_foreground_process()
        sensitive = self.window_tool.check_if_sensitive_window(title)
        width = height = 0
        try:
            from PIL import Image

            with Image.open(path) as image:
                width, height = image.size
        except Exception:
            pass
        visible_text = "" if sensitive else self.extract_visible_text_optional(path)
        visible_text = self.redact_sensitive_regions_basic(visible_text)
        return {
            "ok": True,
            "screenshot_path": path,
            "width": width,
            "height": height,
            "active_window_title": title,
            "process_name": process,
            "visible_text": visible_text,
            "sensitive": sensitive or self._looks_sensitive(visible_text),
            "advanced_vision": self.local_vision_provider != "none",
            "note": self._vision_note(),
        }

    def get_screen_summary(self) -> str:
        return self.describe_current_screen()

    def extract_visible_text_optional(self, screenshot_path: str) -> str:
        if not self.ocr_enabled:
            return ""
        try:
            import pytesseract
            from PIL import Image

            text = pytesseract.image_to_string(Image.open(screenshot_path))
            return "" if self._looks_sensitive(text) else text.strip()
        except Exception:
            return ""

    def redact_sensitive_regions_basic(self, text: str) -> str:
        redacted = text or ""
        for marker in self.SENSITIVE_TEXT:
            redacted = redacted.replace(marker, "[redacted]")
            redacted = redacted.replace(marker.upper(), "[redacted]")
            redacted = redacted.replace(marker.title(), "[redacted]")
        return redacted

    def describe_current_screen(self) -> str:
        data = self.analyze_screenshot_basic()
        if not data.get("ok"):
            return data.get("error", "Screen capture unavailable.")
        if data.get("sensitive"):
            return "I cannot analyze password, payment, banking, secret, or private screens."
        title = data.get("active_window_title") or "unknown window"
        path = data.get("screenshot_path")
        size = f"{data.get('width', 0)}x{data.get('height', 0)}"
        note = data.get("note", "")
        return f"Here is what I can see safely: active window is {title}, screenshot size is {size}, and the screenshot was saved locally: {path}. {note}".strip()

    def _vision_note(self) -> str:
        if self.local_vision_provider == "none":
            return "I can capture the screen and basic window context, but advanced visual understanding is not configured yet."
        return "Local vision analysis is configured."

    def _looks_sensitive(self, text: str) -> bool:
        lowered = (text or "").lower()
        return any(marker in lowered for marker in self.SENSITIVE_TEXT)
