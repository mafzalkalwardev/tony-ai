"use strict";

const { config } = require("../config");
const { skillPromptBlock } = require("../skills/registry");
const { languageDirective } = require("./language");
const { brainPromptHints } = require("../brain/obsidian");

function buildSystemPrompt({ memoryHints = [], companion = false, languageStyle = "english", userMessage = "" } = {}) {
  const lines = [
    `You are TONY (Tactical Omniscient Neural Yielder), personal AI for ${config.userName}.`,
    config.persona,
    "You understand English, Urdu (Arabic script), and Roman Urdu / Hinglish fluently.",
    languageDirective(languageStyle),
    "Crack light jokes when it fits; never be cruel. Be concise unless asked for depth.",
    "Use Obsidian brain tools: brain_search, brain_graph, brain_write, brain_rebuild when memory/knowledge helps.",
    "Use tools when they help. Prefer remember/recall for lasting facts.",
    "When the user teaches a workflow or asks you to learn something, call learn_skill.",
    "Never store secrets, passwords, API keys, OTP, or payment data in memory or skills.",
    "Computer control via python_tool: list_windows, focus_window, open_app, type_text, hotkey, mouse_click, screenshot, screen_context, camera_capture, desktop_status, shell_safe — ALWAYS respect approval=true for risky actions.",
    "When Voicebox is available, use voicebox_speak for spoken replies in the active profile (Farman).",
  ];
  if (companion) {
    lines.push(
      "Companion mode: warm briefing tone — best friend, caring partner, protective brother when waking. Roman Urdu OK."
    );
  }
  const skills = skillPromptBlock();
  if (skills) lines.push(skills);
  const brain = brainPromptHints(userMessage);
  if (brain) lines.push(brain);
  if (memoryHints.length) {
    lines.push("Known facts about the user:");
    for (const h of memoryHints.slice(0, 12)) lines.push(`- ${h}`);
  }
  return lines.join("\n");
}

module.exports = { buildSystemPrompt };
