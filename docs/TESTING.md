# Testing Tony AI

Tony's automated tests are designed to run without a real microphone, GitHub login, GPU, paid API, external website, or destructive command.

## Pytest

```powershell
python -m pytest tests
```

Coverage includes command normalization, intent routing, safety, assistant brain, voice setup fallbacks, wake phrase matching, project detection, Git/GitHub wrappers, workflow memory, vision safety, and UI smoke imports.

## Command Simulation

```powershell
python scripts/test_tony_commands.py
```

This runs representative typed commands through `AssistantBrain` in dry-run mode and saves:

```text
tony/logs/test_reports/command_test_report.md
```

## Voice Transcript Simulation

```powershell
python scripts/test_voice_transcripts.py
```

This simulates voice transcripts without microphone access and saves:

```text
tony/logs/test_reports/voice_transcript_test_report.md
```

## Manual Microphone Test

```powershell
python scripts/mic_test.py
```

The script lists input devices, records three seconds, saves `tony/logs/voice/mic_test.wav`, prints RMS audio level, and transcribes only if `faster-whisper` is installed.

## Health Check

```powershell
python scripts/health_check.py
```

The health check verifies Python, packages, config files, logs, database write access, Git, GitHub CLI, Ollama reachability, microphone availability, and test folder presence.
