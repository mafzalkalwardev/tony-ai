(() => {
  const log = document.getElementById("log");
  const form = document.getElementById("form");
  const message = document.getElementById("message");
  const tokenInput = document.getElementById("token");
  const speakBox = document.getElementById("speak");
  const micBtn = document.getElementById("mic");
  const micLabel = document.getElementById("micLabel");
  const micState = document.getElementById("micState");
  const chips = document.getElementById("chips");
  const skillsList = document.getElementById("skillsList");
  const learnForm = document.getElementById("learnForm");
  const voiceSelect = document.getElementById("voiceProfile");
  const btnStop = document.getElementById("btnStop");
  const waveCanvas = document.getElementById("wave");
  const graphCanvas = document.getElementById("graphCanvas");
  const brainStatsEl = document.getElementById("brainStats");
  let waveAnimId = 0;
  let waveLevel = 0.15;
  let recordingAudio = null;
  let analyser = null;

  tokenInput.value = localStorage.getItem("tony_api_token") || "tony-dev-token";
  const savedVoice = localStorage.getItem("tony_voice_profile") || "Farman";

  function token() {
    const t = tokenInput.value.trim();
    localStorage.setItem("tony_api_token", t);
    return t;
  }
  function authHeaders() {
    return { Authorization: `Bearer ${token()}`, "Content-Type": "application/json" };
  }
  function selectedVoice() {
    return (voiceSelect?.value || savedVoice || "Farman").trim();
  }

  async function syncVoiceProfile(name) {
    const profile = name || selectedVoice();
    localStorage.setItem("tony_voice_profile", profile);
    try {
      await fetch("/api/voice/profile", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ profile }),
      });
    } catch { /* ignore */ }
    return profile;
  }

  async function loadProfiles() {
    try {
      const data = await (await fetch("/api/voice/profiles", { headers: authHeaders() })).json();
      const profiles = data.profiles || [];
      const active = data.activeProfile || savedVoice || "Farman";
      voiceSelect.innerHTML = "";
      if (!profiles.length) {
        const opt = document.createElement("option");
        opt.value = active;
        opt.textContent = active + " (offline?)";
        voiceSelect.appendChild(opt);
      } else {
        for (const p of profiles) {
          const opt = document.createElement("option");
          opt.value = p.name || p.id;
          opt.textContent = p.name || p.id;
          if ((p.name || p.id) === active) opt.selected = true;
          voiceSelect.appendChild(opt);
        }
        if (![...voiceSelect.options].some((o) => o.value === active)) {
          voiceSelect.value = profiles[0].name || profiles[0].id;
        }
      }
      await syncVoiceProfile(voiceSelect.value);
    } catch {
      voiceSelect.innerHTML = `<option value="Farman">Farman</option>`;
    }
  }

  voiceSelect?.addEventListener("change", () => {
    syncVoiceProfile(voiceSelect.value);
    micState.textContent = `Voice → ${voiceSelect.value}`;
  });

  btnStop?.addEventListener("click", async () => {
    try {
      speechSynthesis.cancel();
    } catch { /* ignore */ }
    try {
      if (farmanAudio) {
        farmanAudio.pause();
        farmanAudio = null;
      }
    } catch { /* ignore */ }
    micState.textContent = "Stopping…";
    try {
      const data = await (await fetch("/api/voice/stop", { method: "POST", headers: authHeaders() })).json();
      micState.textContent = data.ok ? "Stopped" : "Stop failed";
      addBubble("tony", "Stopped speaking.", "voice");
    } catch (err) {
      micState.textContent = `Stop: ${err.message}`;
    }
  });

  function drawWave() {
    if (!waveCanvas) return;
    const ctx = waveCanvas.getContext("2d");
    const w = waveCanvas.width;
    const h = waveCanvas.height;
    ctx.clearRect(0, 0, w, h);
    const bars = 14;
    const gap = 2;
    const bw = (w - gap * (bars - 1)) / bars;
    for (let i = 0; i < bars; i += 1) {
      const n = Math.sin(Date.now() / 180 + i * 0.55) * 0.5 + 0.5;
      const amp = Math.max(0.08, waveLevel) * (0.45 + n * 0.55);
      const bh = Math.max(3, h * amp);
      const x = i * (bw + gap);
      const y = (h - bh) / 2;
      ctx.fillStyle = recordingAudio ? "rgba(224,122,122,0.9)" : "rgba(110,214,198,0.75)";
      ctx.fillRect(x, y, bw, bh);
    }
    waveAnimId = requestAnimationFrame(drawWave);
  }
  drawWave();

  function drawGraph(payload) {
    if (!graphCanvas) return;
    const ctx = graphCanvas.getContext("2d");
    const w = graphCanvas.width;
    const h = graphCanvas.height;
    ctx.clearRect(0, 0, w, h);
    const nodes = (payload?.nodes || []).slice(0, 18);
    if (!nodes.length) {
      ctx.fillStyle = "rgba(127,158,152,0.8)";
      ctx.font = "12px IBM Plex Mono, monospace";
      ctx.fillText("No graph nodes yet — Rebuild", 16, h / 2);
      return;
    }
    const placed = nodes.map((n, i) => {
      const a = (i / nodes.length) * Math.PI * 2;
      const r = 38 + (i % 3) * 14;
      return {
        ...n,
        x: w / 2 + Math.cos(a) * r,
        y: h / 2 + Math.sin(a) * r * 0.7,
      };
    });
    const byId = Object.fromEntries(placed.map((p) => [p.id, p]));
    ctx.strokeStyle = "rgba(110,214,198,0.25)";
    for (const e of (payload.edges || []).slice(0, 40)) {
      const a = byId[e.from];
      const b = byId[e.to];
      if (!a || !b) continue;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    }
    for (const n of placed) {
      ctx.beginPath();
      ctx.fillStyle = n.type === "note" ? "#6ed6c6" : n.type === "tag" ? "#d4a574" : "rgba(232,246,243,0.7)";
      ctx.arc(n.x, n.y, n.type === "note" ? 4.5 : 3, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  async function refreshBrain() {
    try {
      const stats = await (await fetch("/api/brain", { headers: authHeaders() })).json();
      if (brainStatsEl) {
        brainStatsEl.textContent = `${stats.notes || 0} notes · ${stats.nodeCount || 0} nodes · ${stats.edgeCount || 0} edges`;
      }
      const g = await (await fetch("/api/brain/graph?q=tony&limit=16", { headers: authHeaders() })).json();
      drawGraph(g);
    } catch (err) {
      if (brainStatsEl) brainStatsEl.textContent = `Brain: ${err.message}`;
    }
  }

  document.getElementById("btnBrainRebuild")?.addEventListener("click", async () => {
    try {
      const data = await (await fetch("/api/brain/rebuild", { method: "POST", headers: authHeaders() })).json();
      addBubble("tony", `Brain rebuilt: ${data.notes} notes, ${data.nodeCount} nodes`, "brain");
      refreshBrain();
    } catch (err) {
      addBubble("tony", `Brain rebuild failed: ${err.message}`);
    }
  });

  // Particle field
  const canvas = document.getElementById("field");
  const ctx = canvas.getContext("2d");
  let parts = [];
  function resize() {
    canvas.width = innerWidth * devicePixelRatio;
    canvas.height = innerHeight * devicePixelRatio;
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    parts = Array.from({ length: 48 }, () => ({
      x: Math.random() * innerWidth,
      y: Math.random() * innerHeight,
      r: Math.random() * 1.6 + 0.4,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
    }));
  }
  resize();
  addEventListener("resize", resize);
  (function tick() {
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    for (const p of parts) {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > innerWidth) p.vx *= -1;
      if (p.y < 0 || p.y > innerHeight) p.vy *= -1;
      ctx.beginPath();
      ctx.fillStyle = "rgba(110,214,198,0.35)";
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(tick);
  })();

  if (window.gsap) {
    gsap.from(".topbar", { y: -20, opacity: 0, duration: 0.6, ease: "power3.out" });
    gsap.from(".workspace", { y: 16, opacity: 0, duration: 0.7, delay: 0.08, ease: "power3.out" });
    gsap.from(".control", { y: 24, opacity: 0, duration: 0.65, delay: 0.15, ease: "power3.out" });
    gsap.to("#arcProgress", { rotation: 360, transformOrigin: "32px 32px", duration: 14, repeat: -1, ease: "none" });
    gsap.to(".o1", { x: 30, y: 20, duration: 7, yoyo: true, repeat: -1, ease: "sine.inOut" });
    gsap.to(".o2", { x: -24, y: -18, duration: 8, yoyo: true, repeat: -1, ease: "sine.inOut" });
  }

  function addBubble(role, text, meta) {
    const div = document.createElement("div");
    div.className = `bubble ${role === "user" ? "user" : "tony"}`;
    if (meta) {
      const m = document.createElement("span");
      m.className = "meta";
      m.textContent = meta;
      div.appendChild(m);
    }
    div.appendChild(document.createTextNode(text));
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    if (window.gsap) gsap.from(div, { y: 8, opacity: 0, duration: 0.3 });
  }

  function browserSpeak(text) {
    try {
      if (!speechSynthesis || !text) return;
      speechSynthesis.cancel();
      speechSynthesis.speak(new SpeechSynthesisUtterance(text));
    } catch { /* ignore */ }
  }

  let farmanAudio = null;
  async function playFarmanAudio(generationId) {
    if (!generationId) return false;
    const url = `/api/voice/audio/${encodeURIComponent(generationId)}?token=${encodeURIComponent(token())}`;
    try {
      if (farmanAudio) {
        farmanAudio.pause();
        farmanAudio = null;
      }
      farmanAudio = new Audio(url);
      await farmanAudio.play();
      return true;
    } catch (err) {
      micState.textContent = `Audio play: ${err.message}`;
      return false;
    }
  }

  async function waitAndPlayFarman(speech, reply) {
    const gid = speech?.generationId || speech?.voicebox?.generationId;
    if (!gid) {
      browserSpeak(reply);
      addBubble("tony", "(browser voice — no Farman job)", "audio");
      return;
    }
    // CPU TTS blocks Voicebox for minutes — talk now, swap to Farman when ready
    browserSpeak(reply);
    addBubble("tony", "(interim voice… Farman WAV load ho raha hai)", "voicebox");
    micState.textContent = "Farman synthesizing…";
    const started = Date.now();
    while (Date.now() - started < 420000) {
      try {
        const st = await (await fetch(`/api/voice/generation/${encodeURIComponent(gid)}`, { headers: authHeaders() })).json();
        if (st.soft) {
          await new Promise((r) => setTimeout(r, 3000));
          continue;
        }
        if (st.status === "completed") {
          try { speechSynthesis.cancel(); } catch { /* ignore */ }
          const played = await playFarmanAudio(gid);
          micState.textContent = played ? `Speaking as ${speech.profile || selectedVoice()}` : "Farman ready";
          addBubble("tony", played ? `(Farman voice playing)` : "(Farman WAV ready — click allow audio)", "voicebox");
          return;
        }
        if (st.status === "failed" || st.status === "cancelled") {
          micState.textContent = "Farman failed — browser voice used";
          return;
        }
        micState.textContent = `Farman… ${st.status || "working"}`;
      } catch {
        /* Voicebox often times out mid-CPU synth — keep waiting */
      }
      await new Promise((r) => setTimeout(r, 3000));
    }
    micState.textContent = "Farman timeout — browser voice used";
  }

  function ensureVoice(reply, speech) {
    if (!speakBox.checked || !reply) return;
    if (speech && speech.provider === "voicebox" && (speech.generationId || speech.voicebox?.generationId)) {
      waitAndPlayFarman(speech, reply);
      return;
    }
    if (speech && speech.ok && speech.provider === "python_tts") {
      addBubble("tony", "(Windows TTS — Farman/Voicebox down)", "audio");
      // If bridge didn't actually play, still hear something
      if (!speech.local?.spoken) browserSpeak(reply);
      return;
    }
    if (speech && speech.browserSpeak) {
      browserSpeak(reply);
      addBubble("tony", "(browser fallback — Voicebox busy/down)", "audio");
      return;
    }
    browserSpeak(reply);
    addBubble("tony", "(browser voice)", "audio");
  }

  function renderChips(data) {
    const mind = data.layers?.mind || {};
    const vb = data.layers?.voicebox || {};
    const br = data.layers?.bridge || {};
    const sk = data.layers?.skills || {};
    const warm = vb.models?.ttsLoaded;
    const brain = data.layers?.brain || {};
    const items = [
      ["Mind", mind.activeFallback === "groq" || mind.activeFallback === "ollama", mind.activeFallback || "?"],
      ["Voice", !!vb.ok, vb.ok ? (warm ? "warm" : "cold") : "down"],
      ["Desktop", !!br.ok, br.ok ? "online" : "down"],
      ["Skills", true, `${sk.installed || 0}`],
      ["Brain", true, `${brain.nodeCount || 0}n`],
    ];
    chips.innerHTML = items.map(([l, on, v]) =>
      `<div class="chip ${on ? "on" : "off"}"><span class="d"></span>${l}: ${v}</div>`
    ).join("");
  }

  function renderSkills(skills) {
    const sorted = [...(skills || [])].sort((a, b) =>
      String(a.category || "").localeCompare(String(b.category || "")) ||
      String(a.name || "").localeCompare(String(b.name || ""))
    );
    skillsList.innerHTML = sorted.map((s) => {
      const xp = s.xp || 0;
      const pct = Math.min(100, (xp % 50) * 2);
      const cat = s.category ? `<span class="lvl">${s.category}</span> · ` : "";
      return `<article class="skill">
        <header><h3>${s.name}</h3><span class="lvl">${cat}L${s.level || 1} · ${xp}xp</span></header>
        <p>${s.summary || (s.installed ? "Installed" : "Available")}${s.custom ? " · custom" : ""}</p>
        <div class="bar"><span style="width:${pct}%"></span></div>
      </article>`;
    }).join("");
    if (window.anime) {
      anime({ targets: ".skill", opacity: [0, 1], translateY: [8, 0], delay: anime.stagger(25), duration: 350, easing: "easeOutQuad" });
    }
  }

  async function refreshHealth() {
    try {
      const data = await (await fetch("/health")).json();
      renderChips(data);
      micState.textContent = data.layers?.voicebox?.ok ? "Systems nominal" : "Voicebox offline · browser voice OK";
    } catch {
      micState.textContent = "Gateway down";
    }
  }

  async function refreshSkills() {
    try {
      const data = await (await fetch("/api/skills", { headers: authHeaders() })).json();
      renderSkills(data.skills || []);
    } catch (err) {
      skillsList.innerHTML = `<p class="meta">Skills unavailable: ${err.message}</p>`;
    }
  }

  async function sendChat(text) {
    await syncVoiceProfile();
    micState.textContent = speakBox.checked ? `Speaking as ${selectedVoice()}…` : "Thinking…";
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ message: text, speak: speakBox.checked }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    return data;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = message.value.trim();
    if (!text) return;
    addBubble("user", text);
    message.value = "";
    message.disabled = true;
    micState.textContent = "Thinking…";
    try {
      const data = await sendChat(text);
      addBubble("tony", data.reply || "(empty)", data.provider || "");
      ensureVoice(data.reply, data.speech);
      refreshSkills();
    } catch (err) {
      addBubble("tony", `Error: ${err.message}`);
    } finally {
      message.disabled = false;
      message.focus();
      micState.textContent = "Ready";
      refreshHealth();
    }
  });

  learnForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("skillName").value.trim();
    const summary = document.getElementById("skillSummary").value.trim();
    const playbook = document.getElementById("skillPlaybook").value
      .split(/\n/)
      .map((l) => l.trim())
      .filter(Boolean);
    try {
      const res = await fetch("/api/skills/learn", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ name, summary, playbook }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || res.statusText);
      addBubble("tony", `Learned skill: ${data.skill?.name} (L${data.skill?.level})`, "skills");
      learnForm.reset();
      refreshSkills();
      if (window.anime) anime({ targets: ".skills-pane", scale: [0.99, 1], duration: 350 });
    } catch (err) {
      addBubble("tony", `Learn failed: ${err.message}`);
    }
  });

  document.getElementById("btnIdleLearn").addEventListener("click", async () => {
    try {
      const data = await (await fetch("/api/skills/idle", { method: "POST", headers: authHeaders() })).json();
      addBubble("tony", `Idle learn: ${data.skill?.name || data.mode} · XP updated`, "skills");
      refreshSkills();
    } catch (err) {
      addBubble("tony", `Idle learn failed: ${err.message}`);
    }
  });

  document.getElementById("btnClear").addEventListener("click", () => { log.innerHTML = ""; });
  document.getElementById("btnWarmup")?.addEventListener("click", async () => {
    micState.textContent = "Warming Farman model…";
    try {
      const data = await (await fetch("/api/voice/warmup", { method: "POST", headers: authHeaders() })).json();
      addBubble("tony", data.message || (data.ok ? "Voice model kept warm." : data.error || "Warmup done"), "voice");
      micState.textContent = data.after?.ttsLoaded || data.ok ? "Model warm" : "Warmup issue";
      refreshHealth();
    } catch (err) {
      micState.textContent = err.message;
    }
  });
  document.getElementById("btnSkills").addEventListener("click", () => refreshSkills());
  document.getElementById("btnScreen").addEventListener("click", async () => {
    addBubble("user", "See my screen", "control");
    try {
      const data = await sendChat("Use python_tool screen_context with approved true and briefly describe what you see.");
      addBubble("tony", data.reply || "(empty)", data.provider || "");
      ensureVoice(data.reply, data.speech);
    } catch (err) { addBubble("tony", err.message); }
  });
  document.getElementById("btnDesktop").addEventListener("click", async () => {
    addBubble("user", "Desktop status", "control");
    try {
      const data = await sendChat("Call python_tool desktop_status and summarize.");
      addBubble("tony", data.reply || "(empty)", data.provider || "");
      ensureVoice(data.reply, data.speech);
    } catch (err) { addBubble("tony", err.message); }
  });

  // Mic
  let mediaRecorder = null, chunks = [], recording = false, stream = null, wave = null;
  function setRec(on) {
    micBtn.classList.toggle("recording", on);
    micLabel.textContent = on ? "…" : "Hold";
    if (!on) waveLevel = 0.15;
  }
  async function startRec() {
    if (recording) return;
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      const actx = new Ctx();
      const src = actx.createMediaStreamSource(stream);
      analyser = actx.createAnalyser();
      analyser.fftSize = 64;
      src.connect(analyser);
      recordingAudio = actx;
      const data = new Uint8Array(analyser.frequencyBinCount);
      const pump = () => {
        if (!analyser) return;
        analyser.getByteFrequencyData(data);
        let sum = 0;
        for (const v of data) sum += v;
        waveLevel = Math.min(1, (sum / data.length / 255) * 2.2);
        if (recording) requestAnimationFrame(pump);
      };
      pump();
    } catch { waveLevel = 0.55; }
    chunks = [];
    const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "audio/webm";
    mediaRecorder = new MediaRecorder(stream, { mimeType: mime });
    mediaRecorder.ondataavailable = (ev) => { if (ev.data?.size) chunks.push(ev.data); };
    mediaRecorder.start(200);
    recording = true;
    setRec(true);
    micState.textContent = "Listening…";
  }
  async function stopRec() {
    if (!recording || !mediaRecorder) return;
    recording = false;
    setRec(false);
    micState.textContent = "Processing…";
    const blob = await new Promise((resolve) => {
      mediaRecorder.onstop = () => resolve(new Blob(chunks, { type: mediaRecorder.mimeType || "audio/webm" }));
      try { mediaRecorder.stop(); } catch { resolve(new Blob(chunks, { type: "audio/webm" })); }
    });
    stream?.getTracks().forEach((t) => t.stop());
    stream = null;
    analyser = null;
    if (recordingAudio) {
      try { recordingAudio.close(); } catch { /* ignore */ }
      recordingAudio = null;
    }
    waveLevel = 0.15;
    if (!blob.size) { micState.textContent = "No audio"; return; }
    const bytes = new Uint8Array(await blob.arrayBuffer());
    let binary = "";
    for (let i = 0; i < bytes.length; i += 1) binary += String.fromCharCode(bytes[i]);
    addBubble("user", "(voice)", "mic");
    try {
      const res = await fetch("/api/voice/converse", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ audioBase64: btoa(binary), mimeType: blob.type || "audio/webm", speak: true }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || res.statusText);
      if (data.transcript) addBubble("user", data.transcript, "heard");
      addBubble("tony", data.reply || "(empty)", data.provider || "voice");
      ensureVoice(data.reply, data.speech);
      refreshSkills();
      micState.textContent = "Ready";
    } catch (err) {
      addBubble("tony", `Voice error: ${err.message}`);
      micState.textContent = "Retry";
    }
  }
  micBtn.addEventListener("mousedown", (e) => { e.preventDefault(); startRec().catch((err) => { micState.textContent = err.message; }); });
  micBtn.addEventListener("mouseup", (e) => { e.preventDefault(); stopRec().catch(() => {}); });
  micBtn.addEventListener("mouseleave", () => { if (recording) stopRec().catch(() => {}); });
  micBtn.addEventListener("touchstart", (e) => { e.preventDefault(); startRec().catch((err) => { micState.textContent = err.message; }); }, { passive: false });
  micBtn.addEventListener("touchend", (e) => { e.preventDefault(); stopRec().catch(() => {}); });

  addBubble("tony", "ULTRON online. Personal assistant · vibe coding · Obsidian brain. Hold mic, Stop anytime.", "boot");
  if (window.ultron?.isElectron) {
    addBubble("tony", "Electron shell detected — desktop Ultron mode.", "boot");
  }
  refreshHealth();
  refreshSkills();
  refreshBrain();
  loadProfiles();
  setInterval(refreshHealth, 12000);
  setInterval(refreshSkills, 20000);
  setInterval(refreshBrain, 25000);
  setInterval(loadProfiles, 30000);
})();
