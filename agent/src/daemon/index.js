"use strict";

const { config } = require("../config");
const { runDailyConsolidate, writeIdleSkillNote } = require("../memory/learner");
const { acquireIdleSkill, skillsStats } = require("../skills/registry");
const { voiceboxHealth } = require("../voice/voicebox");
const { warmupVoicebox, modelsStatus } = require("../voice/warmup");
const { bridgeHealth } = require("../bridge/client");
const { llmHealth } = require("../llm/providers");
const { memoryStats } = require("../memory/store");
const { rebuildGraph, brainStats } = require("../brain/obsidian");

let lastLearnDay = "";

async function checkLayers() {
  const [llm, voice, bridge, mem, models] = await Promise.all([
    llmHealth(),
    voiceboxHealth(),
    bridgeHealth(),
    Promise.resolve(memoryStats()),
    modelsStatus(),
  ]);
  const report = {
    at: new Date().toISOString(),
    llm,
    voicebox: voice,
    models,
    bridge,
    memory: mem,
    skills: skillsStats(),
    brain: brainStats(),
  };
  console.log("[daemon] health", JSON.stringify(report));
  return report;
}

function maybeDailyLearn() {
  const now = new Date();
  const day = now.toISOString().slice(0, 10);
  const hour = now.getHours();
  if (hour === config.daemon.learnHour && lastLearnDay !== day) {
    lastLearnDay = day;
    const result = runDailyConsolidate();
    const skill = acquireIdleSkill();
    writeIdleSkillNote("daily_free_time");
    console.log("[daemon] daily learn", result, skill);
    return { result, skill };
  }
  return null;
}

function startDaemon() {
  console.log("[daemon] Tony learning daemon started");
  try {
    const boot = acquireIdleSkill();
    console.log("[daemon] boot skill tick", boot);
  } catch (err) {
    console.error("[daemon] boot skill failed", err.message);
  }

  // Rebuild Obsidian graph hourly-ish with health (and on boot)
  try {
    const g = rebuildGraph();
    console.log("[daemon] brain graph", g);
  } catch (err) {
    console.error("[daemon] brain graph failed", err.message);
  }

  // Pin Voicebox TTS in memory
  warmupVoicebox({ includeStt: true, pingSpeak: true })
    .then((r) => console.log("[daemon] voice warmup", JSON.stringify(r.message || r)))
    .catch((e) => console.error("[daemon] voice warmup", e.message));

  checkLayers().catch((e) => console.error("[daemon] health error", e.message));
  maybeDailyLearn();

  setInterval(() => {
    checkLayers().catch((e) => console.error("[daemon] health error", e.message));
    maybeDailyLearn();
    try {
      rebuildGraph();
    } catch {
      /* ignore */
    }
  }, config.daemon.healthMs);

  // Keep model loaded every 8 minutes
  setInterval(() => {
    warmupVoicebox({ includeStt: false, pingSpeak: false })
      .then((r) => console.log("[daemon] keep-warm", r.message || r.actions?.join(",")))
      .catch((e) => console.error("[daemon] keep-warm", e.message));
  }, 8 * 60 * 1000);

  setInterval(() => {
    try {
      const skill = acquireIdleSkill();
      const note = writeIdleSkillNote("periodic_idle");
      console.log("[daemon] idle skill", skill, note.notePath);
    } catch (err) {
      console.error("[daemon] idle skill failed", err.message);
    }
  }, 30 * 60 * 1000);
}

if (require.main === module) {
  startDaemon();
}

module.exports = { startDaemon, checkLayers, maybeDailyLearn };
