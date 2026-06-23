import json

from pathlib import Path

import pytest

from tony.core.project_detector import ProjectDetector
from tony.core.workspace import WorkspaceManager
from tony.core.memory import MemoryStore


def test_detects_vite_react_project(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"dev": "vite", "test": "vitest"}, "dependencies": {"react": "latest", "vite": "latest"}}),
        encoding="utf-8",
    )

    detected = ProjectDetector().detect(tmp_path)

    assert detected.project_type == "react-vite"
    assert detected.recommended_run_command == "npm run dev"
    assert detected.recommended_test_command == "npm test"
    assert detected.package_manager == "npm"


def test_detects_tony_python_project(tmp_path):
    (tmp_path / "run_tony.py").write_text("print('hi')", encoding="utf-8")

    detected = ProjectDetector().detect(tmp_path)

    assert detected.project_type == "python"
    assert detected.recommended_run_command == "python run_tony.py"


def test_blocks_user_home_workspace():
    memory = MemoryStore(":memory:")

    with pytest.raises(ValueError):
        WorkspaceManager(Path.home(), memory)
