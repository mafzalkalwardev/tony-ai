from __future__ import annotations

import json
from pathlib import Path

from tony.core.project_detector import ProjectDetector
from tony.tools.git_tool import GitTool


class RepoAnalyzer:
    IGNORED_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", "uploads", "logs"}
    SAFE_SUFFIXES = {".md", ".txt", ".py", ".json", ".toml", ".yml", ".yaml", ".js", ".ts", ".tsx", ".jsx"}
    SECRET_MARKERS = {"api_key", "secret", "token", "password", "private_key"}

    def __init__(self, detector: ProjectDetector, git: GitTool) -> None:
        self.detector = detector
        self.git = git

    def analyze_repo(self, path: Path | str) -> str:
        return self.generate_repo_summary(path)

    def detect_project_type(self, path: Path | str) -> str:
        return self.detector.detect(path).project_type

    def list_important_files(self, path: Path | str) -> list[str]:
        root = Path(path)
        important = []
        for name in ["README.md", "package.json", "requirements.txt", "pyproject.toml", "run_tony.py", "main.py", "app.py", "manage.py"]:
            if (root / name).exists():
                important.append(name)
        return important

    def read_safe_files(self, path: Path | str, limit: int = 5) -> dict[str, str]:
        root = Path(path)
        safe: dict[str, str] = {}
        for file in root.rglob("*"):
            if len(safe) >= limit:
                break
            if not file.is_file() or self._is_ignored(file) or file.name.lower().startswith(".env"):
                continue
            if file.suffix.lower() not in self.SAFE_SUFFIXES:
                continue
            text = file.read_text(encoding="utf-8", errors="replace")[:2000]
            if self._looks_secret(text):
                continue
            safe[str(file.relative_to(root))] = text
        return safe

    def detect_package_scripts(self, path: Path | str) -> dict[str, str]:
        package = Path(path) / "package.json"
        if not package.exists():
            return {}
        try:
            return json.loads(package.read_text(encoding="utf-8")).get("scripts", {})
        except (json.JSONDecodeError, OSError):
            return {}

    def detect_test_commands(self, path: Path | str) -> list[str]:
        detected = self.detector.detect(path)
        return [detected.recommended_test_command] if detected.recommended_test_command else []

    def detect_build_commands(self, path: Path | str) -> list[str]:
        scripts = self.detect_package_scripts(path)
        return ["npm run build"] if "build" in scripts else []

    def detect_git_status(self, path: Path | str) -> str:
        return self.git.git_status(path).as_text()

    def detect_recent_commits(self, path: Path | str) -> str:
        return self.git.git_log(path, limit=5).as_text()

    def detect_common_problems(self, path: Path | str) -> list[str]:
        problems = []
        root = Path(path)
        if not (root / "README.md").exists():
            problems.append("README.md is missing.")
        if (root / "package.json").exists() and not (root / "package-lock.json").exists():
            problems.append("Node project has no package-lock.json.")
        if (root / "requirements.txt").exists() and not self.detect_test_commands(root):
            problems.append("Python test command was not detected.")
        return problems

    def generate_repo_summary(self, path: Path | str) -> str:
        root = Path(path).resolve()
        detected = self.detector.detect(root)
        scripts = self.detect_package_scripts(root)
        problems = self.detect_common_problems(root)
        return (
            f"# Repo Summary\n\n"
            f"Project: {root.name}\n"
            f"Project type: {detected.project_type}\n"
            f"Main language: {self._main_language(detected.project_type)}\n"
            f"Important files: {', '.join(self.list_important_files(root)) or 'none detected'}\n"
            f"Run command: {detected.recommended_run_command or 'n/a'}\n"
            f"Test command: {detected.recommended_test_command or 'n/a'}\n"
            f"Build command: {', '.join(self.detect_build_commands(root)) or 'n/a'}\n"
            f"Package scripts: {scripts or 'none'}\n\n"
            f"Git status:\n{self.detect_git_status(root)}\n\n"
            f"Possible issues:\n" + "\n".join(f"- {p}" for p in problems or ["No common problems detected."]) + "\n\n"
            f"Recommended next steps:\n- Review Git status\n- Run tests before delivery\n- Generate a client-safe delivery report"
        )

    def _main_language(self, project_type: str) -> str:
        if project_type in {"python", "django", "flask"}:
            return "Python"
        if project_type in {"node", "react", "react-vite", "express"}:
            return "JavaScript/TypeScript"
        return "Unknown"

    def _is_ignored(self, file: Path) -> bool:
        return any(part in self.IGNORED_DIRS for part in file.parts)

    def _looks_secret(self, text: str) -> bool:
        lowered = text.lower()
        return any(marker in lowered for marker in self.SECRET_MARKERS)

