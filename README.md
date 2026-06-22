# Tony AI Core v1

Tony is a free, local-first Windows laptop assistant for Muhammad Afzal. V1 is a typed desktop control center that can understand simple English, Urdu, Hindi, Roman Urdu, and Hinglish commands, run safe tools, use Git, open VS Code, call a local Ollama model, and keep local SQLite logs.

Official future wake phrase:

```text
Wake up Tony, Daddy's Home
```

## Features

- PyQt6 desktop UI named Tony AI Control Center
- Typed command input with chat-style output
- Push-to-talk voice input button
- Local faster-whisper speech-to-text foundation
- Local pyttsx3 text-to-speech startup greeting
- Rule-based mixed-language command parser
- Local Ollama integration at `http://localhost:11434`
- Safe shell execution through PowerShell
- Git status, diff, log, commit, and push helpers
- GitHub CLI detection and auth/repo helpers
- SQLite memory for commands, tasks, approvals, and project history
- Approval gate for risky actions
- Block list for destructive commands and secret exposure
- Wake phrase placeholder for later: `Wake up Tony, Daddy's Home`

## Setup

Install Python 3.11 or newer, then from this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install Ollama from https://ollama.com, then install the default local model:

```powershell
ollama pull qwen3:4b
```

Tony will still launch if Ollama is not running. It will show:

```text
Ollama is not running. Start Ollama and install a model, then try again.
```

Voice support is optional at runtime. If `faster-whisper`, `sounddevice`, `pyttsx3`, the microphone, or the local Whisper model is missing, Tony shows a helpful fallback message and keeps the text UI working.

## Run

```powershell
python run_tony.py
```

Startup message:

```text
Welcome back, Muhammad Afzal. Tony is online.
```

## Example Commands

```text
repo status dikhao
VS Code kholo
git diff dikhao
git push karo
rm -rf project
Tony, backend start karo
client ko professional English message likh do
```

For voice, click `Voice Input`, speak for the configured recording window, and Tony will show the recognized text before executing anything.

## Safety Notes

Tony does not use paid APIs, cloud AI APIs, private keys, or automatic messaging. It asks for approval before risky actions like `git push`, `git commit`, package installs, file editing, and unknown shell scripts. Voice commands go through the same safety checks as typed commands, and risky voice actions require typed or spoken `yes`.

## Roadmap

- V1: Text-first local desktop agent
- V2: Push-to-talk local voice foundation, wake phrase placeholder, STT, TTS
- V3: Laptop operator with careful app/window control
- V4: GitHub and business workflow automation
- V5: Advanced memory, routines, and multi-step workflows
