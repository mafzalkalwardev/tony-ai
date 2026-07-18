from __future__ import annotations

import os
import subprocess
import webbrowser
from pathlib import Path


class AppTool:
    def open_vscode(self, folder: Path | str) -> str:
        target = str(Path(folder).resolve())
        # 1) Official CLI if installed
        try:
            subprocess.Popen(["code", target])
            return f"Opening VS Code: {target}"
        except (FileNotFoundError, OSError):
            pass

        # 2) Common Windows install locations
        home = Path.home()
        candidates = [
            home / "AppData/Local/Programs/Microsoft VS Code/Code.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Microsoft VS Code/Code.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Microsoft VS Code/Code.exe",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft VS Code/Code.exe",
        ]
        for exe in candidates:
            if exe and exe.is_file():
                subprocess.Popen([str(exe), target])
                return f"Opening VS Code: {target}"

        # 3) Start menu / app alias
        try:
            subprocess.Popen(["cmd", "/c", "start", "", "code", target], shell=True)
            return f"Opening VS Code via start: {target}"
        except Exception:
            pass

        return (
            "Couldn't find VS Code. Install it or enable the 'code' command-line launcher "
            "(VS Code → Command Palette → Shell Command: Install 'code' in PATH)."
        )
    def open_file_explorer(self, folder: Path | str) -> str:
        subprocess.Popen(["explorer", str(Path(folder).resolve())])
        return f"Opening File Explorer: {Path(folder).resolve()}"

    def open_terminal(self, folder: Path | str) -> str:
        try:
            subprocess.Popen(["wt", "-d", str(Path(folder).resolve())])
            return f"Opening Windows Terminal: {Path(folder).resolve()}"
        except FileNotFoundError:
            subprocess.Popen(["powershell", "-NoExit"], cwd=str(Path(folder).resolve()))
            return f"Opening PowerShell: {Path(folder).resolve()}"

    def open_notepad(self) -> str:
        subprocess.Popen(["notepad"])
        return "Opening Notepad."

    def open_calculator(self) -> str:
        subprocess.Popen(["calc"])
        return "Opening Calculator."

    def open_browser(self, url: str = "about:blank") -> str:
        webbrowser.open(url)
        return f"Opening browser: {url}"

    def open_edge(self, url: str | None = None) -> str:
        target = url or "about:blank"
        # Opens / focuses Microsoft Edge with a tab (uses existing Edge when possible)
        try:
            subprocess.Popen(["msedge", target], shell=False)
            return f"Opening in Microsoft Edge: {target}"
        except FileNotFoundError:
            subprocess.Popen(["cmd", "/c", "start", "", "msedge", target], shell=True)
            return f"Opening in Microsoft Edge: {target}"

    def open_chrome(self, url: str | None = None) -> str:
        target = url or "about:blank"
        try:
            subprocess.Popen(["chrome", target], shell=False)
            return f"Opening in Chrome: {target}"
        except FileNotFoundError:
            subprocess.Popen(["cmd", "/c", "start", "", "chrome", target], shell=True)
            return f"Opening Chrome: {target}"

    def open_url(self, url: str, prefer_edge: bool = True) -> str:
        if prefer_edge:
            return self.open_edge(url)
        return self.open_browser(url)

    def open_app(self, app_name: str, workspace: Path | str, url: str | None = None) -> str:
        normalized = (app_name or "").lower().strip()
        explicit_url = url

        if "youtube" in normalized:
            return self.open_edge(explicit_url or "https://www.youtube.com")
        if normalized in {"url", "link", "website"} and explicit_url:
            return self.open_edge(explicit_url)
        if explicit_url and explicit_url.startswith("http"):
            if "chrome" in normalized:
                return self.open_chrome(explicit_url)
            return self.open_edge(explicit_url)
        if "edge" in normalized:
            return self.open_edge(explicit_url)
        if "code" in normalized or normalized == "vscode":
            return self.open_vscode(workspace)
        if "explorer" in normalized or "file" in normalized:
            return self.open_file_explorer(workspace)
        if "terminal" in normalized or "powershell" in normalized:
            return self.open_terminal(workspace)
        if "notepad" in normalized:
            return self.open_notepad()
        if "calculator" in normalized or "calc" in normalized:
            return self.open_calculator()
        if "chrome" in normalized:
            return self.open_chrome(explicit_url)
        if "browser" in normalized:
            return self.open_browser(explicit_url or "about:blank")
        if "word" in normalized or "winword" in normalized:
            return self._start_cmd("winword", friendly="Microsoft Word")
        if "excel" in normalized:
            return self._start_cmd("excel", friendly="Excel")
        if "spotify" in normalized:
            return self._start_cmd("spotify:", friendly="Spotify")
        if "discord" in normalized:
            return self._start_cmd("discord:", friendly="Discord")
        # Generic: Windows Start / shell open by name
        return self._start_cmd(app_name)

    def _start_cmd(self, app_or_uri: str, friendly: str | None = None) -> str:
        name = str(app_or_uri or "").strip()
        if not name:
            return "No app name given."
        # Block obvious shell injection
        if any(c in name for c in ("&", "|", ";", ">", "<", "`", "$")):
            return f"Refused unsafe app name: {name}"
        try:
            subprocess.Popen(["cmd", "/c", "start", "", name], shell=True)
            label = friendly or name.rstrip(":")
            return f"Opening {label}."
        except Exception as exc:  # noqa: BLE001
            return f"Failed to launch {name}: {exc}"
