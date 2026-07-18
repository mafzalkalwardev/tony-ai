# ULTRON + Tony

Personal AI assistant: Electron desktop shell + hybrid Node/Python brain.

## Quick start

```powershell
npm install
npm run live          # bridge + gateway + daemon
npm run ultron        # Electron app (starts stack if needed)
npm run test:agent
npm run test:ultron
```

HUD: http://localhost:8787/ · token `tony-dev-token`

## Stack

| Layer | Role |
|-------|------|
| **ULTRON (Electron)** | Desktop personal assistant window + tray |
| **Tony gateway** | ReAct brain, skills, chat, voice APIs |
| **Python bridge** | Desktop control (windows, type, click, screen) |
| **Obsidian vault** | Agentic Brain knowledge graph |
| **Voicebox** | Farman cloned voice (optional) |
| **Evolve daemon** | Idle self-improvement (XP + vault notes) |

## Skills

50+ catalog packs including **vibe coding**, taste engineering, pair flow, Ultron Personal OS, and self-evolution. New catalog skills auto-sync on boot.
