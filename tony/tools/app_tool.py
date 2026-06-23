from __future__ import annotations

import subprocess
import webbrowser
from pathlib import Path


class AppTool:
    def open_vscode(self, folder: Path | str) -> str:
        try:
            subprocess.Popen(["code", str(Path(folder).resolve())])
            return f"Opening VS Code: {Path(folder).resolve()}"
        except FileNotFoundError:
            return "VS Code command 'code' is unavailable. Enable the VS Code command-line launcher."

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

    def open_app(self, app_name: str, workspace: Path | str) -> str:
        normalized = app_name.lower()
        if "code" in normalized:
            return self.open_vscode(workspace)
        if "explorer" in normalized or "file" in normalized:
            return self.open_file_explorer(workspace)
        if "terminal" in normalized or "powershell" in normalized:
            return self.open_terminal(workspace)
        if "notepad" in normalized:
            return self.open_notepad()
        if "calculator" in normalized or "calc" in normalized:
            return self.open_calculator()
        if "browser" in normalized or "chrome" in normalized:
            return self.open_browser()
        return f"Tony does not know how to safely open this app yet: {app_name}"
