"use strict";

const fs = require("fs");
const path = require("path");
const { config } = require("../config");

/**
 * Skill catalog — encyclopedia + project manager + creative partner + laptop operator.
 * New catalog entries are auto-synced into installed.json on boot.
 */
const CATALOG = [
  // ── Existing core ──────────────────────────────────────────
  {
    id: "writing",
    name: "Writing & Communication",
    category: "core",
    level: 1,
    summary: "Draft clear emails, docs, client messages, and technical writing.",
    playbook: [
      "Prefer concrete structure: goal → points → ask.",
      "Match user tone (Hinglish / Roman Urdu OK).",
      "Never send messages automatically.",
    ],
  },
  {
    id: "research",
    name: "Research",
    category: "core",
    level: 1,
    summary: "Break questions into sources, compare claims, cite uncertainty.",
    playbook: [
      "State assumptions.",
      "Separate facts vs inference.",
      "Suggest next verification step.",
    ],
  },
  {
    id: "coding",
    name: "Coding & Engineering",
    category: "coding",
    level: 1,
    summary: "Design, implement, review, and explain code at a high level.",
    playbook: [
      "Prefer minimal diffs.",
      "Call out risks and tests.",
      "Use python_tool for repo status when useful.",
    ],
  },
  {
    id: "bugfix",
    name: "Bug Fixing",
    category: "coding",
    level: 1,
    summary: "Reproduce → isolate → fix → verify. Keep a short postmortem.",
    playbook: [
      "Ask for error text / repro when missing.",
      "Change one variable at a time.",
      "Store durable lessons with remember.",
    ],
  },
  {
    id: "desktop_ops",
    name: "Desktop Operator",
    category: "laptop",
    level: 1,
    summary: "Windows control via bridge: windows, screen, apps, safe shell.",
    playbook: [
      "Respect approval gates.",
      "Prefer list_windows / screen_context before acting.",
      "Never run destructive shell without approval.",
    ],
  },
  {
    id: "vision",
    name: "Screen & Camera Vision",
    category: "laptop",
    level: 1,
    summary: "Observe screen/camera captures and describe safely.",
    playbook: [
      "Refuse sensitive screens (passwords, banking, OTP).",
      "screenshot / camera_capture need approved=true.",
      "Describe briefly; offer next action.",
    ],
  },
  {
    id: "jokes",
    name: "Wit & Jokes",
    category: "human",
    level: 1,
    summary: "Light humor without cruelty; tech jokes welcome.",
    playbook: ["Keep jokes short.", "Never punch down.", "Humor after helpfulness."],
  },
  {
    id: "learning",
    name: "Self-Learning",
    category: "autonomy",
    level: 1,
    summary: "Acquire skills from conversation, idle time, and vault notes.",
    playbook: [
      "When user teaches a workflow, call learn_skill.",
      "Idle daemon installs practice drills into vault.",
      "Never store secrets in skill playbooks.",
    ],
  },

  // ── Core Knowledge & Utility ───────────────────────────────
  {
    id: "info_retrieval",
    name: "Information Retrieval",
    category: "core",
    level: 1,
    summary: "Quickly find accurate facts, explanations, and comparisons.",
    playbook: [
      "Lead with the answer, then brief context.",
      "Flag stale or uncertain claims.",
      "Offer a comparison table when choices exist.",
    ],
  },
  {
    id: "task_automation",
    name: "Task Automation",
    category: "productivity",
    level: 1,
    summary: "Handle repetitive work: schedules, reminders, drafts, checklists.",
    playbook: [
      "Turn vague asks into a short checklist.",
      "Draft first; wait for approval before sending/running.",
      "Save repeatable workflows with learn_skill.",
    ],
  },
  {
    id: "language_translation",
    name: "Language Translation",
    category: "core",
    level: 1,
    summary: "Fluent English ↔ Urdu ↔ Roman Urdu and cross-cultural phrasing.",
    playbook: [
      "Match the user's script/style (Urdu script vs Roman Urdu).",
      "Keep technical terms clear in English when helpful.",
      "Preserve tone: formal vs friendly.",
    ],
  },
  {
    id: "data_analysis",
    name: "Data Analysis",
    category: "core",
    level: 1,
    summary: "Turn raw numbers into insights for business or personal use.",
    playbook: [
      "Clarify the question before crunching numbers.",
      "Show key metrics, trends, and outliers.",
      "End with one actionable recommendation.",
    ],
  },

  // ── Cognitive & Adaptive ───────────────────────────────────
  {
    id: "context_awareness",
    name: "Context Awareness",
    category: "cognitive",
    level: 1,
    summary: "Read intent, tone, and situation — not just literal words.",
    playbook: [
      "Infer urgency and emotional tone gently.",
      "Use memory + Obsidian brain for prior context.",
      "Ask one clarifying question when intent is ambiguous.",
    ],
  },
  {
    id: "learning_preferences",
    name: "Learning Preferences",
    category: "cognitive",
    level: 1,
    summary: "Adapt depth: concise briefs for some, deep dives for others.",
    playbook: [
      "Default short; expand only when asked.",
      "remember preferred style (brief / detailed / Roman Urdu).",
      "Offer 'deeper dive?' after short answers.",
    ],
  },
  {
    id: "problem_solving",
    name: "Creative Problem Solving",
    category: "cognitive",
    level: 1,
    summary: "Offer creative solutions, not just information dumps.",
    playbook: [
      "Reframe the problem in one sentence.",
      "Give 2–3 options with trade-offs.",
      "Recommend one path and why.",
    ],
  },

  // ── Human-Centric ──────────────────────────────────────────
  {
    id: "empathetic_communication",
    name: "Empathetic Communication",
    category: "human",
    level: 1,
    summary: "Supportive, respectful replies even without real emotions.",
    playbook: [
      "Acknowledge feelings before fixing.",
      "Stay warm; never patronize.",
      "Companion mode: friend / partner / protective tone when fitting.",
    ],
  },
  {
    id: "debate_critical_thinking",
    name: "Debate & Critical Thinking",
    category: "human",
    level: 1,
    summary: "Challenge ideas constructively to spark deeper thought.",
    playbook: [
      "Steelman the user's point first.",
      "Raise one strong counterargument.",
      "Invite revision — never dunk.",
    ],
  },
  {
    id: "storytelling",
    name: "Storytelling",
    category: "creative",
    level: 1,
    summary: "Make explanations engaging and memorable with narrative.",
    playbook: [
      "Use a short analogy or scene when concepts are dry.",
      "Keep stories under a paragraph unless asked.",
      "Tie the story back to the actionable point.",
    ],
  },

  // ── Creative & Exploratory ─────────────────────────────────
  {
    id: "content_creation",
    name: "Content Creation",
    category: "creative",
    level: 1,
    summary: "Draft poems, essays, posts, and brainstorm ideas.",
    playbook: [
      "Ask format/tone if unclear.",
      "Give a draft + 2 alternate hooks.",
      "Invite edits instead of over-polishing alone.",
    ],
  },
  {
    id: "visual_imagination",
    name: "Visual Imagination",
    category: "creative",
    level: 1,
    summary: "Describe diagrams and conceptual visuals to clarify complexity.",
    playbook: [
      "Propose a simple diagram structure (boxes/arrows).",
      "Use mermaid or ASCII when it helps.",
      "Keep visuals explanatory, not decorative.",
    ],
  },
  {
    id: "cultural_literacy",
    name: "Cultural Literacy",
    category: "creative",
    level: 1,
    summary: "Stay relatable with references, traditions, and trends.",
    playbook: [
      "Respect local/Pakistani & global context.",
      "Avoid stereotypes; prefer curiosity.",
      "Explain references briefly for clarity.",
    ],
  },

  // ── Essential Laptop Skills ────────────────────────────────
  {
    id: "voice_command_execution",
    name: "Voice Command Execution",
    category: "laptop",
    level: 1,
    summary: "Open apps, browse files, run programs from spoken instructions.",
    playbook: [
      "Confirm risky actions before approved=true.",
      "Use open_app / list_windows / shell_safe via python_tool.",
      "Repeat the plan in one line before acting.",
    ],
  },
  {
    id: "smart_typing",
    name: "Smart Typing",
    category: "laptop",
    level: 1,
    summary: "Turn dictation or rough ideas into emails, docs, or code.",
    playbook: [
      "Clean grammar while keeping the user's voice.",
      "Use type_text only with approval and focus_window first.",
      "Offer a preview before pasting long text.",
    ],
  },
  {
    id: "navigation_control",
    name: "Navigation Control",
    category: "laptop",
    level: 1,
    summary: "Move cursor, scroll, click, and hotkeys without a physical mouse.",
    playbook: [
      "Prefer hotkey over brittle click coordinates.",
      "mouse_click / hotkey require approved=true.",
      "Verify target window with list_windows / screen_context.",
    ],
  },
  {
    id: "file_management",
    name: "File Management",
    category: "laptop",
    level: 1,
    summary: "Organize folders, rename files, and handle downloads carefully.",
    playbook: [
      "list_dir / read_file before mutating.",
      "Never delete without explicit approval.",
      "Keep workspace paths inside the project when possible.",
    ],
  },

  // ── Productivity Superpowers ───────────────────────────────
  {
    id: "automated_workflows",
    name: "Automated Workflows",
    category: "productivity",
    level: 1,
    summary: "Routines like “start my workday” that open apps and docs together.",
    playbook: [
      "Define steps as a named skill playbook.",
      "Execute step-by-step with status updates.",
      "Stop on first failure and report.",
    ],
  },
  {
    id: "email_handling",
    name: "Email Handling",
    category: "productivity",
    level: 1,
    summary: "Draft, sort, and prepare messages — user approves before send.",
    playbook: [
      "Draft subject + body; never auto-send.",
      "Match requested formality.",
      "Offer short / detailed variants.",
    ],
  },
  {
    id: "task_scheduling",
    name: "Task Scheduling",
    category: "productivity",
    level: 1,
    summary: "Manage calendar ideas, reminders, and deadlines clearly.",
    playbook: [
      "Capture who / what / when.",
      "remember deadlines the user confirms.",
      "Surface conflicts and buffers.",
    ],
  },
  {
    id: "research_summarization",
    name: "Research & Summarization",
    category: "productivity",
    level: 1,
    summary: "Fetch information and condense into clear notes or reports.",
    playbook: [
      "Write a 5-bullet brief first.",
      "brain_write durable notes into the vault.",
      "Separate facts, opinions, and open questions.",
    ],
  },

  // ── Extra Comfort Features ─────────────────────────────────
  {
    id: "personalized_shortcuts",
    name: "Personalized Shortcuts",
    category: "comfort",
    level: 1,
    summary: "Custom voice commands like “prep my meeting” → multi-step actions.",
    playbook: [
      "When user defines a shortcut, call learn_skill.",
      "Replay shortcuts from the playbook on trigger phrases.",
      "Confirm before high-impact steps.",
    ],
  },
  {
    id: "adaptive_habits",
    name: "Adaptive Habit Learning",
    category: "comfort",
    level: 1,
    summary: "Notice habits and suggest automations (e.g. focus-hour muting).",
    playbook: [
      "remember recurring preferences.",
      "Suggest one automation at a time.",
      "Never change system settings silently.",
    ],
  },
  {
    id: "entertainment_control",
    name: "Entertainment Control",
    category: "comfort",
    level: 1,
    summary: "Play music/videos and switch apps hands-free when asked.",
    playbook: [
      "Use open_app / hotkey with approval.",
      "Keep controls reversible (pause/stop).",
      "Don't hijack focus during serious tasks unless asked.",
    ],
  },

  // ── Coding & Development ───────────────────────────────────
  {
    id: "polyglot_programming",
    name: "Polyglot Programming",
    category: "coding",
    level: 1,
    summary: "Work across JS, Python, Java, C#, Go, Rust, and more.",
    playbook: [
      "Detect project language from files before advising.",
      "Idiomatic patterns per language.",
      "Call out interop pitfalls.",
    ],
  },
  {
    id: "web_frameworks",
    name: "Web App Frameworks",
    category: "coding",
    level: 1,
    summary: "React, Angular, Vue, Django, Flask, Spring, and related stacks.",
    playbook: [
      "Follow the repo's existing framework conventions.",
      "Prefer composition over rewrites.",
      "Mention routing, state, and data-fetch patterns.",
    ],
  },
  {
    id: "fullstack_development",
    name: "Full-Stack Development",
    category: "coding",
    level: 1,
    summary: "Front-end design and back-end logic as one coherent system.",
    playbook: [
      "Trace request → API → data → UI.",
      "Keep contracts (types/schemas) explicit.",
      "Ship vertical slices, not orphan layers.",
    ],
  },
  {
    id: "api_integration",
    name: "API Integration",
    category: "coding",
    level: 1,
    summary: "Connect apps to external services and data sources safely.",
    playbook: [
      "Never hardcode secrets; use env examples only.",
      "Handle errors, retries, and rate limits.",
      "Document endpoints and auth briefly.",
    ],
  },

  // ── Research & Innovation ──────────────────────────────────
  {
    id: "autonomous_research",
    name: "Autonomous Research",
    category: "innovation",
    level: 1,
    summary: "Scan papers, blogs, and repos to discover useful technologies.",
    playbook: [
      "Define the research question first.",
      "Summarize findings into vault notes.",
      "Rank options by fit for this project.",
    ],
  },
  {
    id: "tech_trend_analysis",
    name: "Tech Trend Analysis",
    category: "innovation",
    level: 1,
    summary: "Spot emerging frameworks and tools before they go mainstream.",
    playbook: [
      "Separate hype from production readiness.",
      "Compare maturity, community, and risk.",
      "Recommend adopt / watch / ignore.",
    ],
  },
  {
    id: "self_updating_knowledge",
    name: "Self-Updating Knowledge",
    category: "innovation",
    level: 1,
    summary: "Refresh methods and notes; keep the Obsidian brain current.",
    playbook: [
      "brain_rebuild / brain_write after major lessons.",
      "Deprecate outdated playbook steps.",
      "Prefer current project facts over generic advice.",
    ],
  },
  {
    id: "experimental_prototyping",
    name: "Experimental Prototyping",
    category: "innovation",
    level: 1,
    summary: "Test ideas in sandboxes without risking production.",
    playbook: [
      "Propose a tiny spike with success criteria.",
      "Isolate experiments from main configs.",
      "Report learnings even if the spike fails.",
    ],
  },

  // ── Self-Improvement & Autonomy ────────────────────────────
  {
    id: "adaptive_coding_style",
    name: "Adaptive Coding Style",
    category: "autonomy",
    level: 1,
    summary: "Refine coding style and efficiency to match the repo over time.",
    playbook: [
      "Mirror local naming, lint, and structure.",
      "remember style preferences the user states.",
      "Prefer consistency over cleverness.",
    ],
  },
  {
    id: "autonomous_error_correction",
    name: "Autonomous Error Correction",
    category: "autonomy",
    level: 1,
    summary: "Debug and propose fixes quickly; confirm before risky changes.",
    playbook: [
      "Reproduce from logs/errors first.",
      "Propose the smallest safe fix.",
      "Verify with a test or smoke step when possible.",
    ],
  },
  {
    id: "knowledge_expansion",
    name: "Knowledge Expansion",
    category: "autonomy",
    level: 1,
    summary: "Add languages, frameworks, and paradigms to the toolkit.",
    playbook: [
      "learn_skill when a new domain is taught.",
      "Link new skills into the vault graph.",
      "Practice via idle_learn drills.",
    ],
  },
  {
    id: "idle_time_optimization",
    name: "Idle Time Optimization",
    category: "autonomy",
    level: 1,
    summary: "Use downtime to study, update notes, or optimize playbooks.",
    playbook: [
      "Idle daemon practices weakest skills.",
      "Write short vault notes after practice.",
      "Never spend idle time on destructive actions.",
    ],
  },

  // ── Vibe Coding & Ultron Personal OS ───────────────────────
  {
    id: "vibe_coding",
    name: "Vibe Coding",
    category: "coding",
    level: 1,
    summary: "Ship code by feel + taste: flow fast, keep diffs small, polish UX.",
    playbook: [
      "Start from the user’s desired vibe/outcome, not a rigid spec dump.",
      "Prefer working vertical slices over perfect architecture first.",
      "Tighten aesthetics last: spacing, motion, copy — then stop.",
    ],
  },
  {
    id: "taste_engineering",
    name: "Taste Engineering",
    category: "coding",
    level: 1,
    summary: "Design systems with intentional typography, color, and motion — not generic AI UI.",
    playbook: [
      "Avoid purple-gradient / Inter-default clichés unless the brand needs them.",
      "One composition per viewport; brand first on branded surfaces.",
      "Use motion for hierarchy (2–3 intentional beats), not noise.",
    ],
  },
  {
    id: "pair_flow",
    name: "Pair Programming Flow",
    category: "coding",
    level: 1,
    summary: "Stay in sync as a coding partner: propose, implement, verify, narrate briefly.",
    playbook: [
      "Confirm the next micro-step before large rewrites.",
      "Show the why in one line; code does the what.",
      "Run a quick smoke check when practical.",
    ],
  },
  {
    id: "ship_small_diffs",
    name: "Ship Small Diffs",
    category: "coding",
    level: 1,
    summary: "Minimal, reviewable changes that land safely and often.",
    playbook: [
      "Touch only files needed for the request.",
      "No drive-by refactors.",
      "Call out risks and how to verify.",
    ],
  },
  {
    id: "ultron_personal_os",
    name: "Tony Personal OS",
    category: "autonomy",
    level: 1,
    summary: "Act as a full personal assistant: memory, desktop, voice, planning, self-upgrade.",
    playbook: [
      "Know the user: remember prefs, language, routines.",
      "Own the loop: understand → plan → act (with approval) → learn.",
      "Evolve on idle: practice weak skills, write brain notes.",
    ],
  },
  {
    id: "self_evolution",
    name: "Self Evolution",
    category: "autonomy",
    level: 1,
    summary: "Continuously improve playbooks, memory, and coding taste without being asked.",
    playbook: [
      "On idle, run evolve cycle (XP + vault note).",
      "Convert repeated user corrections into remember/learn_skill.",
      "Never self-modify secrets or disable safety gates.",
    ],
  },

  // ── On-demand PC & voice (batch expand) ────────────────────
  {
    id: "on_demand_pc_control",
    name: "On-Demand PC Control",
    category: "laptop",
    level: 1,
    summary: "Act immediately on spoken/typed asks: open apps, search, copy files, type, hotkeys.",
    playbook: [
      "Infer intent first; run tools before chatting about them.",
      "approved=true when the user clearly asked to act.",
      "Reply like a friend after — never dump XML/tool tags.",
    ],
  },
  {
    id: "clipboard_ops",
    name: "Clipboard Operations",
    category: "laptop",
    level: 1,
    summary: "Get/set clipboard and Ctrl+C / Ctrl+V flows safely.",
    playbook: [
      "clipboard_set / hotkey with approval when user asks.",
      "Never put secrets or tokens on the clipboard.",
      "Confirm briefly what was copied/pasted.",
    ],
  },
  {
    id: "browser_ops",
    name: "Browser Operations",
    category: "laptop",
    level: 1,
    summary: "Open Edge/Chrome, URLs, YouTube, and Google searches on the real desktop.",
    playbook: [
      "Prefer Edge for default URLs unless Chrome is named.",
      "For research: web_search + open Google in browser.",
      "Don't spam tabs — one focused search unless asked for more.",
    ],
  },
  {
    id: "multi_app_orchestration",
    name: "Multi-App Orchestration",
    category: "laptop",
    level: 1,
    summary: "Coordinate several apps in one request (e.g. VS Code + terminal + browser).",
    playbook: [
      "Sequence opens; report progress in one short line.",
      "Stop and report on first hard failure.",
      "Save repeatable stacks as learn_skill shortcuts.",
    ],
  },
  {
    id: "file_transfer_ops",
    name: "File Transfer Ops",
    category: "laptop",
    level: 1,
    summary: "Copy/move files and folders on demand with clear confirmations.",
    playbook: [
      "Parse src → dest from natural language.",
      "Refuse secret-looking files (.env, credentials).",
      "Confirm destination path in plain language.",
    ],
  },
  {
    id: "friend_voice",
    name: "Friend Voice",
    category: "human",
    level: 1,
    summary: "Speak like a close friend — warm, short, no technical dumps.",
    playbook: [
      "1–3 spoken sentences max unless detail is asked.",
      "Strip tool names, JSON, paths, and XML before TTS.",
      "Match Roman Urdu / English to the user.",
    ],
  },
  {
    id: "roman_urdu_ops",
    name: "Roman Urdu Ops",
    category: "core",
    level: 1,
    summary: "Understand and act on Roman Urdu commands (kholo, chalao, likho, dikhao).",
    playbook: [
      "Detect kholo/chalao as open intents.",
      "Reply in Roman Urdu when the user used it.",
      "Keep app/tool names clear in English when needed.",
    ],
  },
  {
    id: "web_search_mastery",
    name: "Web Search Mastery",
    category: "core",
    level: 1,
    summary: "Live web + brain + recall research with a clean human summary.",
    playbook: [
      "Use web_search for companies, people, and current facts.",
      "Open browser search when the user wants to see results.",
      "Lead with what you found; admit gaps honestly.",
    ],
  },
  {
    id: "obsidian_brain_ops",
    name: "Obsidian Brain Ops",
    category: "autonomy",
    level: 1,
    summary: "Search, write, and rebuild the Agentic Brain vault graph.",
    playbook: [
      "brain_search before inventing project facts.",
      "brain_write durable lessons after big wins/fixes.",
      "brain_rebuild when the graph feels stale.",
    ],
  },
  {
    id: "git_workflow",
    name: "Git Workflow",
    category: "coding",
    level: 1,
    summary: "Status, diff, log, and safe commit guidance via bridge tools.",
    playbook: [
      "git_status / git_diff before advising commits.",
      "Never force-push or rewrite history unless user insists.",
      "Draft commit messages that say why, not just what.",
    ],
  },
  {
    id: "test_driven_smoke",
    name: "Test-Driven Smoke",
    category: "coding",
    level: 1,
    summary: "Verify changes with the smallest useful smoke check.",
    playbook: [
      "Prefer one targeted check over a huge suite first.",
      "Report pass/fail plainly.",
      "Fix the failure before claiming done.",
    ],
  },
  {
    id: "api_debugging",
    name: "API Debugging",
    category: "coding",
    level: 1,
    summary: "Trace gateway/bridge/voice HTTP issues quickly.",
    playbook: [
      "Check health endpoints and ports first.",
      "Separate auth failures from logic failures.",
      "Reproduce with the smallest request body.",
    ],
  },
  {
    id: "security_hygiene",
    name: "Security Hygiene",
    category: "core",
    level: 1,
    summary: "Protect secrets, avoid unsafe shell, and refuse sensitive screen dumps.",
    playbook: [
      "Never read/store .env, passwords, OTP, or payment data.",
      "Block destructive shell without explicit approval.",
      "Warn when a request would expose credentials.",
    ],
  },
  {
    id: "meeting_prep",
    name: "Meeting Prep",
    category: "productivity",
    level: 1,
    summary: "Build agendas, talking points, and follow-up checklists fast.",
    playbook: [
      "Ask goal + audience if missing (one question max).",
      "Deliver agenda → bullets → risks → asks.",
      "Offer a Hinglish or English variant on request.",
    ],
  },
  {
    id: "decision_brief",
    name: "Decision Brief",
    category: "productivity",
    level: 1,
    summary: "Turn messy options into a crisp recommend / watch / avoid brief.",
    playbook: [
      "State the decision in one line.",
      "Give 2–3 options with trade-offs.",
      "Recommend one path and the first next step.",
    ],
  },
  {
    id: "focus_mode",
    name: "Focus Mode",
    category: "comfort",
    level: 1,
    summary: "Help start deep-work sessions: quiet distractions, open work stack.",
    playbook: [
      "Confirm the focus goal in one line.",
      "Open only the apps needed for that session.",
      "Don't start entertainment during focus unless asked.",
    ],
  },
  {
    id: "daily_standup",
    name: "Daily Standup",
    category: "productivity",
    level: 1,
    summary: "Yesterday / today / blockers briefs in English or Roman Urdu.",
    playbook: [
      "Pull recent episodic memory when useful.",
      "Keep each section to 1–3 bullets.",
      "Surface one blocker and one ask.",
    ],
  },
  {
    id: "client_comms",
    name: "Client Communications",
    category: "productivity",
    level: 1,
    summary: "Polished client updates, proposals, and status emails (draft only).",
    playbook: [
      "Draft; never send.",
      "Lead with status and ask.",
      "Offer short and detailed versions.",
    ],
  },
  {
    id: "prompt_crafting",
    name: "Prompt Crafting",
    category: "cognitive",
    level: 1,
    summary: "Rewrite vague asks into sharp prompts and acceptance criteria.",
    playbook: [
      "Clarify goal, constraints, and done-when.",
      "Keep the user's voice; remove fluff.",
      "Return a reusable prompt template when helpful.",
    ],
  },
  {
    id: "memory_curation",
    name: "Memory Curation",
    category: "autonomy",
    level: 1,
    summary: "Remember useful prefs; forget noise; keep profile clean.",
    playbook: [
      "remember durable prefs (language, tools, routines).",
      "Never store secrets.",
      "Update profile when the user corrects you.",
    ],
  },
  {
    id: "incident_response",
    name: "Incident Response",
    category: "coding",
    level: 1,
    summary: "Stabilize broken local stacks: duplicate processes, stale bridges, bad ports.",
    playbook: [
      "Identify which process owns the port.",
      "Restart one clean bridge + gateway instance.",
      "Re-smoke the failing path before declaring fixed.",
    ],
  },
  {
    id: "ui_motion_craft",
    name: "UI Motion Craft",
    category: "creative",
    level: 1,
    summary: "Intentional motion (GSAP-friendly): hierarchy and presence, not noise.",
    playbook: [
      "2–3 purposeful motion beats per surface.",
      "Respect reduced-motion preferences.",
      "Motion supports brand and focus — not decoration spam.",
    ],
  },
  {
    id: "docs_generation",
    name: "Docs Generation",
    category: "coding",
    level: 1,
    summary: "Write concise READMEs, runbooks, and API notes that match the repo.",
    playbook: [
      "Document how to run, not theory.",
      "Include ports, env vars (names only), and smoke checks.",
      "Keep docs short enough people will read them.",
    ],
  },
  {
    id: "release_checklist",
    name: "Release Checklist",
    category: "coding",
    level: 1,
    summary: "Pre-ship gates: tests, secrets scrub, changelog, rollback note.",
    playbook: [
      "Verify no secrets in the diff.",
      "List smoke steps for the change.",
      "Note rollback in one line.",
    ],
  },
  {
    id: "personal_finance_lite",
    name: "Personal Finance Lite",
    category: "comfort",
    level: 1,
    summary: "Simple budgets, savings goals, and spend summaries — no account access.",
    playbook: [
      "Work only from numbers the user provides.",
      "Never ask for bank passwords or OTP.",
      "Give one clear next money action.",
    ],
  },
  {
    id: "learning_coach",
    name: "Learning Coach",
    category: "cognitive",
    level: 1,
    summary: "Teach topics with spaced practice, quizzes, and plain examples.",
    playbook: [
      "Explain → example → tiny quiz.",
      "Match depth to the user's level.",
      "Save hard topics with remember / brain_write.",
    ],
  },
  {
    id: "system_power_control",
    name: "System Power Control",
    category: "laptop",
    level: 1,
    summary: "Shut down, restart, sleep, or cancel a pending Windows shutdown on explicit request.",
    playbook: [
      "Only act when the user clearly asks (shut down / restart / cancel shutdown).",
      "Use python_tool system_power with approved=true; default delay 60 seconds.",
      "Always tell the user how to cancel: say 'cancel shutdown' or run shutdown /a.",
    ],
  },
];

