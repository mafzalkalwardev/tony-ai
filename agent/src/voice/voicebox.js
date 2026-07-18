"use strict";

const { config } = require("../config");

/** Active speak profile override (HUD can change without restart). */
let activeProfile = config.voicebox.profile || "Farman";
/** Recent generation ids for Stop. */
const recentGenerations = [];

function getActiveProfile() {
  return activeProfile || config.voicebox.profile || "Farman";
}

function setActiveProfile(name) {
  activeProfile = String(name || "").trim() || config.voicebox.profile || "Farman";
  return { ok: true, profile: activeProfile };
}

function trackGeneration(id) {
  if (!id) return;
  recentGenerations.unshift(id);
  if (recentGenerations.length > 8) recentGenerations.length = 8;
}

function clipSpeakText(text) {
  const { toFriendSpeech } = require("./friendSpeech");
  const t = toFriendSpeech(text);
  const max = Number(process.env.VOICEBOX_MAX_CHARS || 280);
  if (t.length <= max) return t;
  return `${t.slice(0, max - 1).replace(/\s+\S*$/, "").trim()}…`;
}

async function voiceboxHealth() {
  try {
    const res = await fetch(`${config.voicebox.url}/profiles`, {
      signal: AbortSignal.timeout(2500),
    });
    if (!res.ok) {
      const docs = await fetch(`${config.voicebox.url}/docs`, { signal: AbortSignal.timeout(2000) });
      return { ok: docs.ok, status: res.status, via: docs.ok ? "docs" : "profiles" };
    }
    const profiles = await res.json().catch(() => []);
    const list = Array.isArray(profiles) ? profiles : profiles?.profiles || [];
    return {
      ok: true,
      profileCount: list.length,
      activeProfile: getActiveProfile(),
      profiles: list.map((p) => ({
        id: p.id,
        name: p.name || p.id,
        language: p.language,
        voice_type: p.voice_type,
      })),
    };
  } catch (err) {
    return { ok: false, error: err.message, activeProfile: getActiveProfile() };
  }
}

async function listProfiles() {
  const health = await voiceboxHealth();
  if (!health.ok) return { ok: false, error: health.error, profiles: [], activeProfile: getActiveProfile() };
  return {
    ok: true,
    profiles: health.profiles || [],
    activeProfile: getActiveProfile(),
  };
}

async function resolveProfile(preferred) {
  const name = preferred || getActiveProfile() || "";
  try {
    const res = await fetch(`${config.voicebox.url}/profiles`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) return { profile: name || undefined };
    const profiles = await res.json().catch(() => []);
    const list = Array.isArray(profiles) ? profiles : profiles?.profiles || [];
    if (!list.length) return { profile: name || undefined, warning: "no_profiles" };
    if (!name) {
      const first = list[0];
      return { profile: first.name || first.id, profileId: first.id };
    }
    const match = list.find(
      (p) =>
        String(p.name || "").toLowerCase() === name.toLowerCase() ||
        String(p.id || "") === name
    );
    if (match) return { profile: match.name || match.id, profileId: match.id };
    return { profile: name, warning: "profile_not_found", available: list.map((p) => p.name || p.id) };
  } catch {
    return { profile: name || undefined };
  }
}

async function getGeneration(generationId) {
  const res = await fetch(`${config.voicebox.url}/history/${encodeURIComponent(generationId)}`, {
    signal: AbortSignal.timeout(8000),
  });
  if (!res.ok) {
    // fallback: status SSE one-shot is unreliable; try JSON status via history only
    return { id: generationId, status: "unknown", error: `history ${res.status}` };
  }
  return res.json();
}

/**
 * Poll history until completed/failed. Avoids hanging on SSE streams.
 */
