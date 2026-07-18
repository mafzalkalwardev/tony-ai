# Hybrid Tony

## Phase status

- **Phase 1** — ReAct brain, Voicebox hooks, memory, Python bridge
- **Phase 2–3** — JARVIS HUD + desktop/vision tools
- **Phase 4** — Skills matrix (learn / install / idle XP), Obsidian brain, Command Deck UI

### Skills (44 catalog packs)

Grouped playbooks Tony uses as an encyclopedia + project manager + creative partner + laptop operator:

| Category | Examples |
|----------|----------|
| Core | info retrieval, translation, data analysis, writing, research |
| Cognitive | context awareness, learning preferences, problem solving |
| Human | empathy, debate/critical thinking, jokes |
| Creative | content creation, storytelling, visual imagination, cultural literacy |
| Laptop | voice commands, smart typing, navigation, files, desktop ops, vision |
| Productivity | workflows, email, scheduling, research summarization, task automation |
| Comfort | personalized shortcuts, adaptive habits, entertainment |
| Coding | polyglot, frameworks, full-stack, APIs, bugfix |
| Innovation | autonomous research, trends, self-updating knowledge, prototyping |
| Autonomy | self-learning, error correction, knowledge expansion, idle optimization |

- Teach custom skills via HUD **Teach Tony** or `learn_skill`
- New catalog skills auto-sync into `data/skills/installed.json` on boot
- Daemon idle-learns (~30m) → XP + vault notes under `vault/Agentic Brain/Skills/`
- APIs: `GET /api/skills`, `POST /api/skills/learn`, `POST /api/skills/install`, `POST /api/skills/install-all`, `POST /api/skills/idle`

## Run

```powershell
npm run live
```

Open http://localhost:8787/ (hard refresh after UI updates).

Default token: `tony-dev-token`
