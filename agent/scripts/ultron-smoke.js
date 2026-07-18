"use strict";

/**
 * Ultron smoke — catalog, evolve, mock agent identity.
 */
const path = require("path");

process.env.TONY_LLM_PROVIDER = "mock";
process.env.TONY_DATA_DIR = path.join(__dirname, "..", "..", "data", "smoke-ultron");
process.env.TONY_VAULT_DIR = path.join(__dirname, "..", "..", "vault");

delete require.cache[require.resolve("../src/config")];

async function main() {
  const { CATALOG, ensureSeedInstalled, skillsStats, listCatalog } = require("../src/skills/registry");
  const { evolveAndLog } = require("../src/core/evolve");
  const { runAgent } = require("../src/core/agent");
  const { buildSystemPrompt } = require("../src/llm/persona");

  ensureSeedInstalled();
  const vibe = CATALOG.find((s) => s.id === "vibe_coding");
  const ultron = CATALOG.find((s) => s.id === "ultron_personal_os");
  if (!vibe || !ultron) throw new Error("missing vibe/ultron skills");

  const stats = skillsStats();
  if (stats.total < 50) throw new Error(`expected 50+ skills, got ${stats.total}`);

  const evolved = evolveAndLog();
  if (!evolved.ok) throw new Error("evolve failed");

  const prompt = buildSystemPrompt({ languageStyle: "roman_urdu", userMessage: "bhai vibe coding sikhao" });
  if (!/ULTRON/i.test(prompt) || !/Vibe coding/i.test(prompt)) {
    throw new Error("persona missing Ultron/vibe identity");
  }

  const reply = await runAgent("Bhai short batao tum Ultron ho?");
  if (!reply.reply) throw new Error("empty reply");

  const installedVibe = listCatalog().find((s) => s.id === "vibe_coding");
  if (!installedVibe?.installed) throw new Error("vibe_coding not installed");

  console.log("ULTRON SMOKE OK", {
    skills: stats.total,
    evolved: evolved.practiced,
    themes: evolved.themes,
    reply: reply.reply.slice(0, 120),
    provider: reply.provider,
  });
}

main().catch((err) => {
  console.error("ULTRON SMOKE FAIL", err);
  process.exit(1);
});
