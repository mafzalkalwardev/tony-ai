from __future__ import annotations

import os
from pathlib import Path

from tony.core.memory import MemoryStore


class WorkspaceManager:
    def __init__(self, initial_path: Path | str, memory: MemoryStore) -> None:
        self.memory = memory
        self.current_path = Path(initial_path).resolve()
        self.validate_workspace(self.current_path)

    def set_workspace(self, path: Path | str) -> Path:
        target = Path(path).expanduser().resolve()
        self.validate_workspace(target)
        self.current_path = target
        self.memory.log_workspace(str(target), "active")
        return self.current_path

    def get_workspace(self) -> Path:
        return self.current_path

    def validate_workspace(self, path: Path | str) -> None:
        target = Path(path).expanduser().resolve()
        if not target.exists() or not target.is_dir():
            raise ValueError(f"Workspace folder does not exist: {target}")
        if self._is_blocked_workspace(target):
            raise ValueError(f"Blocked workspace path: {target}")

    def _is_blocked_workspace(self, path: Path) -> bool:
        system_root = Path(os.environ.get("SystemDrive", "C:") + "\\").resolve()
        blocked = {
            system_root,
            Path("C:/Windows").resolve(),
            Path("C:/Program Files").resolve(),
            Path("C:/Program Files (x86)").resolve(),
            Path.home().resolve(),
        }
        if path in blocked:
            return True
        system_markers = {"Windows", "System32", "pagefile.sys", "hiberfil.sys"}
        try:
            names = {child.name for child in path.iterdir()}
        except OSError:
            return True
        return bool(system_markers.intersection(names))
