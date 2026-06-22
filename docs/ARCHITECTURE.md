# Architecture

Tony Core v1 is intentionally small and modular.

## Entry Point

- `run_tony.py` starts the PyQt6 app.
- `tony/app.py` creates the Qt application and main window.

## UI

- `tony/ui/main_window.py` owns the desktop control center.
- `tony/ui/styles.qss` contains the dark theme.
- Long-running work uses `AgentWorker`, `VoiceWorker`, and `QThreadPool` so the UI stays responsive.

## Core

- `agent.py` coordinates parsing, safety, tools, memory, and Ollama.
- `command_parser.py` maps mixed-language typed commands to intents.
- `safety.py` classifies commands as `SAFE`, `NEEDS_APPROVAL`, or `BLOCKED`.
- `planner.py` turns intents into human-readable planned actions.
- `task_runner.py` runs agent work in the background for the UI.
- `ollama_client.py` talks to the local Ollama API and handles offline errors.
- `memory.py` stores conversations, tasks, approvals, and project history in SQLite.

## Tools

- `shell_tool.py` runs PowerShell commands with timeout and captured output.
- `git_tool.py` wraps common Git commands.
- `github_tool.py` uses the free GitHub CLI `gh`.
- `vscode_tool.py` opens folders with the `code` command.
- `file_tool.py` supports local file read/create primitives with secret protection.
- `browser_tool.py` is a placeholder for later browser automation.

## Voice

`tony/voice/` contains the V2 voice foundation:

- `stt.py` records a short microphone clip and transcribes it with local faster-whisper.
- `tts.py` speaks the startup greeting with pyttsx3 when available.
- `wake_word.py` stores the official wake phrase placeholder.

Always-listening wake word mode is intentionally not enabled yet.
