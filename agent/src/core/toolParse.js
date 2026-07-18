"use strict";

/**
 * Small LLMs often print fake XML tool tags instead of native tool_calls.
 * Parse ANY known tool tag and convert to real executable calls.
 */

const NATIVE_TOOLS = new Set([
  "remember",
  "recall",
  "user_profile_update",
  "list_skills",
  "learn_skill",
  "install_skill",
  "brain_search",
  "brain_graph",
  "brain_write",
  "brain_rebuild",
  "python_tool",
  "self_evolve",
  "voicebox_speak",
  "voicebox_transcribe",
  "web_search",
]);

const BRIDGE_TOOLS = new Set([
  "open_app",
  "list_windows",
  "focus_window",
  "type_text",
  "hotkey",
  "mouse_click",
  "mouse_move",
  "scroll",
  "clipboard_get",
  "clipboard_set",
  "copy_file",
  "move_file",
  "list_dir",
  "read_file",
  "screenshot",
  "screen_context",
  "camera_capture",
  "desktop_status",
  "system_power",
  "shell_safe",
  "git_status",
  "git_diff",
  "git_log",
]);

function parseAttrBag(attrs) {
  const out = {};
  // key="value" or key='value' or key=value or key={...}
  const re =
    /([a-zA-Z0-9_]+)\s*=\s*(?:(\{[\s\S]*?\})|"([^"]*)"|'([^']*)'|([^\s>\/]+))/g;
  let m;
  while ((m = re.exec(attrs || ""))) {
    const key = m[1];
    let val = m[2] || m[3] || m[4] || m[5] || "";
    if (m[2]) {
      try {
        out[key] = JSON.parse(m[2].replace(/'/g, '"'));
      } catch {
        out[key] = m[2];
      }
    } else if (val === "true" || val === "false") {
      out[key] = val === "true";
    } else if (/^\d+$/.test(val)) {
      out[key] = Number(val);
    } else {
      out[key] = val;
    }
  }
  return out;
}

function makeCall(name, args, id) {
  return {
    id: id || `pseudo_${name}_${Math.random().toString(36).slice(2, 7)}`,
    type: "function",
    function: {
      name,
      arguments: JSON.stringify(args || {}),
    },
  };
}

function parsePseudoToolCalls(content) {
  const text = String(content || "");
  const calls = [];

  // Generic: <tool_name key=val ...></tool_name> or self-closing
  const genericRe =
    /<\s*([a-zA-Z_][a-zA-Z0-9_]*)\b([^>]*)>(?:[\s\S]*?<\/\s*\1\s*>)?/gi;
  let m;
  while ((m = genericRe.exec(text))) {
    const tag = m[1];
    const attrs = parseAttrBag(m[2] || "");

    if (tag === "python_tool") {
      const bridgeName = attrs.name;
      const bridgeArgs = typeof attrs.args === "object" ? attrs.args : {};
      if (bridgeName) {
        calls.push(
          makeCall("python_tool", {
            name: bridgeName,
            args: bridgeArgs,
            approved: Boolean(attrs.approved),
          })
        );
      }
      continue;
    }

    if (NATIVE_TOOLS.has(tag)) {
      const { approved, ...rest } = attrs;
      calls.push(makeCall(tag, rest));
      continue;
    }

    if (BRIDGE_TOOLS.has(tag)) {
      calls.push(
        makeCall("python_tool", {
          name: tag,
          args: attrs,
          approved: Boolean(attrs.approved),
        })
      );
    }
  }

  // <python_tool={...}>
  const jsonTagRe = /<\s*python_tool\s*=\s*(\{[\s\S]*?\})\s*>/gi;
  while ((m = jsonTagRe.exec(text))) {
    try {
      const obj = JSON.parse(m[1].replace(/'/g, '"'));
      if (obj.name) {
        calls.push(
          makeCall("python_tool", {
            name: obj.name,
            args: obj.args || {},
            approved: Boolean(obj.approved),
          })
        );
      }
    } catch {
      /* ignore */
    }
  }

  return calls;
}

function stripPseudoToolMarkup(content) {
  return String(content || "")
    .replace(/<\s*[a-zA-Z_][a-zA-Z0-9_]*\b[^>]*>[\s\S]*?(?:<\/\s*[a-zA-Z_][a-zA-Z0-9_]*\s*>)?/gi, " ")
    .replace(/<\s*python_tool\s*=\s*\{[\s\S]*?\}\s*>/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function userWantsAction(message) {
  const t = String(message || "").toLowerCase();
  if (/\blist\s+open\s+windows\b/.test(t)) return true;
  if (userWantsPower(t)) return true;
  return /\b(open|launch|start|run|click|type|press|close|focus|navigate|go to|search|find|copy|paste|move|rename|delete|kholo|khol|chalao|karo|kar do|please do|do it|youtube|edge|chrome|notepad|calculator|file|folder|clipboard|scroll|likho|dikhao|dekhao)\b/i.test(
    t
  );
}

function userWantsPower(message) {
  const t = String(message || "").toLowerCase();
  return /\b(shut\s*down|shutdown|power\s*off|restart|reboot|cancel\s+shut\s*down|abort\s+shut\s*down|computer\s+(band|off)|pc\s+(band|off)|sleep\s+(pc|computer)|hibernate)\b/i.test(
    t
  );
}

function userWantsSearch(message) {
  const t = String(message || "").toLowerCase();
  return /\b(search|google|look up|tell me about|kya hai|who is|what is|research|find info)\b/i.test(t);
}

function inferDesktopAction(message) {
  const t = String(message || "").toLowerCase().trim();
  const calls = [];

  // Power control (explicit only)
  if (userWantsPower(t)) {
    if (/\b(cancel|abort)\b/.test(t) && /\b(shut|shutdown)\b/.test(t)) {
      return makeCall(
        "python_tool",
        { name: "system_power", args: { action: "abort" }, approved: true },
        "infer_power_abort"
      );
    }
    if (/\b(restart|reboot)\b/.test(t)) {
      return makeCall(
        "python_tool",
        { name: "system_power", args: { action: "restart", delay: 60 }, approved: true },
        "infer_power_restart"
      );
    }
    if (/\bsleep\b/.test(t) || /\bhibernate\b/.test(t)) {
      return makeCall(
        "python_tool",
        { name: "system_power", args: { action: "sleep" }, approved: true },
        "infer_power_sleep"
      );
    }
    // shutdown / power off / band karo
    return makeCall(
      "python_tool",
      { name: "system_power", args: { action: "shutdown", delay: 60 }, approved: true },
      "infer_power_shutdown"
    );
  }

  // List windows (must beat "open windows" false positive)
  if (/\b(list|show|dekhao|dikhao)\b/.test(t) && /\bwindows?\b/.test(t)) {
    return makeCall(
      "python_tool",
      { name: "list_windows", args: {}, approved: true },
      "infer_list_windows"
    );
  }
  if (/\b(active|current|focused)\s+window\b/.test(t) || /\bdesktop status\b/.test(t)) {
    return makeCall(
      "python_tool",
      { name: "desktop_status", args: {}, approved: true },
      "infer_desktop_status"
    );
  }

  // Web / company research — web + brain + open browser search on PC
  if (userWantsSearch(t)) {
    const q = String(message || "")
      .replace(/^(search|google|look up|tell me about|research)\s+(about\s+)?/i, "")
      .replace(/\s+and tell me.*$/i, "")
      .replace(/\s+and\s+i\b.*$/i, "")
      .trim() || message;
    calls.push(
      makeCall("web_search", { query: q, limit: 5 }, "infer_web_search")
    );
    calls.push(makeCall("brain_search", { query: q, limit: 5 }, "infer_brain"));
    calls.push(makeCall("recall", { query: q, limit: 5 }, "infer_recall"));
    // Also open Edge Google search so the PC visibly does the search
    calls.push(
      makeCall(
        "python_tool",
        {
          name: "open_app",
          args: {
            app_name: "edge",
            url: `https://www.google.com/search?q=${encodeURIComponent(q)}`,
          },
          approved: true,
        },
        "infer_browser_search"
      )
    );
    return calls;
  }

  if (!userWantsAction(t)) return null;

  // Copy / move files
  const copyM = /(?:copy|paste)\s+(.+?)\s+(?:to|into)\s+(.+)/i.exec(message);
  if (copyM) {
    return makeCall(
      "python_tool",
      {
        name: "copy_file",
        args: { src: copyM[1].trim().replace(/^["']|["']$/g, ""), dest: copyM[2].trim().replace(/^["']|["']$/g, "") },
        approved: true,
      },
      "infer_copy"
    );
  }
  const moveM = /move\s+(.+?)\s+to\s+(.+)/i.exec(message);
  if (moveM) {
    return makeCall(
      "python_tool",
      {
        name: "move_file",
        args: { src: moveM[1].trim(), dest: moveM[2].trim() },
        approved: true,
      },
      "infer_move"
    );
  }

  // Clipboard / hotkeys
  const clipSet = /(?:put|set|copy)\s+["'](.+?)["']\s+(?:on|to|in)\s+(?:the\s+)?clipboard/i.exec(message)
    || /clipboard\s+(?:pe|mein|par)?\s*["'](.+?)["']/i.exec(message);
  if (clipSet) {
    return makeCall(
      "python_tool",
      { name: "clipboard_set", args: { text: clipSet[1] }, approved: true },
      "infer_clipboard_set"
    );
  }
  if (/\b(copy|ctrl\+c)\b/i.test(t) && /\b(selected|selection|text)\b/i.test(t)) {
    return makeCall("python_tool", { name: "hotkey", args: { keys: ["ctrl", "c"] }, approved: true }, "infer_hotkey_copy");
  }
  if (/\bpaste\b/i.test(t) && !copyM) {
    return makeCall("python_tool", { name: "hotkey", args: { keys: ["ctrl", "v"] }, approved: true }, "infer_hotkey_paste");
  }
  // Type text into focused window
  const typeM = /(?:type|likho|likh)\s+["'](.+?)["']/i.exec(message)
    || /(?:type|likho)\s+(.+)$/i.exec(message);
  if (typeM && /\b(type|likho|likh)\b/i.test(t)) {
    return makeCall(
      "python_tool",
      { name: "type_text", args: { text: typeM[1].trim() }, approved: true },
      "infer_type"
    );
  }

  // Scroll
  if (/\bscroll\s+(up|down)\b/i.test(t) || /\b(upar|neeche)\s+scroll\b/i.test(t)) {
    const down = /\b(down|neeche)\b/i.test(t);
    return makeCall(
      "python_tool",
      { name: "scroll", args: { clicks: down ? -5 : 5 }, approved: true },
      "infer_scroll"
    );
  }

  // YouTube / Edge / apps
  if (/\byoutube\b/.test(t)) {
    const inEdge = /\bedge\b/.test(t) || /\bsession\b/.test(t);
    return makeCall(
      "python_tool",
      {
        name: "open_app",
        args: { app_name: inEdge ? "youtube_edge" : "youtube", url: "https://www.youtube.com" },
        approved: true,
      },
      "infer_youtube"
    );
  }

  if (/\b(open|launch|start|kholo|chalao)\b/.test(t) && /\bedge\b/.test(t) && !/\byoutube\b/.test(t)) {
    return makeCall("python_tool", { name: "open_app", args: { app_name: "edge" }, approved: true }, "infer_edge");
  }

  const appMap = [
    [/visual\s*studio|\bvscode\b|\bvs\s*code\b/, "code"],
    [/\bnotepad\b/, "notepad"],
    [/calculator|\bcalc\b/, "calculator"],
    [/explorer|file manager/, "explorer"],
    [/terminal|powershell/, "terminal"],
    [/chrome/, "chrome"],
    [/word\b|winword/, "word"],
    [/excel/, "excel"],
    [/spotify/, "spotify"],
    [/discord/, "discord"],
    [/slack/, "slack"],
    [/photoshop/, "photoshop"],
  ];
  if (/\b(open|launch|start|kholo|chalao|please)\b/.test(t) || /\bopen\b/.test(t)) {
    for (const [re, app] of appMap) {
      if (re.test(t)) {
        return makeCall(
          "python_tool",
          { name: "open_app", args: { app_name: app }, approved: true },
          `infer_${app}`
        );
      }
    }
    // "X kholo/chalao" (Roman Urdu: app name first)
    const urduOpen = /^(.+?)\s+(kholo|chalao|khol do|open karo)\s*$/i.exec(message);
    if (urduOpen) {
      const appName = urduOpen[1].replace(/[?.!]+$/, "").trim();
      if (appName && appName.length < 80) {
        return makeCall(
          "python_tool",
          { name: "open_app", args: { app_name: appName }, approved: true },
          "infer_urdu_open"
        );
      }
    }
    // Generic: "open X" → start menu / shell open
    const generic = /(?:open|launch|start|kholo|chalao)\s+(.+)$/i.exec(message);
    if (generic) {
      const appName = generic[1].replace(/[?.!]+$/, "").trim();
      if (appName && appName.length < 80) {
        return makeCall(
          "python_tool",
          { name: "open_app", args: { app_name: appName }, approved: true },
          "infer_generic_open"
        );
      }
    }
  }

  const url = /(https?:\/\/\S+)/i.exec(message);
  if (url && /\b(open|go to|visit|kholo)\b/i.test(t)) {
    return makeCall(
      "python_tool",
      { name: "open_app", args: { app_name: "url", url: url[1] }, approved: true },
      "infer_url"
    );
  }

  return null;
}

/** Normalize infer result to always be an array of tool calls */
function asCallList(inferred) {
  if (!inferred) return [];
  return Array.isArray(inferred) ? inferred : [inferred];
}

function normalizeToolCall(call) {
  const name = call.function?.name || call.name;
  let args = call.function?.arguments || call.arguments || {};
  if (typeof args === "string") {
    try {
      args = JSON.parse(args);
    } catch {
      args = {};
    }
  }
  return { name, args, id: call.id };
}

function applyActionApproval(name, args, userMessage) {
  const next = { ...args };
  if (name === "python_tool") {
    const tool = String(next.name || "");
    if (tool === "system_power" && userWantsPower(userMessage)) {
      next.approved = true;
    } else if (userWantsAction(userMessage)) {
      if (
        [
          "open_app",
          "focus_window",
          "list_windows",
          "desktop_status",
          "hotkey",
          "type_text",
          "mouse_click",
          "mouse_move",
          "scroll",
          "clipboard_get",
          "clipboard_set",
          "copy_file",
          "move_file",
        ].includes(tool)
      ) {
        next.approved = true;
      }
    }
  }
  if (next.approved === "true" || next.approved === 1) next.approved = true;
  return next;
}

module.exports = {
  parsePseudoToolCalls,
  stripPseudoToolMarkup,
  userWantsAction,
  userWantsSearch,
  userWantsPower,
  inferDesktopAction,
  asCallList,
  normalizeToolCall,
  applyActionApproval,
};
