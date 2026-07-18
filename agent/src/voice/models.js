"use strict";

const { config } = require("../config");

const DEFAULT_TTS = process.env.VOICEBOX_TTS_MODEL || "qwen-tts-1.7B";
const DEFAULT_STT = process.env.VOICEBOX_STT_MODEL || "whisper-base";

async function modelsStatus() {
  try {
    const res = await fetch(`${config.voicebox.url}/models/status`, {
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return { ok: false, status: res.status };
    const body = await res.json();
    const models = body.models || body || [];
    const list = Array.isArray(models) ? models : [];
    const tts = list.find((m) => m.model_name === DEFAULT_TTS);
    return {
      ok: true,
      models: list,
      ttsModel: DEFAULT_TTS,
      ttsLoaded: Boolean(tts?.loaded),
      ttsDownloaded: Boolean(tts?.downloaded),
      sttLoaded: Boolean(list.find((m) => m.model_name === DEFAULT_STT)?.loaded),
    };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

async function loadModel(modelName) {
  const res = await fetch(`${config.voicebox.url}/models/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model_name: modelName }),
    signal: AbortSignal.timeout(600_000),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body.detail || body.error || `load ${modelName} failed (${res.status})`);
  }
  return { ok: true, model: modelName, ...body };
}

module.exports = { modelsStatus, loadModel, DEFAULT_TTS, DEFAULT_STT };
