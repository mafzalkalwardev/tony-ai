<div align="center">

# TONY AI

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=28&duration=2800&pause=700&color=2563EB&center=true&vCenter=true&width=900&lines=Local+Voice-First+Windows+Assistant;Python+%2B+PyQt6+Desktop+Agent;Hands-free+laptop+control;Built+for+everyday+productivity" alt="Typing SVG" />

<p>
  <img src="https://komarev.com/ghpvc/?username=mafzalkalwardev&label=Project%20Views&color=2563eb&style=for-the-badge" alt="Project views" />
  <img src="https://img.shields.io/github/stars/mafzalkalwardev/tony-ai?style=for-the-badge&color=22c55e" alt="GitHub stars" />
  <img src="https://img.shields.io/github/forks/mafzalkalwardev/tony-ai?style=for-the-badge&color=f59e0b" alt="GitHub forks" />
  <img src="https://img.shields.io/github/license/mafzalkalwardev/tony-ai?style=for-the-badge&color=64748b" alt="License" />
</p>

<p>
  <img src="https://skillicons.dev/icons?i=python,qt,windows" alt="Skill icons" />
</p>

<p>
  <strong>Local voice-first Windows laptop assistant built with Python and PyQt6 for voice commands and desktop productivity.</strong>
</p>

</div>

---

## Contribution Snake

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake.svg">
    <img alt="Contribution snake" src="https://raw.githubusercontent.com/mafzalkalwardev/google-voice-dispatch-agent/output/github-contribution-grid-snake.svg">
  </picture>
</div>

---

## SEO Keywords

`voice assistant` `PyQt6` `Windows AI` `local agent`

---

## Overview

Tony AI is a free/local Windows laptop assistant with typed commands, push-to-talk voice, wake phrase architecture, project/Git tools, workflow memory, and approval-gated screen awareness. Tony works text-first even if voice dependencies, microphone access, OCR, or optional local AI tools are missing.

Tony does not use paid APIs and does not upload screenshots, recordings, secrets, or workflow memory.

## Features

- Clean PyQt6 assistant UI with command input, Push to Talk, Wake Mode, Stop, and Settings.
- Local speech-to-text foundation with `faster-whisper`, plus graceful fallback.
- Local text-to-speech with `pyttsx3`.
- Mixed English, Urdu, Hindi, Roman Urdu, and Hinglish command normalization.
- Shared `AssistantBrain` pipeline for text, voice, and wake transcripts.
- Safety levels: `SAFE`, `NEEDS_APPROVAL`, and `BLOCKED`.
- Git/project tools for status, diff, analysis, run/test recommendations, and local workflows.
- GitHub CLI helpers that work locally and handle missing `gh`.
- Business/report/prompt drafting only; Tony does not auto-send messages.
- V6 Vision Mode with approval-gated local screenshots.
- Observe Mode and Teach Mode, both approval-first and local-only.
- SQLite memory/logs under `tony/logs/`.
- Release QA scripts, health checks, command simulations, and CI workflow.

## Screenshots

| Dashboard | Voice Mode |
| --- | --- |
| ![Dashboard](docs/screenshots/dashboard.png) | ![Voice Mode](docs/screenshots/voice_mode.png) |

| Command Test | Voice Setup |
| --- | --- |
| ![Command Test](docs/screenshots/command_test.png) | ![Voice Setup](docs/screenshots/settings_voice_setup.png) |

## Demo Commands

```text
repo status dikhao
VS Code kholo
terminal kholo
project analyze karo
git push karo
rm -rf project
.env read karo
client message banao
Tony screen dekho
Tony watch me
Tony workflows dikhao
```

Wake phrases:

```text
Wake Up, Tony!
Wake up Tony, Daddy's Home
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Optional local model support:

```powershell
ollama pull qwen3:4b
```

Tony still launches when Ollama is not running.

## Running Tony

```powershell
python run_tony.py
```

Startup greeting:

```text
Welcome back, Muhammad Afzal. Tony is online.
```

## Voice Setup

Voice uses local/free tools:

- `sounddevice` for microphone recording
- `scipy` for WAV writing
- `faster-whisper` for speech-to-text
- `pyttsx3` for text-to-speech

Tony remains usable with typed commands if voice is unavailable. Use Settings -> Check Voice Setup, or run:

```powershell
python scripts/mic_test.py
python scripts/test_voice_transcripts.py
```

## Testing

```powershell
python -m pytest tests
python scripts/health_check.py
python scripts/test_tony_commands.py
python scripts/test_voice_transcripts.py
python scripts/prepare_release.py
python scripts/prepare_pr_summary.py
```

Reports are saved under:

```text
tony/logs/test_reports/
```

## Safety System

Tony asks approval before risky actions such as:

- `git push`, `git commit`, dependency installs
- running project scripts
- screenshots, observe mode, teach mode
- workflow replay, mouse/keyboard control
- GitHub write actions

Tony blocks dangerous/private actions such as:

- `rm -rf`, `del /s`, destructive file actions
- `.env`, API keys, tokens, secrets
- password/OTP/2FA recording
- banking/payment screens
- automatic email/message sending
- force push and reset hard

## Project Structure

```text
tony/
  core/      Assistant brain, safety, memory, workflow context
  tools/     Git, GitHub, project, business, screen, workflow tools
  ui/        PyQt6 desktop interface
  voice/     STT, TTS, wake phrase, voice setup
config/      Settings and permissions
docs/        Safety, commands, release, testing, vision, teach mode
scripts/     QA, release, mic, screenshots, asset generation
tests/       Automated pytest suite
```

## Roadmap

- V1: Text-first local desktop agent
- V2: Push-to-talk voice foundation
- V3: Laptop operator and project runner
- V4: Live voice architecture and local recorders
- V5: GitHub, business, reports, prompts, workflows
- V6: Vision Mode, Observe Mode, Teach Mode, workflow memory
- V7: Workflow editor, safer replay previews, packaged installer

## Release Notes

Current version: `1.0.0`

See [CHANGELOG.md](CHANGELOG.md) and [docs/RELEASE.md](docs/RELEASE.md).

## Contributing

Use real issues and pull requests only. Do not add features that bypass safety, approval, local-only storage, or secret handling rules.

## License

License is currently private/TBD. Add a formal license before public distribution.

## Credits

Built as Tony AI, a local-first Windows assistant for Muhammad Afzal.
