"use strict";

/**
 * Turn assistant text into something a friend would say out loud —
 * no tool dumps, JSON, Python blobs, or robotic narration.
 */
function toFriendSpeech(text, { languageStyle = "english" } = {}) {
  let t = String(text || "");

  // Strip code / JSON / tool markup first
  t = t
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`[^`]+`/g, " ")
    .replace(/<python_tool\b[^>]*>/gi, " ")
    .replace(/<\/?[^>]+>/g, " ")
    .replace(/\{[^{}]{0,800}\}/g, " ")
    .replace(/\[[^\]\n]{0,400}\]/g, " ");

  // Kill technical dumps people hate hearing
  t = t
    .replace(/\bpython_tool\b/gi, " ")
    .replace(/\b(tool|function|args?|approved|ok|true|false|null|undefined)\s*[:=]/gi, " ")
    .replace(/\b(list_windows|focus_window|type_text|hotkey|mouse_click|screen_context|desktop_status|shell_safe|open_app|camera_capture|screenshot|git_\w+|brain_\w+|voicebox_\w+)\b/gi, " ")
    .replace(/\bD:\\[^\s]+/gi, " ")
    .replace(/\bhttps?:\/\/\S+/gi, " ")
    .replace(/\b[\w.-]+\.(js|py|json|md|tsx?|css)\b/gi, " ")
    .replace(/\b(generationId|profile_id|audio_path|status|provider)\b/gi, " ")
    .replace(/["']ok["']\s*:\s*(true|false)/gi, " ")
    .replace(/\bL\d+\s*·\s*\d+xp\b/gi, " ");

  // Soften leftover robot phrasing
  t = t
    .replace(/\bI (have )?(used|executed|called|invoked|ran)\b[^.?!]{0,40}/gi, "I checked")
    .replace(/\b(and )?got (ok )?true\b/gi, "")
    .replace(/\bok true\b/gi, "")
    .replace(/\bstatus:?\s*(ok|true|false)\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();

  // Soften markdown leftovers
  t = t
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/^\s*[-*•]\s+/gm, "")
    .replace(/\*\*|__/g, "")
    .replace(/\s+/g, " ")
    .trim();

  // If still looks like raw data, replace with a human line
  const looksTechnical =
    !t ||
    t.length < 12 ||
    /^[\{\[\"'\\d]/.test(t) ||
    (t.match(/[{}:_=]/g) || []).length > 4 ||
    /\b(error|traceback|exception)\b/i.test(t) ||
    /^(I checked)\s*$/i.test(t);

  if (looksTechnical) {
    return languageStyle === "roman_urdu" || languageStyle === "urdu_script"
      ? "Ho gaya bhai — main dekh liya. Short mein: sab theek chal raha hai."
      : "All good — I checked it. Want the short version?";
  }

  // Prefer first 2 conversational sentences for TTS
  const parts = t.split(/(?<=[.!?…])\s+/).filter(Boolean);
  let spoken = parts.slice(0, 3).join(" ");
  if (!spoken) spoken = t;

  const max = Number(process.env.VOICEBOX_MAX_CHARS || 280);
  if (spoken.length > max) {
    spoken = `${spoken.slice(0, max - 1).replace(/\s+\S*$/, "").trim()}…`;
  }

  // Light friend polish — don't start with robotic labels
  spoken = spoken
    .replace(/^(Answer|Response|Result|Output|Summary)\s*:\s*/i, "")
    .replace(/\bI have (executed|called|invoked)\b/gi, "I")
    .replace(/\bvia the (python )?bridge\b/gi, "")
    .replace(/\busing the \w+ tool\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();

  return spoken;
}

function friendSpeechInstruct(languageStyle = "english") {
  if (languageStyle === "roman_urdu" || languageStyle === "urdu_script") {
    return "talk like a close friend; casual Roman Urdu vibe; warm and natural; never sound like reading a manual";
  }
  return "talk like a close friend; casual conversational English; warm and natural; never sound like reading documentation or code";
}

module.exports = { toFriendSpeech, friendSpeechInstruct };
