"use strict";

/**
 * Offline smoke test — mock LLM path, memory, and agent loop without live servers.
 */
const path = require("path");
const fs = require("fs");

process.env.TONY_LLM_PROVIDER = "mock";
process.env.TONY_DATA_DIR = path.join(__dirname, "..", "..", "data", "smoke");
process.env.TONY_VAULT_DIR = path.join(__dirname, "..", "..", "vault");

// clear require cache config after env
delete require.cache[require.resolve("../src/config")];

async function main() {
  const { runAgent } = require("../src/core/agent");
  const { rememberFact, recallFacts, memoryStats } = require("../src/memory/store");
  const { runDailyConsolidate } = require("../src/memory/learner");

  const hello = await runAgent("hello Tony");
  if (!hello.reply) throw new Error("empty hello reply");

  rememberFact("User likes dark mode", "preference", "smoke");
  const facts = recallFacts("dark");
  if (!facts.length) throw new Error("recall failed");

  const joke = await runAgent("tell me a joke");
  if (!/bug|dark|ticket|programmer/i.test(joke.reply)) {
    console.warn("joke reply unexpected but continuing:", joke.reply);
  }

  const learn = runDailyConsolidate();
  if (!fs.existsSync(learn.notePath)) throw new Error("daily note missing");

  console.log("SMOKE OK", {
    hello: hello.reply.slice(0, 80),
    provider: hello.provider,
    memory: memoryStats(),
    learn: learn.notePath,
  });
}

main().catch((err) => {
  console.error("SMOKE FAIL", err);
  process.exit(1);
});