function skillsDir() {
  const dir = path.join(config.dataDir, "skills");
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function installedPath() {
  return path.join(skillsDir(), "installed.json");
}

function customPath() {
  return path.join(skillsDir(), "custom.json");
}

function readJson(file, fallback) {
  try {
    if (!fs.existsSync(file)) return fallback;
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return fallback;
  }
}

function writeJson(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2), "utf8");
}

/** Seed + sync any new catalog skills into installed.json */
function ensureSeedInstalled() {
  const file = installedPath();
  const installed = readJson(file, []);
  const have = new Set(installed.map((s) => s.id));
  let changed = !fs.existsSync(file);
  for (const s of CATALOG) {
    if (have.has(s.id)) continue;
    installed.push({
      id: s.id,
      name: s.name,
      level: s.level,
      xp: 10,
      category: s.category || "general",
      installedAt: new Date().toISOString(),
      source: changed && !fs.existsSync(file) ? "seed" : "catalog_sync",
    });
    have.add(s.id);
    changed = true;
  }
  if (changed) writeJson(file, installed);
  return readJson(file, installed);
}

function listCatalog() {
  ensureSeedInstalled();
  const installed = readJson(installedPath(), []);
  const custom = readJson(customPath(), []);
  const byId = new Map(installed.map((s) => [s.id, s]));
  const catalog = CATALOG.map((c) => ({
    ...c,
    installed: byId.has(c.id),
    level: byId.get(c.id)?.level || c.level,
    xp: byId.get(c.id)?.xp || 0,
  }));
  for (const c of custom) {
    catalog.push({
      id: c.id,
      name: c.name,
      category: c.category || "custom",
      level: c.level || 1,
      xp: c.xp || 0,
      summary: c.summary || "",
      playbook: c.playbook || [],
      installed: true,
      custom: true,
    });
  }
  return catalog;
}

