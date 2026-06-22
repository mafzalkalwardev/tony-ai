from __future__ import annotations

from pathlib import Path

from tony.tools.shell_tool import ShellResult, ShellTool


class GitTool:
    def __init__(self, shell: ShellTool) -> None:
        self.shell = shell

    def git_status(self, path: Path | str) -> ShellResult:
        return self.shell.run("git status --short", path)

    def git_diff(self, path: Path | str) -> ShellResult:
        return self.shell.run("git diff", path)

    def git_log(self, path: Path | str, limit: int = 5) -> ShellResult:
        return self.shell.run(f"git log --oneline -n {limit}", path)

    def git_add(self, path: Path | str, files: list[str]) -> ShellResult:
        safe_files = " ".join(f'"{file}"' for file in files)
        return self.shell.run(f"git add {safe_files}", path, require_safe=False)

    def git_commit(self, path: Path | str, message: str) -> ShellResult:
        escaped = message.replace('"', '\\"') or "Tony update"
        return self.shell.run(f'git commit -m "{escaped}"', path, require_safe=False)

    def git_push(self, path: Path | str) -> ShellResult:
        return self.shell.run("git push", path, require_safe=False)

