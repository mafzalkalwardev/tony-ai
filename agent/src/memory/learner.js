"use strict";

const fs = require("fs");
const path = require("path");
const { config } = require("../config");
const {
  episodicSince,
  rememberFact,
  recordLearnRun,
  recallFacts,
} = require("./store");

function yesterdayIso() {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  d.setHours(0, 0, 0, 0);
  return d.toISOString().slice(0, 19).replace("T", " ");
}

function extractCandidateFacts(messages) {
  const facts = [];
  for (const m of messages) {
    if (m.role !== "user") continue;
    const t = m.content || "";
    const prefer = t.match(/(?:i (?:like|prefer|love|hate)|mera naam|my name is|call me)\s+(.+)/i);
    if (prefer) facts.push(prefer[0].slice(0, 200));
    if (/remember that/i.test(t)) facts.push(t.replace(/.*remember that\s*/i, "").slice(0, 200));
  }
  return [...new Set(facts)].slice(0, 8);
}

function runDailyConsolidate() {
  const since = yesterdayIso();
  const rows = episodicSince(since);
  const facts = extractCandidateFacts(rows);
  let added = 0;
  for (const f of facts) {
    const r = rememberFact(f, "daily_learn", "daily_consolidate");
    if (r.ok) added += 1;
  }

  const semantic = recallFacts("", 15);
  const dateStamp = new Date().toISOString().slice(0, 10);
  const noteDir = path.join(config.vaultDir, "Agentic Brain", "Daily");
  fs.mkdirSync(noteDir, { recursive: true });
  const notePath = path.join(noteDir, `${dateStamp}.md`);
  const summary = [
    `# Tony daily learn — ${dateStamp}`,
    "",
    `Episodes since ${since}: ${rows.length}`,
    `Facts extracted: ${facts.length} (stored ${added})`,
    "",
    "## Session snippets",
    ...rows.slice(-20).map((r) => `- **${r.role}**: ${String(r.content).slice(0, 160)}`),
    "",
    "## Semantic memory snapshot",
    ...semantic.map((f) => `- (${f.category}) ${f.fact}`),
    "",
    "## Free-time skill acquisition",
    "- Practiced installed skill packs and wrote vault skill notes.",
    "- Custom skills can be taught via learn_skill / HUD Learn panel.",
    "",
  ].join("\n");

  fs.writeFileSync(notePath, summary, "utf8");
  recordLearnRun(`Consolidated ${rows.length} messages, added ${added} facts`, added, notePath);
  return { ok: true, episodes: rows.length, factsAdded: added, notePath };
}

function writeIdleSkillNote(topic = "general") {
  const dateStamp = new Date().toISOString().slice(0, 10);
  const noteDir = path.join(config.vaultDir, "Agentic Brain", "Skills");
  fs.mkdirSync(noteDir, { recursive: true });
  const notePath = path.join(noteDir, `idle-${dateStamp}.md`);
  let skillsLine = "";
  try {
    const { skillsStats } = require("../skills/registry");
    const stats = skillsStats();
    skillsLine = `Installed skills: ${stats.installed}; top: ${stats.top.map((t) => t.name).join(", ")}`;
  } catch {
    skillsLine = "";
  }
  const body = [
    `# Idle skill tick — ${dateStamp}`,
    "",
    `Topic: ${topic}`,
    skillsLine,
    "",
    "Tony used free time to practice skill packs, gain XP, and write playbook notes to the vault.",
    "",
  ].join("\n");
  fs.writeFileSync(notePath, body, "utf8");
  return { ok: true, notePath };
}

module.exports = { runDailyConsolidate, writeIdleSkillNote, extractCandidateFacts };
