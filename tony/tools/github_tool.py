from __future__ import annotations

from pathlib import Path

from tony.tools.shell_tool import ShellResult, ShellTool


class GitHubTool:
    def __init__(self, shell: ShellTool) -> None:
        self.shell = shell

    def check_gh_installed(self, path: Path | str) -> ShellResult:
        result = self.shell.run("gh --version", path)
        if result.exit_code != 0:
            return ShellResult("", "GitHub CLI not found. Install gh or use normal Git commands.", result.exit_code)
        return result

    def gh_auth_status(self, path: Path | str) -> ShellResult:
        installed = self.check_gh_installed(path)
        if installed.exit_code != 0:
            return installed
        return self.shell.run("gh auth status", path)

    def list_repo_info(self, path: Path | str) -> ShellResult:
        installed = self.check_gh_installed(path)
        if installed.exit_code != 0:
            return installed
        return self.shell.run("gh repo view", path)

