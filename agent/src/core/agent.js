"use strict";

const { config } = require("../config");
const { chatWithFallback } = require("../llm/providers");
const { buildSystemPrompt } = require("../llm/persona");
const { detectLanguageStyle } = require("../llm/language");
const { TOOL_DEFS, executeTool } = require("../tools/registry");
const { logEpisodic, memoryHints, recentEpisodic } = require("../memory/store");
const {
  parsePseudoToolCalls,
  stripPseudoToolMarkup,
  inferDesktopAction,
  asCallList,
  normalizeToolCall,
  applyActionApproval,
  userWantsAction,
  userWantsSearch,
} = require("./toolParse");

async function runToolCalls(toolCalls, toolTrace, messages, userMessage) {
  for (const call of toolCalls) {
    const { name, args: rawArgs, id } = normalizeToolCall(call);
    const args = applyActionApproval(name, rawArgs, userMessage);
    const out = await executeTool(name, args);
    toolTrace.push({
      name,
      args: JSON.stringify(args),
      result: out,
    });
    messages.push({
      role: "tool",
      tool_call_id: id || `call_${toolTrace.length}`,
      content: JSON.stringify(out),
    });
  }
}

/** Pure PC actions — skip LLM when tools already succeeded (fast + no tag dumps). */
function isPureDesktopAction(inferred) {
  if (!inferred.length) return false;
  return inferred.every((c) => {
    const n = c.function?.name;
    if (n === "python_tool") return true;
    return false;
  });
}

