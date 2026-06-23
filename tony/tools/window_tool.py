from __future__ import annotations

import subprocess


class WindowTool:
    SENSITIVE_KEYWORDS = (
        "bank",
        "payment",
        "paypal",
        "stripe",
        "card",
        "password",
        "1password",
        "bitwarden",
        "authenticator",
        "otp",
        "2fa",
        "login",
        "compose",
        "whatsapp",
        "telegram",
        ".env",
        "secret",
        "token",
    )

    def get_active_window_title(self) -> str:
        try:
            import pygetwindow as gw

            window = gw.getActiveWindow()
            return window.title if window and window.title else ""
        except Exception:
            return self._powershell_active_window_title()

    def list_open_windows(self) -> list[str]:
        try:
            import pygetwindow as gw

            return [title for title in gw.getAllTitles() if title]
        except Exception:
            return []

    def get_foreground_process(self) -> str:
        title = self.get_active_window_title()
        if not title:
            return ""
        try:
            import psutil

            lowered = title.lower()
            for proc in psutil.process_iter(["name"]):
                name = proc.info.get("name") or ""
                if name and name.lower().replace(".exe", "") in lowered:
                    return name
        except Exception:
            pass
        return ""

    def check_if_sensitive_window(self, title: str | None = None) -> bool:
        text = (title if title is not None else self.get_active_window_title()).lower()
        return any(keyword in text for keyword in self.SENSITIVE_KEYWORDS)

    def focus_window(self, title: str) -> str:
        if not title:
            return "Tell Tony which window to focus."
        try:
            import pygetwindow as gw

            matches = gw.getWindowsWithTitle(title)
            if not matches:
                return f"No open window matched: {title}"
            matches[0].activate()
            return f"Focused window: {matches[0].title}"
        except Exception as exc:
            return f"Window focus unavailable: {exc}"

    def open_app_safe(self, app_name: str) -> str:
        allowed = {"notepad": "notepad", "calculator": "calc", "calc": "calc"}
        command = allowed.get(app_name.lower().strip())
        if not command:
            return "That app is not on Tony's safe app list yet."
        try:
            subprocess.Popen([command], shell=False)
            return f"Opening {app_name}."
        except Exception as exc:
            return f"Could not open {app_name}: {exc}"

    def _powershell_active_window_title(self) -> str:
        command = (
            "Add-Type @'\n"
            "using System;\nusing System.Runtime.InteropServices;\nusing System.Text;\n"
            "public class W { [DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow();"
            "[DllImport(\"user32.dll\")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count); }\n"
            "'@; $b=New-Object Text.StringBuilder 512; [void][W]::GetWindowText([W]::GetForegroundWindow(), $b, $b.Capacity); $b.ToString()"
        )
        try:
            result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, timeout=3)
            return result.stdout.strip()
        except Exception:
            return ""
