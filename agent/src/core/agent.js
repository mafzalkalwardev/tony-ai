"use strict";

const { config } = require("../config");
const { chatWithFallback } = require("../llm/providers");
const { buildSystemPrompt } = require("../llm/persona");
const { detectLanguageStyle } = require("../llm/language");
const { TOOL_DEFS, executeTool } = require("../tools/registry");
const { logEpisodic, memoryHints, recentEpisodic } = require("../memory/store");

async function runAgent(userMessage, { source = "text", speakReply = false } = {}) {
  const hints = memoryHints();
  const languageStyle = detectLanguageStyle(userMessage);
  const history = recentEpisodic(6).map((r) => ({
    role: r.role === "tool" ? "assistant" : r.role,
    content: String(r.content || "").slice(0, 1200),
  }));

  const messages = [
    {
      role: "system",
      content: buildSystemPrompt({
        memoryHints: hints,
        companion: config.companionMode,
        languageStyle,
        userMessage,
      }),
    },
    ...history.filter((m) => m.role === "user" || m.role === "assistant"),
    { role: "user", content: userMessage },
  ];

  logEpisodic("user", userMessage, { source, languageStyle });

  const toolTrace = [];
  let finalText = "";
  let provider = "unknown";
  let lastErrors = [];

  for (let i = 0; i < config.maxIterations; i += 1) {
    const result = await chatWithFallback(messages, { tools: TOOL_DEFS });
    provider = result.provider;
    lastErrors = result.fallbackErrors || [];
    const msg = result.message || {};
    messages.push(msg);

    const toolCalls = msg.tool_calls || [];
    if (!toolCalls.length) {
      finalText = msg.content || "";
      break;
    }

    for (const call of toolCalls) {
      const name = call.function?.name || call.name;
      const args = call.function?.arguments || call.arguments || {};
      const out = await executeTool(name, args);
      toolTrace.push({
        name,
        args: typeof args === "string" ? args : JSON.stringify(args),
        result: out,
      });
      messages.push({
        role: "tool",
        tool_call_id: call.id || `call_${toolTrace.length}`,
        content: JSON.stringify(out),
      });
    }
  }

  if (!finalText) {
    messages.push({
      role: "user",
      content:
        languageStyle === "roman_urdu"
          ? "Tool results ko integrate karke user ko Roman Urdu mein short final jawab do."
          : languageStyle === "urdu_script"
            ? "ٹول نتائج کو جوڑ کر مختصر اردو جواب دیں۔"
            : "Integrate the tool results and give your final answer to the user. Be concise.",
    });
    const reflect = await chatWithFallback(messages);
    provider = reflect.provider;
    lastErrors = reflect.fallbackErrors || lastErrors;
    finalText = reflect.message?.content || "Done.";
  }

  logEpisodic("assistant", finalText, {
    source,
    provider,
    tools: toolTrace.map((t) => t.name),
    languageStyle,
  });

  let speech = null;
  if (speakReply && finalText) {
    try {
      // Queue Farman without blocking chat; HUD polls generation + plays WAV
      speech = await executeTool(
        "voicebox_speak",
        JSON.stringify({ text: finalText, wait: false })
      );
    } catch (err) {
      speech = { ok: false, error: err.message, browserSpeak: true };
    }
  }

  return {
    reply: finalText,
    provider,
    tools: toolTrace,
    speech,
    spoken: Boolean(speech && speech.ok),
    languageStyle,
    ...(provider === "mock" && lastErrors.length ? { fallbackHint: lastErrors[0] } : {}),
  };
}

module.exports = { runAgent };
