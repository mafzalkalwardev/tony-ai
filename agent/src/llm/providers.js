"use strict";

const { config } = require("../config");

async function fetchJson(url, options = {}) {
  const res = await fetch(url, options);
  const text = await res.text();
  let body;
  try {
    body = text ? JSON.parse(text) : {};
  } catch {
    body = { raw: text };
  }
  if (!res.ok) {
    const err = new Error(body.error?.message || body.error || `HTTP ${res.status} ${url}`);
    err.status = res.status;
    err.body = body;
    throw err;
  }
  return body;
}

async function chatGroq(messages, { tools } = {}) {
  if (!config.llm.groqApiKey) throw new Error("GROQ_API_KEY missing");
  const body = {
    model: config.llm.groqModel,
    messages,
    temperature: 0.6,
  };
  if (tools?.length) {
    body.tools = tools;
    body.tool_choice = "auto";
  }
  const data = await fetchJson("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.llm.groqApiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  return {
    provider: "groq",
    message: data.choices?.[0]?.message || { role: "assistant", content: "" },
    usage: data.usage,
  };
}

async function chatOllama(messages, { tools } = {}) {
  const body = {
    model: config.llm.ollamaModel,
    messages: messages.map((m) => ({
      role: m.role,
      content: m.content || "",
      ...(m.tool_calls ? { tool_calls: m.tool_calls } : {}),
    })),
    stream: false,
  };
  if (tools?.length) body.tools = tools;
  const data = await fetchJson(`${config.llm.ollamaBaseUrl}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const msg = data.message || { role: "assistant", content: "" };
  return { provider: "ollama", message: msg, usage: data.usage };
}

function mockChat(messages, { tools } = {}) {
  const lastUser = [...messages].reverse().find((m) => m.role === "user");
  const text = (lastUser?.content || "").toLowerCase();
  const hasToolResults = messages.some((m) => m.role === "tool");
  const sys = messages.find((m) => m.role === "system")?.content || "";
  const roman =
    /Roman Urdu/i.test(sys) ||
    /\b(kya|hai|bhai|theek|haan|nahi|kaise)\b/i.test(lastUser?.content || "");

  // After tools ran, synthesize a final answer (do not loop forever).
  if (hasToolResults) {
    const lastTool = [...messages].reverse().find((m) => m.role === "tool");
    let summary = "Done.";
    try {
      const parsed = JSON.parse(lastTool.content || "{}");
      summary =
        parsed.text ||
        parsed.summary ||
        (parsed.facts ? `I recall: ${parsed.facts.map((f) => f.fact).join("; ")}` : null) ||
        (parsed.ok && parsed.fact ? `Remembered: ${parsed.fact}` : null) ||
        JSON.stringify(parsed).slice(0, 400);
    } catch {
      summary = String(lastTool?.content || "Done.").slice(0, 400);
    }
    if (roman && !/[\u0600-\u06FF]/.test(summary)) {
      summary = `Theek hai — result: ${summary}`;
    }
    return { provider: "mock", message: { role: "assistant", content: summary } };
  }

  if (tools?.length && (text.includes("learn") || text.includes("sikhao") || text.includes("teach"))) {
    return {
      provider: "mock",
      message: {
        role: "assistant",
        content: null,
        tool_calls: [
          {
            id: "call_mock_learn",
            type: "function",
            function: {
              name: "learn_skill",
              arguments: JSON.stringify({
                name: "User Taught Workflow",
                summary: lastUser.content.slice(0, 120),
                playbook: ["Listen to user steps", "Confirm", "Reuse next time"],
              }),
            },
          },
        ],
      },
    };
  }

  if (tools?.length && (text.includes("skills") || text.includes("what can you"))) {
    return {
      provider: "mock",
      message: {
        role: "assistant",
        content: null,
        tool_calls: [
          {
            id: "call_mock_skills",
            type: "function",
            function: { name: "list_skills", arguments: "{}" },
          },
        ],
      },
    };
  }

  if (tools?.length && (text.includes("remember") || text.includes("yaad"))) {
    return {
      provider: "mock",
      message: {
        role: "assistant",
        content: null,
        tool_calls: [
          {
            id: "call_mock_remember",
            type: "function",
            function: {
              name: "remember",
              arguments: JSON.stringify({ fact: lastUser.content, category: "preference" }),
            },
          },
        ],
      },
    };
  }

  if (tools?.length && (text.includes("git status") || text.includes("repo status"))) {
    return {
      provider: "mock",
      message: {
        role: "assistant",
        content: null,
        tool_calls: [
          {
            id: "call_mock_git",
            type: "function",
            function: {
              name: "python_tool",
              arguments: JSON.stringify({ name: "git_status", args: {} }),
            },
          },
        ],
      },
    };
  }

  if (tools?.length && (text.includes("recall") || text.includes("what do you know"))) {
    return {
      provider: "mock",
      message: {
        role: "assistant",
        content: null,
        tool_calls: [
          {
            id: "call_mock_recall",
            type: "function",
            function: {
              name: "recall",
              arguments: JSON.stringify({ query: lastUser.content }),
            },
          },
        ],
      },
    };
  }

  let reply =
    "I'm Tony — online in mock mode. Wire GROQ_API_KEY or start Ollama for the full brain. " +
    "I can remember facts, call desktop tools, and speak through Voicebox when available.";
  if (roman) {
    reply =
      "Main Tony hoon — abhi mock mode mein hoon (Groq limit / Ollama band). Brain, desktop control, aur Voicebox tools ready hain — key/model fix karo to full jawab aa jayega.";
  }
  if (text.includes("joke") || text.includes("mazak")) {
    reply = roman
      ? "Programmers dark mode kyun pasand karte hain? Kyunki light bugs ko attract karti hai — aur mere paas pehle se tickets kaafi hain."
      : "Why do programmers prefer dark mode? Because light attracts bugs — and I already have enough tickets.";
  } else if (text.includes("hello") || text.includes("hi") || text.includes("salam")) {
    reply = roman
      ? `Salam ${config.userName}! Tony online hai. Bolo kya karna hai?`
      : `Hey ${config.userName}. Tony Phase 1 brain online. What are we building?`;
  } else if (roman && (text.includes("control") || text.includes("pc") || text.includes("kar sakte"))) {
    reply =
      "Ji — main PC control kar sakta hoon: windows list/focus, apps open, type_text, hotkey, mouse_click, screenshot, camera, git/files, shell_safe. Risky actions ke liye approved=true chahiye.";
  }

  return { provider: "mock", message: { role: "assistant", content: reply } };
}

async function probeOllama() {
  try {
    const res = await fetch(`${config.llm.ollamaBaseUrl}/api/tags`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch {
    return false;
  }
}

async function chatWithFallback(messages, options = {}) {
  const preferred = config.llm.provider;
  const order =
    preferred === "groq"
      ? ["groq", "ollama", "mock"]
      : preferred === "ollama"
        ? ["ollama", "groq", "mock"]
        : preferred === "mock"
          ? ["mock"]
          : ["groq", "ollama", "mock"];

  const errors = [];
  for (const name of order) {
    try {
      if (name === "groq") {
        if (!config.llm.groqApiKey) {
          errors.push("groq: no key");
          continue;
        }
        const out = await chatGroq(messages, options);
        out.fallbackErrors = errors;
        return out;
      }
      if (name === "ollama") {
        if (!(await probeOllama())) {
          errors.push("ollama: unreachable");
          continue;
        }
        const out = await chatOllama(messages, options);
        out.fallbackErrors = errors;
        return out;
      }
      const out = mockChat(messages, options);
      out.fallbackErrors = errors;
      return out;
    } catch (err) {
      errors.push(`${name}: ${err.message}`);
    }
  }
  const out = mockChat(messages, options);
  out.fallbackErrors = errors;
  return out;
}

async function llmHealth() {
  const ollama = await probeOllama();
  return {
    providerPref: config.llm.provider,
    groqConfigured: Boolean(config.llm.groqApiKey),
    ollamaReachable: ollama,
    activeFallback: config.llm.groqApiKey ? "groq" : ollama ? "ollama" : "mock",
  };
}

module.exports = {
  chatWithFallback,
  llmHealth,
  chatGroq,
  chatOllama,
  mockChat,
};
