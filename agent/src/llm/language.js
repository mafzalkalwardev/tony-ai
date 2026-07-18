"use strict";

/**
 * Detect language style and reply guidance for Urdu / Roman Urdu / English.
 */
const ROMAN_URDU_RE =
  /\b(kya|kyun|kyu|hai|hain|haan|han|nahi|nahin|naheen|kaise|kese|kaisay|karo|karna|krna|krdo|kardo|mujhe|mujh|mera|meri|mere|tum|tumhara|aap|ap|bhai|yaar|theek|theekhai|acha|accha|achha|samajh|samjha|batao|bata|sunao|suna|chahiye|chahye|please|pls|thora|thora|zara|jaldi|abhi|phir|lekin|magar|kyunki|kyunke|woh|wo|yeh|ye|iska|uska|wahan|yahan|kitna|kitni|kab|kahan|kahan|shukriya|mehrbani|meherbani|salam|assalam|walaikum|allah|inshallah|mashallah|scene|scene\s*kya|bol|bolo|baat|baatein|kar\s*do|de\s*do|bana\s*do|check\s*karo|dekho|suno|kholo|khol|chalao|likho|dikhao|dekhao)\b/i;

function detectLanguageStyle(text) {
  const t = String(text || "");
  const hasUrduScript = /[\u0600-\u06FF]/.test(t);
  if (hasUrduScript) return "urdu_script";
  if (ROMAN_URDU_RE.test(t)) return "roman_urdu";
  // Soft signal: many Latin words that look like informal Urdu transliteration density
  const tokens = t.toLowerCase().match(/[a-z']+/g) || [];
  const hits = tokens.filter((w) =>
    /^(hai|hain|nahi|kya|kar|mera|tum|aap|bhai|yaar|theek|acha)$/.test(w)
  ).length;
  if (hits >= 2) return "roman_urdu";
  return "english";
}

function languageDirective(style) {
  if (style === "urdu_script") {
    return "User wrote in Urdu script. Reply fluently in Urdu (Arabic script) unless they ask for English. Keep tools/technical terms in English when clearer.";
  }
  if (style === "roman_urdu") {
    return [
      "User is speaking Roman Urdu / Hinglish.",
      "Reply fluently in Roman Urdu (Latin script) — natural, friendly, clear, conversational.",
      "Example tone: 'Ji bilkul, main kar deta hoon.' / 'Theek hai bhai, screen check karta hoon.' / 'Haan samajh gaya, ab yeh step karte hain.'",
      "Mix English only for technical words (file, git, API, window, screenshot) when needed.",
      "Do not switch to heavy Urdu Arabic script unless the user used it.",
      "Keep answers short unless they ask for detail.",
    ].join(" ");
  }
  return "Reply in clear English by default; if user switches to Roman Urdu or Urdu, follow them immediately.";
}

module.exports = { detectLanguageStyle, languageDirective };
