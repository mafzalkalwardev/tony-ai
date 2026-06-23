# Roadmap

## V1: Text Agent

- PyQt6 desktop UI
- Typed commands
- Local Ollama brain
- Git and shell tools
- Safety approval system
- SQLite memory and logs

## V2: Voice Foundation (Current)

- Push-to-talk voice input
- Local faster-whisper speech-to-text
- Local pyttsx3 text-to-speech startup greeting
- Graceful microphone/model fallback
- Wake phrase: `Wake up Tony, Daddy's Home`
- Always-listening wake phrase detection later

## V3: Laptop Operator And Project Runner (Current)

- Workspace selection and validation
- Project detection and command recommendations
- Safe app opening
- Localhost browser helper
- Screenshot helper with approval
- Explicit permission before project runs, installs, screenshots, typing, or browser automation

## V4: Live Voice And Recorder Foundation (Current)

- Optional live voice mode, off by default
- Wake phrases: `Wake Up, Tony!` and `Wake up Tony, Daddy's Home`
- Wake phrase fallback architecture when openwakeword is unavailable
- Audio waveform UI
- Local screen recording frames
- Local action recording JSON
- Macro replay with approval
- Strong privacy blocks for passwords, payments, secrets, and automatic messages

## V5: GitHub, Business, And Coding Workflows (Current)

- GitHub CLI workflows
- PR summaries and issue triage
- Client message drafting
- Business task checklists
- No automatic sending without approval
- Repo/code analysis
- Local reports and daily plans
- Prompt generation for coding tools
- Safe step-by-step workflows

## V6: Vision, Observe, Teach, And Workflow Memory (Current)

- Approval-gated local screen capture
- Basic safe screen/window context
- Observe Mode, off by default
- Teach Mode for local workflow learning
- SQLite workflow memory
- Workflow list, preview, dry run, and approval-gated replay
- Sensitive-screen detection and privacy blocks
