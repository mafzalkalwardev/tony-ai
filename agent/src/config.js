"use strict";

const path = require("path");
const fs = require("fs");
const dotenv = require("dotenv");

const ROOT = path.resolve(__dirname, "..", "..");
dotenv.config({ path: path.join(ROOT, ".env") });

function env(key, fallback = "") {
  const v = process.env[key];
  return v === undefined || v === "" ? fallback : v;
}

function envInt(key, fallback) {
  const n = Number.parseInt(env(key, String(fallback)), 10);
  return Number.isFinite(n) ? n : fallback;
}

const dataDir = path.resolve(ROOT, env("TONY_DATA_DIR", "./data"));
const vaultDir = path.resolve(ROOT, env("TONY_VAULT_DIR", "./vault"));

for (const dir of [dataDir, vaultDir, path.join(vaultDir, "Agentic Brain")]) {
  fs.mkdirSync(dir, { recursive: true });
}

const config = {
  root: ROOT,
  port: envInt("TONY_PORT", 8787),
  apiToken: env("TONY_API_TOKEN", "tony-dev-token"),
  maxIterations: envInt("TONY_MAX_ITERATIONS", 8),
  userName: env("TONY_USER_NAME", "Friend"),
  companionMode: env("TONY_COMPANION_MODE", "true") === "true",
  persona: env(
    "TONY_PERSONA",
    "witty Jarvis-style assistant: expert at coding, research, writing, bug fixing; crack light jokes; stay helpful and local-first"
  ),
  llm: {
    provider: env("TONY_LLM_PROVIDER", "auto"),
    groqApiKey: env("GROQ_API_KEY"),
    groqModel: env("GROQ_MODEL", "llama-3.1-8b-instant"),
    ollamaBaseUrl: env("OLLAMA_BASE_URL", "http://localhost:11434"),
    ollamaModel: env("OLLAMA_MODEL", "qwen3:4b"),
  },
  voicebox: {
    url: env("VOICEBOX_URL", "http://127.0.0.1:17493").replace(/\/$/, ""),
    profile: env("VOICEBOX_PROFILE"),
    clientId: env("VOICEBOX_CLIENT_ID", "tony-ai"),
    engine: env("VOICEBOX_ENGINE", ""),
  },
  bridge: {
    url: env("TONY_BRIDGE_URL", "http://127.0.0.1:8790").replace(/\/$/, ""),
    token: env("TONY_BRIDGE_TOKEN", "tony-bridge-token"),
    workspace: env("TONY_BRIDGE_WORKSPACE", ROOT),
  },
  dataDir,
  vaultDir,
  daemon: {
    enabled: env("TONY_DAEMON_ENABLED", "true") === "true",
    healthMs: envInt("TONY_DAEMON_HEALTH_MS", 3_600_000),
    learnHour: envInt("TONY_DAEMON_LEARN_HOUR", 3),
  },
};

module.exports = { config, ROOT };
