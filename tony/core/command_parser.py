from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedCommand:
    intent: str
    original_text: str
    argument: str = ""


class CommandParser:
    def parse(self, text: str) -> ParsedCommand:
        raw = text.strip()
        lowered = raw.lower()

        if not raw:
            return ParsedCommand("unknown", raw)

        if self._has_any(lowered, ["push", "push karo"]):
            return ParsedCommand("git_push", raw)

        if "commit" in lowered:
            return ParsedCommand("git_commit", raw, self._after_keyword(raw, "commit"))

        if "git diff" in lowered or ("repo" in lowered and "diff" in lowered):
            return ParsedCommand("git_diff", raw)

        if "status" in lowered and self._has_any(lowered, ["git", "repo", "github"]):
            return ParsedCommand("git_status", raw)

        if self._has_any(lowered, ["vs code", "vscode", "visual studio code"]) and self._has_any(lowered, ["khol", "kholo", "open"]):
            return ParsedCommand("open_vscode", raw)

        if self._has_any(lowered, ["folder", "directory"]) and self._has_any(lowered, ["khol", "kholo", "open"]):
            return ParsedCommand("open_folder", raw)

        if self._has_any(lowered, ["error check", "masla", "issue", "analyze", "analyse"]):
            return ParsedCommand("analyze_project", raw)

        if self._has_any(lowered, ["file banao", "create file", "nayi file", "new file"]):
            return ParsedCommand("create_file", raw)

        if self._has_any(lowered, ["read", "parho", "parhna", "file parho"]):
            return ParsedCommand("read_file", raw)

        if self._has_any(lowered, ["summarize", "summary", "khulasa"]):
            return ParsedCommand("summarize", raw)

        if self._has_any(lowered, ["run", "chalao", "start karo"]):
            return ParsedCommand("run_shell_command", raw, self._strip_tony_prefix(raw))

        return ParsedCommand("unknown", raw)

    def _has_any(self, text: str, terms: list[str]) -> bool:
        return any(term in text for term in terms)

    def _after_keyword(self, text: str, keyword: str) -> str:
        index = text.lower().find(keyword)
        if index == -1:
            return ""
        return text[index + len(keyword):].strip(" :\"'")

    def _strip_tony_prefix(self, text: str) -> str:
        cleaned = text.strip()
        for prefix in ["Tony,", "tony,", "Tony", "tony"]:
            if cleaned.startswith(prefix):
                return cleaned[len(prefix):].strip()
        return cleaned

