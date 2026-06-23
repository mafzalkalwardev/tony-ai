# Laptop Operator

Tony V3 adds careful local laptop and project tools. It does not randomly control the computer.

## What Tony Can Open

- VS Code
- File Explorer
- Windows Terminal or PowerShell
- Browser to localhost
- Notepad
- Calculator

## Workspace Safety

Tony works inside one active workspace. Use `Set Workspace` in the UI to choose a project folder.

Blocked workspace paths include:

- `C:\`
- `C:\Windows`
- `C:\Program Files`
- `C:\Program Files (x86)`
- The bare user home folder
- Folders containing system markers

## Project Runner

Tony detects common project types from files:

- Node.js from `package.json`
- React/Vite from dependencies or scripts
- Express from dependencies
- Python from `requirements.txt`, `pyproject.toml`, `main.py`, `app.py`, or `run_tony.py`
- Django from `manage.py`
- Flask from `app.py` or Flask dependency
- Git repo from `.git`

Tony recommends run and test commands. Running those commands requires approval.

## Browser Limits

Browser automation is disabled by default. Tony V3 can open localhost URLs. External URLs and browser automation require approval.

Tony V3 does not log in to websites, submit forms, scrape websites, or send messages.

## Screenshot Privacy

Screenshots require approval and are saved locally in `tony/logs/screenshots/`. Tony does not upload screenshots or OCR secrets.

## What Tony Cannot Do Automatically

- Delete important files or folders
- Read `.env` secrets
- Push to GitHub without approval
- Install dependencies without approval
- Disable antivirus or firewall
- Change passwords
- Make payments
- Send emails, SMS, calls, or bulk messages