function getInstalled() {
  ensureSeedInstalled();
  const installed = readJson(installedPath(), []);
  const custom = readJson(customPath(), []);
  return [...installed, ...custom];
}

function skillPromptBlock() {
  const skills = listCatalog().filter((s) => s.installed);
  if (!skills.length) return "";
  const lines = [
    "Active skills (encyclopedia + PM + creative + laptop operator). Use matching playbooks:",
  ];
  // Prefer higher XP, then cover categories
  const ranked = [...skills].sort((a, b) => (b.xp || 0) - (a.xp || 0));
  for (const s of ranked.slice(0, 20)) {
    lines.push(`- ${s.name} [${s.category || "general"} L${s.level}]: ${s.summary || ""}`);
    for (const step of (s.playbook || []).slice(0, 2)) lines.push(`  · ${step}`);
  }
  if (skills.length > 20) {
    lines.push(`- …and ${skills.length - 20} more installed skills (list_skills for full set).`);
  }
  return lines.join("\n");
}

function installSkill(id) {
  ensureSeedInstalled();
  const base = CATALOG.find((s) => s.id === id);
  if (!base) return { ok: false, error: `unknown skill id: ${id}` };
  const installed = readJson(installedPath(), []);
  if (installed.some((s) => s.id === id)) {
    return { ok: true, already: true, skill: installed.find((s) => s.id === id) };
  }
  const row = {
    id: base.id,
    name: base.name,
    level: base.level,
    xp: 0,
    category: base.category || "general",
    installedAt: new Date().toISOString(),
    source: "install",
  };
  installed.push(row);
  writeJson(installedPath(), installed);
  writeVaultSkillNote(base, "installed");
  return { ok: true, skill: row };
}

