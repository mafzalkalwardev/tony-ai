from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from tony.core.safety import SafetyLevel, SafetySystem


@dataclass(frozen=True)
class ShellResult:
    stdout: str
    stderr: str
    exit_code: int

    def as_text(self) -> str:
        parts = []
        if self.stdout:
            parts.append(self.stdout.strip())
        if self.stderr:
            parts.append(f"STDERR:\n{self.stderr.strip()}")
        parts.append(f"Exit code: {self.exit_code}")
        return "\n\n".join(parts)


class ShellTool:
    def __init__(self, safety: SafetySystem, default_shell: str = "powershell") -> None:
        self.safety = safety
        self.default_shell = default_shell

    def run(self, command: str, cwd: Path | str, timeout: int = 60, require_safe: bool = True) -> ShellResult:
        if require_safe:
            decision = self.safety.classify(command, "run_shell_command")
            if decision.level == SafetyLevel.BLOCKED:
                return ShellResult("", f"Blocked: {decision.reason}", 1)

        shell_command = self._build_shell_command(command)
        try:
            completed = subprocess.run(
                shell_command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            return ShellResult(completed.stdout, completed.stderr, completed.returncode)
        except FileNotFoundError as exc:
            return ShellResult("", f"Command not found: {exc}", 127)
        except subprocess.TimeoutExpired:
            return ShellResult("", f"Command timed out after {timeout} seconds.", 124)

    def _build_shell_command(self, command: str) -> list[str]:
        if self.default_shell.lower() == "powershell":
            return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command]
        return ["cmd", "/c", command]

