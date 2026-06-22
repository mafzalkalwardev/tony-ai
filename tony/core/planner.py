from __future__ import annotations

from tony.core.command_parser import ParsedCommand


class Planner:
    def describe_action(self, parsed: ParsedCommand) -> str:
        descriptions = {
            "open_vscode": "Open the current folder in VS Code.",
            "open_folder": "Open the current folder.",
            "run_shell_command": f"Run shell command: {parsed.argument or parsed.original_text}",
            "git_status": "Run git status.",
            "git_diff": "Show git diff.",
            "git_commit": "Create a git commit.",
            "git_push": "Push commits to the remote repository.",
            "analyze_project": "Check git status, recent log, and project files for obvious issues.",
            "create_file": "Create or edit a file.",
            "read_file": "Read a local file.",
            "summarize": "Summarize the provided text with the local Ollama model.",
            "unknown": "Ask the local Ollama model for help understanding the command.",
        }
        return descriptions.get(parsed.intent, "Handle user command.")

