"use strict";

const { DEFAULT_TTS, DEFAULT_STT, modelsStatus, loadModel } = require("./models");

/**
 * Ensure Farman TTS model stays resident in Voicebox memory.
 */
async function warmupVoicebox({ includeStt = true, pingSpeak = true } = {}) {
  const before = await modelsStatus();
  if (!before.ok) {
    return { ok: false, error: before.error || "Voicebox unreachable — open the Voicebox app" };
  }

  const { config } = require("../config");
  const actions = [];

  if (!before.ttsDownloaded) {
    try {
      await fetch(`${config.voicebox.url}/models/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model_name: DEFAULT_TTS }),
        signal: AbortSignal.timeout(30_000),
      });
      actions.push(`download:${DEFAULT_TTS}`);
    } catch (err) {
      actions.push(`download_failed:${err.message}`);
    }
  }

  try {
    await loadModel(DEFAULT_TTS);
    actions.push(before.ttsLoaded ? `keep:${DEFAULT_TTS}` : `load:${DEFAULT_TTS}`);
  } catch (err) {
    actions.push(`load_failed:${err.message}`);
    return { ok: false, actions, error: err.message, before };
  }

  if (includeStt) {
    try {
      await loadModel(DEFAULT_STT);
      actions.push(`load:${DEFAULT_STT}`);
    } catch (err) {
      actions.push(`stt_skip:${err.message}`);
    }
  }

  if (pingSpeak) {
    try {
      // Don't enqueue real TTS during warmup — it jammed Farman's queue on CPU.
      actions.push("prompt_warm:skipped");
    } catch (err) {
      actions.push(`prompt_warm_skip:${err.message}`);
    }
  }

  const after = await modelsStatus();
  return {
    ok: Boolean(after.ttsLoaded),
    actions,
    before,
    after,
    message: after.ttsLoaded
      ? `${DEFAULT_TTS} is loaded and kept warm`
      : `${DEFAULT_TTS} warm-up attempted`,
  };
}

module.exports = {
  warmupVoicebox,
  modelsStatus,
  loadModel,
  DEFAULT_TTS,
  DEFAULT_STT,
};
