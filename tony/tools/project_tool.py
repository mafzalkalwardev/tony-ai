from __future__ import annotations

from pathlib import Path

from tony.core.project_detector import ProjectDetection, ProjectDetector
from tony.tools.git_tool import GitTool
from tony.tools.shell_tool import ShellResult, ShellTool


class ProjectTool:
    def __init__(self, detector: ProjectDetector, shell: ShellTool, git: GitTool, timeout_seconds: int = 120) -> None:
        self.detector = detector
        self.shell = shell
        self.git = git
        self.timeout_seconds = timeout_seconds

    def detect_project_type(self, path: Path | str) -> ProjectDetection:
        return self.detector.detect(path)

    def analyze_project(self, path: Path | str) -> str:
        root = Path(path).resolve()
        detection = self.detect_project_type(root)
        important = self._important_files(root)
        git_status = self.git.git_status(root).as_text()
        scripts = "\n".join(f"- {name}: {cmd}" for name, cmd in detection.scripts.items()) or "No package scripts detected."
        notes = "\n".join(f"- {note}" for note in detection.notes) or "- No notes."
        return (
            f"Workspace: {root}\n"
            f"Project type: {detection.project_type}\n"
            f"Package manager: {detection.package_manager or 'n/a'}\n"
            f"Recommended run: {detection.recommended_run_command or 'No safe run command detected.'}\n"
            f"Recommended tests: {detection.recommended_test_command or 'No test command detected.'}\n\n"
            f"Important files:\n{important}\n\n"
            f"Scripts:\n{scripts}\n\n"
            f"Notes:\n{notes}\n\n"
            f"Git status:\n{git_status}"
        )

    def show_project_summary(self, path: Path | str) -> str:
        return self.analyze_project(path)

    def run_project(self, path: Path | str) -> ShellResult:
        detection = self.detect_project_type(path)
        if not detection.recommended_run_command:
            return ShellResult("", "No recognized run command. Tony will not run unknown scripts automatically.", 1)
        return self.shell.run(detection.recommended_run_command, path, timeout=self.timeout_seconds, require_safe=False)

    def run_tests(self, path: Path | str) -> ShellResult:
        detection = self.detect_project_type(path)
        if not detection.recommended_test_command:
            return ShellResult("", "No recognized test command. Tony will not run unknown test scripts automatically.", 1)
        return self.shell.run(detection.recommended_test_command, path, timeout=self.timeout_seconds, require_safe=False)

    def install_dependencies(self, path: Path | str) -> ShellResult:
        detection = self.detect_project_type(path)
        if detection.package_manager in {"npm", "yarn", "pnpm"}:
            command = f"{detection.package_manager} install"
        elif detection.package_manager == "pip" or detection.project_type in {"python", "django", "flask"}:
            command = "pip install -r requirements.txt"
        else:
            return ShellResult("", "No known dependency install command detected.", 1)
        return self.shell.run(command, path, timeout=self.timeout_seconds, require_safe=False)

    def find_common_errors(self, output: str) -> list[str]:
        lowered = output.lower()
        errors = []
        for marker in ["traceback", "modulenotfounderror", "syntaxerror", "npm err", "enoent", "permission denied"]:
            if marker in lowered:
                errors.append(marker)
        return errors

    def _important_files(self, root: Path) -> str:
        names = [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "main.py",
            "app.py",
            "run_tony.py",
            "manage.py",
            "README.md",
        ]
        found = [name for name in names if (root / name).exists()]
        return "\n".join(f"- {name}" for name in found) if found else "- No common project files found."