function quickFriendReply(toolTrace, languageStyle, userMessage) {
  const last = toolTrace[toolTrace.length - 1]?.result || {};
  const ok = last.ok !== false;
  const raw = String(last.text || last.summary || "");
  const toolName = (() => {
    try {
      return JSON.parse(toolTrace[toolTrace.length - 1]?.args || "{}").name;
    } catch {
      return "";
    }
  })();

  if (toolName === "list_windows" || last.windows || last.titles) {
    const wins = last.windows || last.titles || last.items || [];
    const n = Array.isArray(wins) ? wins.length : last.window_count || 0;
    if (languageStyle === "roman_urdu") {
      return ok ? `Screen pe roughly ${n || "kai"} windows open hain.` : "Windows list nahi mil saki.";
    }
    return ok ? `You've got ${n || "several"} windows open.` : "Couldn't list windows.";
  }
  if (toolName === "desktop_status" || last.active_window) {
    const active = String(last.active_window || "").slice(0, 60) || "unknown";
    const n = last.window_count || "?";
    if (languageStyle === "roman_urdu") {
      return ok ? `Abhi active: ${active}. Total ~${n} windows.` : "Status nahi mila.";
    }
    return ok ? `Active window: ${active} (${n} open).` : "Couldn't get desktop status.";
  }
  if (toolName === "system_power" || last.action === "shutdown" || last.action === "restart" || last.action === "abort") {
    const delay = last.delay != null ? last.delay : 60;
    if (languageStyle === "roman_urdu") {
      if (!ok) return `Power action fail: ${last.error || "error"}`;
      if (last.action === "abort") return "Shutdown cancel kar diya.";
      if (last.action === "restart") return `PC ${delay}s mein restart hoga. Cancel: 'cancel shutdown'.`;
      if (last.action === "sleep") return "Sleep mode pe ja raha hai.";
      return `PC ${delay}s mein shut down hoga. Cancel ke liye bolo: cancel shutdown.`;
    }
    if (!ok) return `Power action failed: ${last.error || "error"}`;
    if (last.action === "abort") return "Shutdown cancelled.";
    if (last.action === "restart") return `Restarting in ${delay}s. Say 'cancel shutdown' to abort.`;
    if (last.action === "sleep") return "Going to sleep.";
    return `Shutting down in ${delay}s. Say 'cancel shutdown' to abort.`;
  }

  const openMatch = /Opening(?:\s+in)?\s+([^:.]+)/i.exec(raw);
  const launchMatch = /Launching:\s*(.+)/i.exec(raw);
  let app = openMatch?.[1]?.trim() || launchMatch?.[1]?.trim() || null;
  if (app) app = app.replace(/:$/, "").replace(/^in\s+/i, "").trim();
  if (!app && /Copied\s+/i.test(raw)) app = "file";
  if (!app && /Moved\s+/i.test(raw)) app = "file";

  if (languageStyle === "roman_urdu") {
    if (!ok) return `Issue aa gaya: ${last.error || "fail"}. Dobara try karo.`;
    if (/copied/i.test(raw)) return "File copy ho gayi bhai.";
    if (/moved/i.test(raw)) return "File move ho gayi.";
    if (/youtube/i.test(userMessage)) return "YouTube Edge mein khol diya.";
    if (toolName === "clipboard_set") return "Clipboard pe set kar diya.";
    if (toolName === "type_text") return "Type kar diya.";
    if (toolName === "hotkey") return "Hotkey laga diya.";
    if (app && app !== "file") return `${app} khol diya.`;
    return "Ho gaya bhai.";
  }
  if (!ok) return `Couldn't finish: ${last.error || "failed"}.`;
  if (/copied/i.test(raw)) return "Copied — you're set.";
  if (/moved/i.test(raw)) return "Moved — done.";
  if (/youtube/i.test(userMessage)) return "YouTube's open in Edge.";
  if (toolName === "clipboard_set") return "Clipboard updated.";
  if (toolName === "type_text") return "Typed it.";
  if (toolName === "hotkey") return "Hotkey sent.";
  if (app && app !== "file") return `${app} is open.`;
  return "Done.";
}

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

  // On-demand: open apps / search / file ops BEFORE the LLM prints fake tags
  const inferred = asCallList(inferDesktopAction(userMessage));
  if (inferred.length) {
    messages.push({ role: "assistant", content: null, tool_calls: inferred });
    await runToolCalls(inferred, toolTrace, messages, userMessage);
  }

  // Fast path: open/copy/move already done — no LLM round-trip
  if (isPureDesktopAction(inferred) && toolTrace.length && !userWantsSearch(userMessage)) {
    const allOk = toolTrace.every((t) => t.result && t.result.ok !== false);
    if (allOk) {
      finalText = quickFriendReply(toolTrace, languageStyle, userMessage);
      provider = "direct";
      logEpisodic("assistant", finalText, {
        source,
        provider,
        tools: toolTrace.map((t) => t.name),
        languageStyle,
      });
      let speech = null;
      if (speakReply && finalText) {
        try {
          const { toFriendSpeech, friendSpeechInstruct } = require("../voice/friendSpeech");
          speech = await executeTool(
            "voicebox_speak",
            JSON.stringify({
              text: toFriendSpeech(finalText, { languageStyle }),
              wait: false,
              personality: true,
              instruct: friendSpeechInstruct(languageStyle),
            })
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
      };
    }
  }

  for (let i = 0; i < config.maxIterations; i += 1) {
    const result = await chatWithFallback(messages, { tools: TOOL_DEFS });
    provider = result.provider;
    lastErrors = result.fallbackErrors || [];
    const msg = result.message || {};
    messages.push(msg);

    let toolCalls = msg.tool_calls || [];
    if (!toolCalls.length && msg.content) {
      toolCalls = parsePseudoToolCalls(msg.content);
    }
    if (!toolCalls.length && !toolTrace.length && userWantsAction(userMessage)) {
      toolCalls = asCallList(inferDesktopAction(userMessage));
    }

    if (!toolCalls.length) {
      finalText = stripPseudoToolMarkup(msg.content || "");
      break;
    }
    await runToolCalls(toolCalls, toolTrace, messages, userMessage);
  }

  if (!finalText || /<[a-z_]+|python_tool|brain_search|recall\s/i.test(finalText)) {
    messages.push({
      role: "user",
      content:
        languageStyle === "roman_urdu"
          ? "Ab dost ki tarah short batao kya mila / kya action hua. Koi XML tag, tool name, JSON mat likho."
          : "Reply like a friend: what you found or did. No XML tags, tool names, or JSON.",
    });
    const reflect = await chatWithFallback(messages);
    provider = reflect.provider;
    lastErrors = reflect.fallbackErrors || lastErrors;
    finalText = stripPseudoToolMarkup(reflect.message?.content || "");
  }

  if ((!finalText || /python_tool|brain_search|<\s*\w+/i.test(finalText)) && toolTrace.length) {
    const last = toolTrace[toolTrace.length - 1]?.result || {};
    const web = toolTrace.find((t) => t.name === "web_search")?.result;
    if (web?.summary) {
      finalText =
        languageStyle === "roman_urdu"
          ? `Sun: ${String(web.summary).slice(0, 280)}`
          : String(web.summary).slice(0, 320);
    } else {
      const ok = last.ok !== false;
      finalText =
        languageStyle === "roman_urdu"
          ? ok
            ? `Ho gaya bhai — ${last.text || last.summary || "action complete"}.`
            : `Issue: ${last.error || "fail"}.`
          : ok
            ? `Done — ${last.text || last.summary || "action complete"}.`
            : `Couldn't finish: ${last.error || "failed"}.`;
    }
    finalText = stripPseudoToolMarkup(finalText);
  }

  if (speakReply && finalText) {
    const tooTechnical =
      /python_tool|brain_search|list_windows|\{|"ok":|```|<\w+/i.test(finalText) || finalText.length > 500;
    if (tooTechnical) {
      messages.push({
        role: "user",
        content:
          languageStyle === "roman_urdu"
            ? "Isay aur natural banao: bilkul dost wali short baat, bina technical jargon ke."
            : "Rewrite as a casual friend message — short, natural, zero jargon.",
      });
      try {
        const soft = await chatWithFallback(messages);
        if (soft.message?.content) {
          finalText = stripPseudoToolMarkup(soft.message.content);
          provider = soft.provider || provider;
        }
      } catch {
        /* keep */
      }
    }
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
      const { toFriendSpeech, friendSpeechInstruct } = require("../voice/friendSpeech");
      const spokenText = toFriendSpeech(finalText, { languageStyle });
      speech = await executeTool(
        "voicebox_speak",
        JSON.stringify({
          text: spokenText,
          wait: false,
          personality: true,
          instruct: friendSpeechInstruct(languageStyle),
        })
      );
    } catch (err) {
      speech = { ok: false, error: err.message, browserSpeak: true };
    }
  }

  return {
    reply: finalizeFriendReply(finalText, toolTrace, languageStyle),
    provider,
    tools: toolTrace,
    speech,
    spoken: Boolean(speech && speech.ok),
    languageStyle,
    ...(provider === "mock" && lastErrors.length ? { fallbackHint: lastErrors[0] } : {}),
  };
}

function finalizeFriendReply(text, toolTrace, languageStyle) {
  let t = stripPseudoToolMarkup(String(text || ""));
  t = t
    .replace(/\b(Theek hai\s*[-–—:]?\s*)?result\s*:\s*/gi, "")
    .replace(/[A-Za-z]:\\[^\s]+/g, "")
    .replace(/\bD:\\tony-ai\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();
  if (/python_tool|brain_search|<\s*\w+|approved\s*=|Opening VS Code:/i.test(t)) t = "";
  if (t && t.length > 2) return t;
  const web = toolTrace.find((x) => x.name === "web_search")?.result;
  if (web?.summary) return String(web.summary).slice(0, 400);
  return quickFriendReply(toolTrace, languageStyle, "");
}

module.exports = { runAgent };
