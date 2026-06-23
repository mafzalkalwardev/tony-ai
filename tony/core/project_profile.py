from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class ProjectProfile:
    def __init__(self, path: Path | str = "tony/logs/project_profiles.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save_profile(
        self,
        workspace: Path | str,
        project_name: str,
        project_type: str,
        repo_url: str = "",
        run_command: str = "",
        test_command: str = "",
        build_command: str = "",
        notes: str = "",
        common_issues: list[str] | None = None,
    ) -> str:
        profiles = self._load()
        key = str(Path(workspace).resolve())
        profiles[key] = {
            "project_name": project_name,
            "project_type": project_type,
            "repo_url": repo_url,
            "run_command": run_command,
            "test_command": test_command,
            "build_command": build_command,
            "notes": notes,
            "common_issues": common_issues or [],
            "last_analyzed_time": datetime.now().isoformat(),
        }
        self.path.write_text(json.dumps(profiles, indent=2), encoding="utf-8")
        return f"Project profile saved for {project_name}."

    def show_profile(self, workspace: Path | str) -> str:
        profile = self._load().get(str(Path(workspace).resolve()))
        if not profile:
            return "No project profile saved yet."
        return json.dumps(profile, indent=2)

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

