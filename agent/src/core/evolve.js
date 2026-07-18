"use strict";

/**
 * Ultron self-evolution — uses idle time to strengthen weak skills,
 * consolidate memory into the Obsidian brain, and write improvement notes.
 */
const fs = require("fs");
const path = require("path");
const { config } = require("../config");
const { recentEpisodic, memoryHints, rememberFact } = require("../memory/store");
const { acquireIdleSkill, gainXp, listCatalog, skillsStats } = require("../skills/registry");
const { writeNote, rebuildGraph, brainStats } = require("../brain/obsidian");

function extractThemes(episodes) {
  const text = episodes.map((e) => String(e.content || "")).join(" ").toLowerCase();
  const themes = [];
  const checks = [
    ["coding", /\b(code|bug|git|react|api|function|error)\b/],
    ["vibe_coding", /\b(vibe|ui|design|aesthetic|polish|feel)\b/],
    ["desktop_ops", /\b(window|screen|click|type|desktop|app)\b/],
    ["language_translation", /\b(urdu|roman|hinglish|translate)\b/],
    ["research", /\b(research|explain|what is|kaise|kya)\b/],
  ];
  for (const [id, re] of checks) {
    if (re.test(text)) themes.push(id);
  }
  return themes;
}

function evolveOnce({ writeBrain = true } = {}) {
  const episodes = recentEpisodic(24);
  const themes = extractThemes(episodes);
  const practiced = [];

  // Practice weakest skills + theme-matched skills
  const catalog = listCatalog().filter((s) => s.installed);
  const weakest = [...catalog].sort((a, b) => (a.xp || 0) - (b.xp || 0)).slice(0, 3);
  for (const s of weakest) {
    practiced.push(gainXp(s.id, 8));
  }
  for (const id of themes.slice(0, 3)) {
    if (catalog.some((s) => s.id === id)) practiced.push(gainXp(id, 10));
  }

  const idle = acquireIdleSkill();

  let note = null;
  if (writeBrain) {
    const hints = memoryHints().slice(0, 6);
    const body = [
      `evolved_at: ${new Date().toISOString()}`,
      `themes: ${themes.join(", ") || "general"}`,
      "",
      "## What I practiced",
      ...practiced.filter((p) => p.ok).map((p) => `- ${p.skill?.name || p.skill?.id} → L${p.skill?.level} (${p.skill?.xp}xp)`),
      "",
      "## Recent conversation signal",
      ...episodes
        .filter((e) => e.role === "user")
        .slice(-5)
        .map((e) => `- ${String(e.content || "").slice(0, 140)}`),
      "",
      "## Known user facts",
      ...(hints.length ? hints.map((h) => `- ${h}`) : ["- (none yet)"]),
      "",
      "## Next self-upgrade",
      "- Keep replies matched to language style.",
      "- Prefer small diffs when coding (vibe coding).",
      "- Ask before risky desktop actions.",
      "",
    ].join("\n");
    note = writeNote({
      title: `ultron-evolve-${new Date().toISOString().slice(0, 10)}`,
      body,
      folder: "Agentic Brain/Inbox",
    });
  }

  try {
    rebuildGraph();
  } catch {
    /* ignore */
  }

  // Soft preference: Ultron identity
  try {
    rememberFact("User runs Ultron personal assistant (Tony core) as their desktop AI", "profile", "evolve");
  } catch {
    /* ignore */
  }

  return {
    ok: true,
    themes,
    practiced: practiced.filter((p) => p.ok).length,
    idle,
    note,
    skills: skillsStats(),
    brain: brainStats(),
  };
}

function evolveLogPath() {
  const dir = path.join(config.dataDir, "evolve");
  fs.mkdirSync(dir, { recursive: true });
  return path.join(dir, "evolve.jsonl");
}

function evolveAndLog() {
  const result = evolveOnce();
  fs.appendFileSync(
    evolveLogPath(),
    `${JSON.stringify({ at: new Date().toISOString(), ...result, note: result.note?.path })}\n`,
    "utf8"
  );
  return result;
}

module.exports = { evolveOnce, evolveAndLog, extractThemes };
