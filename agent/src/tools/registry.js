"use strict";

const { rememberFact, recallFacts, setProfile, getProfile } = require("../memory/store");
const { callPythonTool, bridgeHealth } = require("../bridge/client");
const { speak, transcribe, voiceboxHealth } = require("../voice/voicebox");
const {
  listCatalog,
  learnSkill,
  installSkill,
  gainXp,
  skillsStats,
} = require("../skills/registry");
const {
  searchBrain,
  relatedNodes,
  writeNote,
  rebuildGraph,
  brainStats,
} = require("../brain/obsidian");

const TOOL_DEFS = [
  {
    type: "function",
    function: {
      name: "remember",
      description: "Store a lasting fact about the user or environment (never secrets).",
      parameters: {
        type: "object",
        properties: { fact: { type: "string" }, category: { type: "string" } },
        required: ["fact"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "recall",
      description: "Search semantic memory for facts.",
      parameters: {
        type: "object",
        properties: { query: { type: "string" }, limit: { type: "integer" } },
      },
    },
  },
  {
    type: "function",
    function: {
      name: "user_profile_update",
      description: "Update a user profile key/value.",
      parameters: {
        type: "object",
        properties: { key: { type: "string" }, value: { type: "string" } },
        required: ["key", "value"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "list_skills",
      description: "List installed and available skill packs.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function",
    function: {
      name: "learn_skill",
      description: "Learn or reinforce a custom skill.",
      parameters: {
        type: "object",
        properties: {
          name: { type: "string" },
          summary: { type: "string" },
          playbook: { type: "array", items: { type: "string" } },
        },
        required: ["name"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "install_skill",
      description: "Install a catalog skill by id.",
      parameters: {
        type: "object",
        properties: { id: { type: "string" } },
        required: ["id"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "brain_search",
      description: "Search Obsidian vault / agentic brain notes.",
      parameters: {
        type: "object",
        properties: { query: { type: "string" }, limit: { type: "integer" } },
        required: ["query"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "brain_graph",
      description: "Query knowledge graph related nodes/edges for a topic.",
      parameters: {
        type: "object",
        properties: { query: { type: "string" }, limit: { type: "integer" } },
        required: ["query"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "brain_write",
      description: "Write a new markdown note into the Obsidian vault.",
      parameters: {
        type: "object",
        properties: {
          title: { type: "string" },
          body: { type: "string" },
          folder: { type: "string" },
        },
        required: ["title", "body"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "brain_rebuild",
      description: "Rebuild the Obsidian knowledge graph index.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function",
    function: {
      name: "python_tool",
      description:
        "Desktop control via Python bridge. Tools: git_*, list_dir, read_file, open_app, list_windows, focus_window, type_text, hotkey, mouse_click, screenshot, screen_context, camera_capture, desktop_status, shell_safe. Risky actions need approved=true.",
      parameters: {
        type: "object",
        properties: {
          name: { type: "string" },
          args: { type: "object" },
          approved: { type: "boolean" },
        },
        required: ["name"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "voicebox_speak",
      description: "Speak text with active Voicebox profile (Farman).",
      parameters: {
        type: "object",
        properties: { text: { type: "string" }, profile: { type: "string" } },
        required: ["text"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "voicebox_transcribe",
      description: "Transcribe base64 audio with Voicebox.",
      parameters: {
        type: "object",
        properties: { audioBase64: { type: "string" }, mimeType: { type: "string" } },
        required: ["audioBase64"],
      },
    },
  },
];

function parseArgs(raw) {
  if (!raw) return {};
  if (typeof raw === "object") return raw;
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

async function executeTool(name, rawArgs) {
  const args = parseArgs(rawArgs);
  switch (name) {
    case "remember":
      return rememberFact(args.fact, args.category || "general");
    case "recall":
      return { facts: recallFacts(args.query || "", args.limit || 10) };
    case "user_profile_update":
      return setProfile(args.key, args.value);
    case "list_skills":
      return { skills: listCatalog(), stats: skillsStats() };
    case "learn_skill":
      return learnSkill({
        name: args.name,
        summary: args.summary,
        playbook: args.playbook,
        from: "conversation",
      });
    case "install_skill":
      return installSkill(args.id);
    case "brain_search":
      return searchBrain(args.query, { limit: args.limit || 8 });
    case "brain_graph":
      return relatedNodes(args.query, { limit: args.limit || 12 });
    case "brain_write":
      return writeNote({ title: args.title, body: args.body, folder: args.folder });
    case "brain_rebuild":
      return rebuildGraph();
    case "python_tool": {
      const out = await callPythonTool(args.name, args.args || {}, { approved: Boolean(args.approved) });
      if (out && out.ok) {
        if (["screenshot", "screen_context", "camera_capture"].includes(args.name)) gainXp("vision", 5);
        if (["list_windows", "desktop_status", "open_app", "focus_window", "type_text", "hotkey", "mouse_click"].includes(args.name)) {
          gainXp("desktop_ops", 5);
        }
        if (String(args.name || "").startsWith("git_")) gainXp("coding", 3);
      }
      return out;
    }
    case "voicebox_speak":
      try {
        return await speak(args.text, {
          profile: args.profile,
          wait: args.wait === true,
        });
      } catch (err) {
        return { ok: false, error: err.message, browserSpeak: true };
      }
    case "voicebox_transcribe": {
      try {
        const buf = Buffer.from(args.audioBase64, "base64");
        const ext = (args.mimeType || "audio/wav").includes("webm") ? "webm" : "wav";
        return await transcribe(buf, { filename: `input.${ext}` });
      } catch (err) {
        return { ok: false, error: err.message };
      }
    }
    case "health_layers":
      return {
        voicebox: await voiceboxHealth(),
        bridge: await bridgeHealth(),
        profile: getProfile(),
        skills: skillsStats(),
        brain: brainStats(),
      };
    default:
      return { ok: false, error: `unknown tool: ${name}` };
  }
}

module.exports = { TOOL_DEFS, executeTool };
