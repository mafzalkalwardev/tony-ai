from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProjectDetection:
    project_type: str
    recommended_run_command: str
    recommended_test_command: str
    package_manager: str
    notes: list[str] = field(default_factory=list)
    scripts: dict[str, str] = field(default_factory=dict)
    is_git_repo: bool = False


class ProjectDetector:
    def detect(self, path: Path | str) -> ProjectDetection:
        root = Path(path).resolve()
        package_json = self._read_package_json(root / "package.json")
        scripts = package_json.get("scripts", {}) if package_json else {}
        dependencies = self._package_dependencies(package_json)
        notes: list[str] = []
        is_git_repo = (root / ".git").exists()

        if package_json:
            package_manager = self._detect_package_manager(root)
            project_type = "node"
            run_command = self._node_run_command(scripts, package_manager)
            test_command = self._node_test_command(scripts, package_manager)

            if "vite" in dependencies or "react" in dependencies:
                project_type = "react-vite" if "vite" in dependencies else "react"
                notes.append("Detected React/Vite-related dependencies.")
            if "express" in dependencies:
                project_type = "express"
                notes.append("Detected Express dependency.")

            if is_git_repo:
                notes.append("Git repository detected.")
            return ProjectDetection(project_type, run_command, test_command, package_manager, notes, scripts, is_git_repo)

        if (root / "manage.py").exists():
            notes.append("Django manage.py detected.")
            return ProjectDetection("django", "python manage.py runserver", "python manage.py test", "pip", notes, {}, is_git_repo)

        if self._is_flask(root):
            notes.append("Flask app or dependency detected.")
            return ProjectDetection("flask", "python app.py", "python -m pytest", "pip", notes, {}, is_git_repo)

        python_run = self._python_run_command(root)
        if python_run:
            notes.append("Python project files detected.")
            if is_git_repo:
                notes.append("Git repository detected.")
            return ProjectDetection("python", python_run, "python -m pytest", "pip", notes, {}, is_git_repo)

        if is_git_repo:
            return ProjectDetection("git-repo", "", "", "", ["Git repository detected."], {}, True)

        return ProjectDetection("unknown", "", "", "", ["No known project markers found."], {}, False)

    def _read_package_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _package_dependencies(self, package_json: dict[str, Any]) -> set[str]:
        deps = set(package_json.get("dependencies", {}).keys())
        deps.update(package_json.get("devDependencies", {}).keys())
        return deps

    def _detect_package_manager(self, root: Path) -> str:
        if (root / "pnpm-lock.yaml").exists():
            return "pnpm"
        if (root / "yarn.lock").exists():
            return "yarn"
        return "npm"

    def _node_run_command(self, scripts: dict[str, str], package_manager: str) -> str:
        for script in ["dev", "start", "serve"]:
            if script in scripts:
                return f"{package_manager} run {script}" if script != "start" else f"{package_manager} start"
        return ""

    def _node_test_command(self, scripts: dict[str, str], package_manager: str) -> str:
        if "test" in scripts:
            return f"{package_manager} test"
        return ""

    def _is_flask(self, root: Path) -> bool:
        if (root / "app.py").exists():
            return True
        requirements = root / "requirements.txt"
        if requirements.exists():
            try:
                return "flask" in requirements.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                return False
        return False

    def _python_run_command(self, root: Path) -> str:
        for filename in ["run_tony.py", "main.py", "app.py"]:
            if (root / filename).exists():
                return f"python {filename}"
        if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
            return ""
        return ""
