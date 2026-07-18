"use strict";

const fs = require("fs");
const path = require("path");
const { config } = require("../config");

function ensureDirs() {
  fs.mkdirSync(config.dataDir, { recursive: true });
}

function paths() {
  ensureDirs();
  return {
    episodic: path.join(config.dataDir, "episodic.jsonl"),
    semantic: path.join(config.dataDir, "semantic.json"),
    profile: path.join(config.dataDir, "profile.json"),
    learnRuns: path.join(config.dataDir, "learn_runs.jsonl"),
  };
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

function appendJsonl(file, row) {
  fs.appendFileSync(file, JSON.stringify(row) + "\n", "utf8");
}

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs
    .readFileSync(file, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

function nowIso() {
  return new Date().toISOString().replace("T", " ").slice(0, 19);
}

function logEpisodic(role, content, meta = {}) {
  appendJsonl(paths().episodic, {
    id: Date.now() + Math.random(),
    role,
    content,
    meta,
    created_at: nowIso(),
  });
}

function recentEpisodic(limit = 20) {
  const rows = readJsonl(paths().episodic);
  return rows.slice(-limit);
}

function rememberFact(fact, category = "general", source = "conversation") {
  const clean = String(fact || "").trim();
  if (!clean) return { ok: false, error: "empty fact" };
  const blocked = /(password|api[_ ]?key|secret|otp|token\s*=|bearer\s+)/i;
  if (blocked.test(clean)) return { ok: false, error: "refused: looks like a secret" };
  const p = paths();
  const list = readJson(p.semantic, []);
  const row = {
    id: list.length ? Math.max(...list.map((x) => x.id || 0)) + 1 : 1,
    fact: clean,
    category,
    source,
    created_at: nowIso(),
  };
  list.push(row);
  writeJson(p.semantic, list);
  return { ok: true, id: row.id, fact: clean };
}

function recallFacts(query = "", limit = 10) {
  const list = readJson(paths().semantic, []);
  const q = String(query || "").trim().toLowerCase();
  const filtered = q ? list.filter((f) => String(f.fact).toLowerCase().includes(q)) : list;
  return filtered.slice(-limit).reverse();
}

function setProfile(key, value) {
  const p = paths();
  const obj = readJson(p.profile, {});
  obj[key] = { value: String(value), updated_at: nowIso() };
  writeJson(p.profile, obj);
  return { ok: true, key, value: String(value) };
}

function getProfile(key) {
  const obj = readJson(paths().profile, {});
  if (key) {
    const row = obj[key];
    return row ? { key, value: row.value, updated_at: row.updated_at } : null;
  }
  return Object.entries(obj).map(([k, v]) => ({ key: k, value: v.value, updated_at: v.updated_at }));
}

function memoryHints() {
  const facts = recallFacts("", 8).map((f) => f.fact);
  const name = getProfile("preferred_name");
  if (name?.value) facts.unshift(`Preferred name: ${name.value}`);
  return facts;
}

function episodicSince(isoDate) {
  return readJsonl(paths().episodic).filter((r) => String(r.created_at) >= isoDate);
}

function recordLearnRun(summary, factsAdded, notePath) {
  appendJsonl(paths().learnRuns, {
    summary,
    facts_added: factsAdded,
    note_path: notePath || null,
    created_at: nowIso(),
  });
}

function memoryStats() {
  const p = paths();
  return {
    episodic: readJsonl(p.episodic).length,
    semantic: readJson(p.semantic, []).length,
    profile: Object.keys(readJson(p.profile, {})).length,
    learnRuns: readJsonl(p.learnRuns).length,
    dataDir: config.dataDir,
    backend: "jsonl",
  };
}

module.exports = {
  logEpisodic,
  recentEpisodic,
  rememberFact,
  recallFacts,
  setProfile,
  getProfile,
  memoryHints,
  episodicSince,
  recordLearnRun,
  memoryStats,
};
