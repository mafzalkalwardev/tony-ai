"use strict";
const { runAgent } = require("../src/core/agent");

async function one(label, message) {
  const t0 = Date.now();
  try {
    const r = await runAgent(message, { speakReply: false });
    const ms = Date.now() - t0;
    const tools = (r.tools || []).map((x) => {
      try {
        const a = JSON.parse(x.args || "{}");
        return a.name ? `${x.name}:${a.name}` : x.name;
      } catch {
        return x.name;
      }
    });
    const tag = /<\w+|python_tool|brain_search/i.test(r.reply || "");
    console.log(
      `[${label}] ${ms}ms provider=${r.provider} lang=${r.languageStyle} tag=${tag} tools=${tools.join(",")}`
    );
    console.log(`  reply: ${String(r.reply || "").slice(0, 160)}`);
  } catch (err) {
    console.log(`[${label}] FAIL ${err.message}`);
  }
}

(async () => {
  await one("list", "list open windows");
  await one("urdu-notepad", "notepad kholo");
  await one("urdu-word", "word kholo");
  await one("urdu-excel", "excel kholo");
  await one("edge", "open edge");
  await one("terminal", "terminal kholo");
  await one("paste", "paste");
  await one("clip", 'put "TONY live" on the clipboard');
  await one("status", "desktop status");
})();
