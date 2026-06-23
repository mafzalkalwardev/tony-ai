from pathlib import Path

import pytest

from tony.core.memory import MemoryStore
from tony.core.workspace import WorkspaceManager


def test_workspace_accepts_existing_project_folder(tmp_path):
    manager = WorkspaceManager(tmp_path, MemoryStore(tmp_path / "memory.db"))

    assert manager.get_workspace() == tmp_path.resolve()


def test_workspace_rejects_missing_folder(tmp_path):
    manager = WorkspaceManager(tmp_path, MemoryStore(tmp_path / "memory.db"))

    with pytest.raises(ValueError):
        manager.set_workspace(tmp_path / "missing")
