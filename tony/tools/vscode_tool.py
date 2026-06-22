from __future__ import annotations

from pathlib import Path

from tony.tools.shell_tool import ShellResult, ShellTool


class VSCodeTool:
    def __init__(self, shell: ShellTool) -> None:
        self.shell = shell

    def open_folder(self, folder: Path | str) -> ShellResult:
        path = Path(folder).resolve()
        result = self.shell.run(f'code "{path}"', path, require_safe=False)
        if result.exit_code != 0:
            return ShellResult(
                result.stdout,
                "VS Code command 'code' is unavailable. Install VS Code and enable the command-line launcher.",
                result.exit_code,
            )
        return result

