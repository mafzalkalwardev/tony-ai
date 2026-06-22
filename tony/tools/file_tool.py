from __future__ import annotations

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