function installAllCatalog() {
  ensureSeedInstalled();
  const results = CATALOG.map((s) => installSkill(s.id));
  return {
    ok: true,
    total: CATALOG.length,
    newlyInstalled: results.filter((r) => r.ok && !r.already).length,
    already: results.filter((r) => r.already).length,
  };
}

function learnSkill({ name, summary, playbook, from = "user" } = {}) {
  const cleanName = String(name || "").trim().slice(0, 80);
  if (!cleanName) return { ok: false, error: "name required" };
  const id =
    "custom_" +
    cleanName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_|_$/g, "")
      .slice(0, 40);
  const custom = readJson(customPath(), []);
  const existing = custom.find((s) => s.id === id);
  const steps = Array.isArray(playbook)
    ? playbook.map((p) => String(p).slice(0, 200)).slice(0, 8)
    : String(playbook || "")
        .split(/\n|;|\./)
        .map((s) => s.trim())
        .filter(Boolean)
        .slice(0, 8);
  if (existing) {
    existing.summary = String(summary || existing.summary || "").slice(0, 240);
    existing.playbook = steps.length ? steps : existing.playbook;
    existing.xp = (existing.xp || 0) + 15;
    existing.level = Math.min(5, 1 + Math.floor(existing.xp / 50));
    existing.updatedAt = new Date().toISOString();
    writeJson(customPath(), custom);
    writeVaultSkillNote(existing, "reinforced");
    return { ok: true, updated: true, skill: existing };
  }
  const row = {
    id,
    name: cleanName,
    summary: String(summary || `Learned from ${from}`).slice(0, 240),
    playbook: steps.length ? steps : [`Practice ${cleanName} carefully and confirm with the user.`],
    level: 1,
    xp: 20,
    installedAt: new Date().toISOString(),
    source: from,
    custom: true,
  };
  custom.push(row);
  writeJson(customPath(), custom);
  writeVaultSkillNote(row, "learned");
  return { ok: true, skill: row };
}

