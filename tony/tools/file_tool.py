from __future__ import annotations

import shutil
from pathlib import Path


class FileTool:
    def read_file(self, path: Path | str) -> str:
        target = Path(path)
        if ".env" in target.name.lower():
            return "Blocked: Tony will not read .env files or secrets."
        if not target.exists():
            return f"File not found: {target}"
        return target.read_text(encoding="utf-8", errors="replace")

    def create_file(self, path: Path | str, content: str = "") -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Created file: {target}"

    def copy_file(self, src: Path | str, dest: Path | str) -> str:
        source = Path(src).expanduser()
        target = Path(dest).expanduser()
        if not source.exists():
            return f"Source not found: {source}"
        if any(x in source.name.lower() for x in (".env", "credential", "secret", "password")):
            return "Blocked: won't copy secret-looking files."
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            if target.is_dir():
                target = target / source.name
            shutil.copy2(source, target)
        return f"Copied {source} → {target}"

    def move_file(self, src: Path | str, dest: Path | str) -> str:
        source = Path(src).expanduser()
        target = Path(dest).expanduser()
        if not source.exists():
            return f"Source not found: {source}"
        if any(x in source.name.lower() for x in (".env", "credential", "secret", "password")):
            return "Blocked: won't move secret-looking files."
        # If dest looks like a folder (no suffix / ends with sep / exists as dir), move into it
        if str(dest).endswith(("/", "\\")) or (not target.suffix and not target.exists()) or target.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            target = target / source.name
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        return f"Moved {source} → {target}"
