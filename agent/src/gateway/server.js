"use strict";

const http = require("http");
const path = require("path");
const express = require("express");
const { WebSocketServer } = require("ws");
const { config } = require("../config");
const { runAgent } = require("../core/agent");
const { llmHealth } = require("../llm/providers");
const { memoryStats } = require("../memory/store");
const {
  voiceboxHealth,
  speak,
  transcribe,
  converseFallbackViaBridge,
  listProfiles,
  setActiveProfile,
  getActiveProfile,
  stopSpeaking,
  getGeneration,
  clearSpeakQueue,
  proxyAudio,
} = require("../voice/voicebox");
const { bridgeHealth } = require("../bridge/client");
const { listCatalog, learnSkill, installSkill, installAllCatalog, skillsStats, acquireIdleSkill } = require("../skills/registry");
const { warmupVoicebox, modelsStatus } = require("../voice/warmup");
const { rebuildGraph, brainStats, searchBrain, relatedNodes } = require("../brain/obsidian");

function auth(req, res, next) {
  const header = req.headers.authorization || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : req.query.token || "";
  if (token !== config.apiToken) {
    return res.status(401).json({ error: "unauthorized" });
  }
  return next();
}

function createApp() {
  const app = express();
  app.use(express.json({ limit: "25mb" }));
  app.use(express.static(path.join(__dirname, "..", "..", "public")));

  app.get("/health", async (_req, res) => {
    const [llm, voice, bridge, mem, models] = await Promise.all([
      llmHealth(),
      voiceboxHealth(),
      bridgeHealth(),
      Promise.resolve(memoryStats()),
      modelsStatus(),
    ]);
    res.json({
      ok: true,
      service: "tony-gateway",
      port: config.port,
      user: config.userName,
      layers: {
        mind: llm,
        voicebox: { ...voice, models },
        bridge,
        memory: mem,
        skills: skillsStats(),
        brain: brainStats(),
      },
    });
  });

  app.get("/api/brain", auth, (_req, res) => {
    res.json({ ok: true, ...brainStats() });
  });

  app.post("/api/brain/rebuild", auth, (_req, res) => {
    res.json(rebuildGraph());
  });

  app.get("/api/brain/search", auth, (req, res) => {
    res.json(searchBrain(String(req.query.q || ""), { limit: Number(req.query.limit) || 8 }));
  });

  app.get("/api/brain/graph", auth, (req, res) => {
    res.json(relatedNodes(String(req.query.q || ""), { limit: Number(req.query.limit) || 16 }));
  });

  app.post("/api/voice/warmup", auth, async (_req, res) => {
    try {
      const out = await warmupVoicebox({ includeStt: true, pingSpeak: true });
      res.json(out);
    } catch (err) {
      res.status(500).json({ ok: false, error: err.message });
    }
  });

  app.get("/api/voice/models", auth, async (_req, res) => {
    res.json(await modelsStatus());
  });

  app.get("/api/skills", auth, (_req, res) => {
    res.json({ ok: true, skills: listCatalog(), stats: skillsStats() });
  });

  app.post("/api/skills/learn", auth, (req, res) => {
    const result = learnSkill({
      name: req.body?.name,
      summary: req.body?.summary,
      playbook: req.body?.playbook,
      from: "api",
    });
    const status = result.ok ? 200 : 400;
    res.status(status).json(result);
  });

  app.post("/api/skills/install", auth, (req, res) => {
    const result = installSkill(req.body?.id);
    const status = result.ok ? 200 : 400;
    res.status(status).json(result);
  });

  app.post("/api/skills/install-all", auth, (_req, res) => {
    res.json(installAllCatalog());
  });

  app.post("/api/skills/idle", auth, (_req, res) => {
    res.json(acquireIdleSkill());
  });

  app.post("/api/chat", auth, async (req, res) => {
    try {
      const message = String(req.body?.message || "").trim();
      if (!message) return res.status(400).json({ error: "message required" });
      const speakReply = Boolean(req.body?.speak);
      const result = await runAgent(message, { source: "http", speakReply });
      res.json({ ok: true, ...result });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/voice/converse", auth, async (req, res) => {
    try {
      const { audioBase64, mimeType = "audio/wav", speak: speakOut = true } = req.body || {};
      if (!audioBase64) return res.status(400).json({ error: "audioBase64 required" });

      let transcript = "";
      let sttProvider = "voicebox";
      const vb = await voiceboxHealth();
      if (vb.ok) {
        const buf = Buffer.from(audioBase64, "base64");
        const ext = String(mimeType).includes("webm") ? "webm" : "wav";
        const tr = await transcribe(buf, { filename: `converse.${ext}` });
        transcript = tr.text || "";
      } else {
        sttProvider = "python_fallback";
        const fb = await converseFallbackViaBridge(audioBase64, mimeType);
        if (!fb.ok) {
          return res.status(503).json({
            error: "Voicebox down and Python voice fallback failed",
            voicebox: vb,
            fallback: fb,
          });
        }
        transcript = fb.transcript || fb.text || "";
        if (fb.reply && !speakOut) {
          return res.json({
            ok: true,
            transcript,
            sttProvider,
            reply: fb.reply,
            speech: fb.speech || null,
          });
        }
        if (fb.reply) {
          let speech = fb.speech || null;
          if (speakOut && !speech) {
            try {
              speech = await speak(fb.reply);
            } catch {
              /* ignore */
            }
          }
          return res.json({ ok: true, transcript, sttProvider, reply: fb.reply, speech });
        }
      }

      if (!transcript.trim()) {
        return res.status(400).json({ error: "empty transcript", sttProvider });
      }

      const result = await runAgent(transcript, { source: "voice", speakReply: Boolean(speakOut) });
      res.json({ ok: true, transcript, sttProvider, ...result });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/voice/speak", auth, async (req, res) => {
    try {
      const text = String(req.body?.text || "").trim();
      if (!text) return res.status(400).json({ error: "text required" });
      const wait = req.body?.wait === true; // default false — HUD polls + plays audio
      const out = await speak(text, {
        profile: req.body?.profile || getActiveProfile(),
        wait,
      });
      res.json(out);
    } catch (err) {
      res.status(502).json({ error: err.message });
    }
  });

  app.get("/api/voice/generation/:id", auth, async (req, res) => {
    try {
      const gen = await getGeneration(req.params.id);
      res.json({
        ok: true,
        ...gen,
        audioUrl: `/api/voice/audio/${req.params.id}?token=${encodeURIComponent(config.apiToken)}`,
      });
    } catch (err) {
      // Keep polling alive during heavy CPU TTS
      res.status(200).json({
        ok: false,
        id: req.params.id,
        status: "generating",
        error: err.message,
        soft: true,
      });
    }
  });

  app.get("/api/voice/audio/:id", auth, async (req, res) => {
    try {
      const { buf, type } = await proxyAudio(req.params.id);
      res.setHeader("Content-Type", type);
      res.setHeader("Cache-Control", "no-store");
      res.send(buf);
    } catch (err) {
      res.status(502).json({ error: err.message });
    }
  });

  app.post("/api/voice/clear-queue", auth, async (_req, res) => {
    try {
      res.json(await clearSpeakQueue());
    } catch (err) {
      res.status(500).json({ ok: false, error: err.message });
    }
  });

  app.get("/api/voice/profiles", auth, async (_req, res) => {
    const out = await listProfiles();
    res.status(out.ok ? 200 : 503).json(out);
  });

  app.post("/api/voice/profile", auth, (req, res) => {
    const name = req.body?.profile || req.body?.name;
    if (!name) return res.status(400).json({ error: "profile required" });
    res.json(setActiveProfile(name));
  });

  app.post("/api/voice/stop", auth, async (_req, res) => {
    try {
      const out = await stopSpeaking();
      res.json(out);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.get("/api/memory/stats", auth, (_req, res) => {
    res.json(memoryStats());
  });

  return app;
}

function startGateway() {
  const app = createApp();
  const server = http.createServer(app);
  const wss = new WebSocketServer({ server, path: "/ws" });

  wss.on("connection", (socket, req) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const token = url.searchParams.get("token") || "";
    if (token !== config.apiToken) {
      socket.close(1008, "unauthorized");
      return;
    }
    socket.send(JSON.stringify({ type: "hello", service: "tony-gateway" }));

    socket.on("message", async (raw) => {
      let msg;
      try {
        msg = JSON.parse(String(raw));
      } catch {
        socket.send(JSON.stringify({ type: "error", error: "invalid json" }));
        return;
      }
      try {
        if (msg.type === "chat") {
          const result = await runAgent(msg.message || "", {
            source: "ws",
            speakReply: Boolean(msg.speak),
          });
          socket.send(JSON.stringify({ type: "chat_result", ...result }));
          return;
        }
        if (msg.type === "voice") {
          // reuse HTTP logic via agent after STT
          const vb = await voiceboxHealth();
          let transcript = "";
          if (vb.ok && msg.audioBase64) {
            const buf = Buffer.from(msg.audioBase64, "base64");
            const tr = await transcribe(buf);
            transcript = tr.text || "";
          }
          if (!transcript) {
            socket.send(JSON.stringify({ type: "error", error: "could not transcribe" }));
            return;
          }
          const result = await runAgent(transcript, { source: "ws-voice", speakReply: true });
          socket.send(JSON.stringify({ type: "voice_result", transcript, ...result }));
          return;
        }
        socket.send(JSON.stringify({ type: "error", error: `unknown type ${msg.type}` }));
      } catch (err) {
        socket.send(JSON.stringify({ type: "error", error: err.message }));
      }
    });
  });

  server.listen(config.port, () => {
    console.log(`[tony] gateway listening on http://localhost:${config.port}`);
    console.log(`[tony] HUD: http://localhost:${config.port}/`);
    console.log(`[tony] health: http://localhost:${config.port}/health`);
    // Keep Farman TTS model resident
    warmupVoicebox({ includeStt: true, pingSpeak: true })
      .then((r) => console.log("[tony] voice warmup", r.message || r.error || r))
      .catch((e) => console.warn("[tony] voice warmup failed", e.message));
    setInterval(() => {
      warmupVoicebox({ includeStt: false, pingSpeak: false })
        .then((r) => console.log("[tony] voice keep-warm", r.message || r.actions?.join(",")))
        .catch((e) => console.warn("[tony] keep-warm failed", e.message));
    }, 10 * 60 * 1000);
  });

  return server;
}

if (require.main === module) {
  startGateway();
}

module.exports = { createApp, startGateway };