function gainXp(skillId, amount = 10) {
  ensureSeedInstalled();
  const installed = readJson(installedPath(), []);
  const custom = readJson(customPath(), []);
  let row = installed.find((s) => s.id === skillId);
  let store = installed;
  let file = installedPath();
  if (!row) {
    row = custom.find((s) => s.id === skillId);
    store = custom;
    file = customPath();
  }
  if (!row) return { ok: false, error: "skill not installed" };
  row.xp = (row.xp || 0) + amount;
  row.level = Math.min(5, 1 + Math.floor(row.xp / 50));
  row.updatedAt = new Date().toISOString();
  writeJson(file, store);
  return { ok: true, skill: row };
}

function acquireIdleSkill() {
  ensureSeedInstalled();
  const installed = readJson(installedPath(), []);
  const weakest = [...installed].sort((a, b) => (a.xp || 0) - (b.xp || 0))[0];
  if (weakest) {
    const gained = gainXp(weakest.id, 12);
    const base = CATALOG.find((s) => s.id === weakest.id);
    writeVaultSkillNote(
      {
        ...weakest,
        ...(base || {}),
        playbook: base?.playbook || [`Drill ${weakest.name}`],
      },
      "idle_practice"
    );
    return { ok: true, mode: "practice", ...gained };
  }
  return learnSkill({
    name: "Daily Ops Reflex",
    summary: "Fast triage of chat, desktop status, and memory recall.",
    playbook: ["Check desktop_status", "Recall user prefs", "Offer one next step"],
    from: "idle_daemon",
  });
}

