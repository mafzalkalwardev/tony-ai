# TONY

Personal AI assistant: Electron desktop shell + hybrid Node/Python brain.

## Quick start

```powershell
npm install
npm run live          # bridge + gateway + daemon
npm run tony          # Electron desktop app
npm run test:agent
npm run test:ultron
```

HUD: http://localhost:8787/ · token `tony-dev-token`

## Voice (Farman)

- Uses Voicebox `/generate` with **personality** + emotion **instruct** (not flat TTS)
- Auto tone: greeting / warm / sad / urgent / playful
- **Stop** cancels browser speech, Farman WAV, and queued generations

## Stack

| Layer | Role |
|-------|------|
| **TONY (Electron)** | Desktop personal assistant window + tray |
| **Gateway** | ReAct brain, skills, chat, voice APIs |
| **Python bridge** | Desktop control |
| **Obsidian vault** | Agentic Brain knowledge graph |
| **Voicebox** | Farman cloned voice |
| **Evolve daemon** | Idle self-improvement |