async function waitForGeneration(generationId, { timeoutMs = 420_000, onTick } = {}) {
  const started = Date.now();
  let last = { status: "generating", id: generationId };
  while (Date.now() - started < timeoutMs) {
    try {
      last = await getGeneration(generationId);
      if (typeof onTick === "function") onTick(last);
      const st = last.status || "unknown";
      if (st === "completed") return last;
      if (st === "failed" || st === "cancelled") {
        throw new Error(last.error || `Voicebox generation ${st}`);
      }
    } catch (err) {
      if (/Voicebox generation/.test(String(err.message || ""))) throw err;
    }
    await new Promise((r) => setTimeout(r, 2000));
  }
  throw new Error(`Voicebox timed out (${last.status || "unknown"})`);
}

/**
 * Cancel stuck/queued generations so Farman can speak again.
 */
async function clearSpeakQueue({ keepLatest = 0, onlyIfStuckCount = 0 } = {}) {
  const cancelled = [];
  try {
    const res = await fetch(`${config.voicebox.url}/history?limit=40`, {
      signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) return { ok: false, cancelled: 0, error: `history ${res.status}` };
    const body = await res.json();
    const items = Array.isArray(body) ? body : body.items || [];
    const stuck = items.filter((g) =>
      ["generating", "loading_model", "queued", "pending"].includes(String(g.status || ""))
    );
    if (onlyIfStuckCount > 0 && stuck.length < onlyIfStuckCount) {
      return { ok: true, cancelled: 0, skipped: true, stuck: stuck.length };
    }
    const toCancel = stuck.slice(keepLatest);
    for (const g of toCancel) {
      try {
        const c = await cancelGeneration(g.id);
        cancelled.push({ id: g.id, ...c });
      } catch (err) {
        cancelled.push({ id: g.id, ok: false, error: err.message });
      }
    }
    return { ok: true, cancelled: cancelled.length, items: cancelled };
  } catch (err) {
    return { ok: false, cancelled: cancelled.length, error: err.message };
  }
}

function inferEmotionInstruct(text) {
  const t = String(text || "").toLowerCase();
  if (/\b(sorry|sad|afsos|dukh|miss|condolence)\b/.test(t)) {
    return "soft, gentle, empathetic tone; slower pacing; warm and caring";
  }
  if (/\b(urgent|jaldi|quick|emergency|alert|warning|error|fail)\b/.test(t)) {
    return "urgent but calm; clear and focused; slightly faster pacing";
  }
  if (/\b(joke|mazak|haha|lol|funny|wit)\b/.test(t) || /[!]{2,}/.test(t)) {
    return "playful, witty, light smile in the voice; lively pacing; friendly Jarvis energy";
  }
  if (/\b(love|miss you|proud|shukriya|thanks|great|zabardast|awesome)\b/.test(t)) {
    return "warm, affectionate, upbeat; expressive and natural emotion";
  }
  if (/\b(salam|hello|hi |hey|assalam)\b/.test(t)) {
    return "warm greeting; friendly and confident; natural human emotion";
  }
  // Default: expressive companion — Farman was flat without instruct
  return [
    "talk like a close friend having a chat",
    "natural human emotion and expressiveness",
    "warm witty companion — not a robot reading text",
    "varied pacing and intonation — never monotone",
    "friendly, clear, slightly charismatic",
  ].join("; ");
}

async function queueVoiceboxSpeak(
  text,
  { profile, personality = true, wait = true, language = "en", instruct, emotion } = {}
) {
  const resolved = await resolveProfile(profile);
  const clipped = clipSpeakText(text);
  const style =
    instruct ||
    emotion ||
    process.env.VOICEBOX_INSTRUCT ||
    inferEmotionInstruct(clipped);

  // /generate supports instruct (emotion/style) + personality; /speak does not
  if (!resolved.profileId) {
    // fallback to /speak by name
    const payload = {
      text: clipped,
      profile: resolved.profile,
      personality: personality !== false,
      language: language || "en",
    };
    if (config.voicebox.engine) payload.engine = config.voicebox.engine;
    const res = await fetch(`${config.voicebox.url}/speak`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Voicebox-Client-Id": config.voicebox.clientId,
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(30_000),
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(body.detail || body.error || `Voicebox speak failed (${res.status})`);
    const generationId = body.id || body.generation_id;
    trackGeneration(generationId);
    let final = body;
    if (wait && generationId && (body.status === "generating" || body.status === "loading_model" || !body.audio_path)) {
      final = { ...body, ...(await waitForGeneration(generationId)) };
    }
    return {
      ok: true,
      provider: "voicebox",
      profile: resolved.profile,
      profileId: resolved.profileId,
      generationId,
      status: final.status || body.status,
      audioUrl: generationId ? `${config.voicebox.url}/audio/${generationId}` : null,
      instruct: style,
      personality: true,
      text: clipped,
      ...final,
    };
  }

  const payload = {
    profile_id: resolved.profileId,
    text: clipped,
    language: language || "en",
    personality: personality !== false,
    instruct: String(style).slice(0, 500),
    normalize: true,
  };
  if (config.voicebox.engine) payload.engine = config.voicebox.engine;

  const res = await fetch(`${config.voicebox.url}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Voicebox-Client-Id": config.voicebox.clientId,
    },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(30_000),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body.detail || body.error || `Voicebox generate failed (${res.status})`);
  }

  const generationId = body.id || body.generation_id;
  trackGeneration(generationId);

  let final = body;
  if (wait && generationId && (body.status === "generating" || body.status === "loading_model" || !body.audio_path)) {
    final = { ...body, ...(await waitForGeneration(generationId)) };
  }

  return {
    ok: true,
    provider: "voicebox",
    queued: !wait,
    playedLocally: true,
    profile: resolved.profile,
    profileId: resolved.profileId,
    generationId,
    status: final.status || body.status || "completed",
    audioUrl: generationId ? `${config.voicebox.url}/audio/${generationId}` : null,
    browserSpeak: false,
    instruct: style,
    personality: true,
    text: clipped,
    ...final,
  };
}

async function cancelGeneration(generationId) {
  const res = await fetch(`${config.voicebox.url}/generate/${encodeURIComponent(generationId)}/cancel`, {
    method: "POST",
    signal: AbortSignal.timeout(10_000),
  });
  const body = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, generationId, ...body };
}

/**
 * Stop Tony speaking: cancel recent Voicebox gens + best-effort stop hooks.
 */
async function stopSpeaking() {
  const results = [];
  const ids = [...recentGenerations];
  for (const id of ids) {
    try {
      results.push(await cancelGeneration(id));
    } catch (err) {
      results.push({ ok: false, generationId: id, error: err.message });
    }
  }
  // Cancel everything still generating so Stop always cuts Farman
  const cleared = await clearSpeakQueue({ keepLatest: 0, onlyIfStuckCount: 0 });
  for (const path of ["/speak/stop", "/audio/stop", "/playback/stop"]) {
    try {
      const res = await fetch(`${config.voicebox.url}${path}`, {
        method: "POST",
        signal: AbortSignal.timeout(2000),
      });
      if (res.ok) results.push({ ok: true, path });
    } catch {
      /* ignore */
    }
  }
  recentGenerations.length = 0;
  return {
    ok: true,
    stopped: true,
    cancelled: results.filter((r) => r.ok).length,
    queueCleared: cleared.cancelled || 0,
    results,
    hint: "Browser speech also cancelled from the HUD Stop button.",
  };
}

const { modelsStatus } = require("./models");
const { warmupVoicebox } = require("./warmup");

/**
 * Primary path: Farman (or selected) Voicebox voice.
 * Clears stuck queue, waits for audio on CPU, returns audioUrl for HUD playback.
 */
async function speak(text, opts = {}) {
  const profile = opts.profile || getActiveProfile();
  const errors = [];
  const clipped = clipSpeakText(text);
  if (!clipped) {
    return { ok: false, provider: "none", error: "empty text", browserSpeak: false };
  }

  let status = await modelsStatus();
  if (!status.ttsLoaded) {
    try {
      await warmupVoicebox({ includeStt: false, pingSpeak: false });
      status = await modelsStatus();
    } catch (err) {
      errors.push(`warmup: ${err.message}`);
    }
  }

  // Clear backlog only when it looks jammed (many stuck jobs)
  try {
    const q = await clearSpeakQueue({ keepLatest: 0, onlyIfStuckCount: 2 });
    if (q.cancelled) errors.push(`cleared:${q.cancelled}`);
  } catch (err) {
    errors.push(`clear_queue: ${err.message}`);
  }

  // On CPU, always wait so we only report success when audio exists
  const wait = opts.wait !== undefined ? Boolean(opts.wait) : true;

  // Retry speak once — Voicebox often flaps while loading 1.7B on CPU
  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      const vb = await queueVoiceboxSpeak(clipped, { ...opts, profile, wait });
      const ready = vb.status === "completed";
      return {
        ok: ready || Boolean(vb.generationId),
        provider: "voicebox",
        browserSpeak: !ready,
        profile: vb.profile,
        voicebox: vb,
        generationId: vb.generationId,
        audioUrl: vb.audioUrl,
        status: vb.status,
        modelWarm: Boolean(status.ttsLoaded),
        waitingForAudio: !ready,
        text: clipped,
        errors: errors.length ? errors : undefined,
      };
    } catch (err) {
      errors.push(`voicebox_try${attempt + 1}: ${err.message}`);
      await new Promise((r) => setTimeout(r, 1500));
      try {
        await warmupVoicebox({ includeStt: false, pingSpeak: false });
      } catch (warmErr) {
        errors.push(`rewarm: ${warmErr.message}`);
      }
    }
  }

  try {
    const { callPythonTool } = require("../bridge/client");
    const fb = await callPythonTool("tts_speak", { text: clipped });
    if (fb.ok && fb.spoken) {
      return {
        ok: true,
        provider: "python_tts",
        browserSpeak: false,
        profile,
        local: fb,
        errors,
        fallback: true,
      };
    }
    errors.push(`python_tts: ${fb.text || fb.error || "not spoken"}`);
  } catch (err) {
    errors.push(`python_tts: ${err.message}`);
  }

  return {
    ok: false,
    provider: "none",
    browserSpeak: true,
    profile,
    errors,
    error: errors.join("; ") || "speak failed — use browser fallback",
  };
}

async function transcribe(audioBuffer, { filename = "audio.wav", model = "whisper-turbo" } = {}) {
  const form = new FormData();
  const blob = new Blob([audioBuffer], { type: "application/octet-stream" });
  form.append("audio", blob, filename);
  form.append("model", model);

  const res = await fetch(`${config.voicebox.url}/transcribe`, {
    method: "POST",
    body: form,
    signal: AbortSignal.timeout(120_000),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body.detail || body.error || `Voicebox transcribe failed (${res.status})`);
  }
  const text = body.text || body.transcript || body.result || "";
  return { ok: true, provider: "voicebox", text, raw: body };
}

async function converseFallbackViaBridge(audioBase64, mimeType) {
  const { callPythonTool } = require("../bridge/client");
  return callPythonTool("voice_converse_fallback", {
    audioBase64,
    mimeType,
  });
}

async function proxyAudio(generationId) {
  const res = await fetch(`${config.voicebox.url}/audio/${encodeURIComponent(generationId)}`, {
    signal: AbortSignal.timeout(60_000),
  });
  if (!res.ok) {
    const err = await res.text().catch(() => "");
    throw new Error(err || `audio ${res.status}`);
  }
  const buf = Buffer.from(await res.arrayBuffer());
  const type = res.headers.get("content-type") || "audio/wav";
  return { buf, type };
}

module.exports = {
  voiceboxHealth,
  speak,
  stopSpeaking,
  listProfiles,
  setActiveProfile,
  getActiveProfile,
  transcribe,
  converseFallbackViaBridge,
  resolveProfile,
  queueVoiceboxSpeak,
  waitForGeneration,
  getGeneration,
  clearSpeakQueue,
  cancelGeneration,
  proxyAudio,
  clipSpeakText,
  inferEmotionInstruct,
};