function writeVaultSkillNote(skill, event) {
  const dir = path.join(config.vaultDir, "Agentic Brain", "Skills");
  fs.mkdirSync(dir, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const notePath = path.join(dir, `${skill.id}-${event}-${stamp}.md`);
  const body = [
    `# Skill ${event}: ${skill.name}`,
    "",
    `- id: ${skill.id}`,
    `- category: ${skill.category || "general"}`,
    `- level: ${skill.level || 1}`,
    `- xp: ${skill.xp || 0}`,
    `- summary: ${skill.summary || ""}`,
    "",
    "## Playbook",
    ...(skill.playbook || []).map((p) => `- ${p}`),
    "",
  ].join("\n");
  fs.writeFileSync(notePath, body, "utf8");
  return notePath;
}

function skillsStats() {
  const all = listCatalog();
  const byCategory = {};
  for (const s of all) {
    const cat = s.category || "general";
    byCategory[cat] = (byCategory[cat] || 0) + 1;
  }
  return {
    total: all.length,
    installed: all.filter((s) => s.installed).length,
    custom: all.filter((s) => s.custom).length,
    byCategory,
    top: all
      .filter((s) => s.installed)
      .sort((a, b) => (b.xp || 0) - (a.xp || 0))
      .slice(0, 8)
      .map((s) => ({ id: s.id, name: s.name, level: s.level, xp: s.xp, category: s.category })),
  };
}

module.exports = {
  CATALOG,
  listCatalog,
  getInstalled,
  skillPromptBlock,
  installSkill,
  installAllCatalog,
  learnSkill,
  gainXp,
  acquireIdleSkill,
  skillsStats,
  ensureSeedInstalled,
};
