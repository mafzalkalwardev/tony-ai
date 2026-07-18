"use strict";

/**
 * Lightweight web search for on-demand research (DuckDuckGo Instant Answer + HTML fallback).
 */
async function webSearch(query, { limit = 5 } = {}) {
  const q = String(query || "").trim();
  if (!q) return { ok: false, error: "query required" };

  const hits = [];

  try {
    const url = `https://api.duckduckgo.com/?q=${encodeURIComponent(q)}&format=json&no_html=1&skip_disambig=1`;
    const res = await fetch(url, { signal: AbortSignal.timeout(12_000) });
    const data = await res.json();
    if (data.AbstractText) {
      hits.push({
        title: data.Heading || q,
        snippet: data.AbstractText,
        url: data.AbstractURL || "",
        source: "duckduckgo",
      });
    }
    for (const t of data.RelatedTopics || []) {
      if (hits.length >= limit) break;
      if (t.Text) {
        hits.push({
          title: (t.Text || "").split(" - ")[0].slice(0, 80),
          snippet: t.Text,
          url: t.FirstURL || "",
          source: "duckduckgo",
        });
      } else if (Array.isArray(t.Topics)) {
        for (const sub of t.Topics) {
          if (hits.length >= limit) break;
          if (sub.Text) {
            hits.push({
              title: (sub.Text || "").split(" - ")[0].slice(0, 80),
              snippet: sub.Text,
              url: sub.FirstURL || "",
              source: "duckduckgo",
            });
          }
        }
      }
    }
  } catch (err) {
    return { ok: false, error: err.message, query: q, hits: [] };
  }

  // Wikipedia summary as extra signal
  try {
    const wiki = await fetch(
      `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(q.replace(/\s+/g, "_"))}`,
      { signal: AbortSignal.timeout(8000) }
    );
    if (wiki.ok) {
      const w = await wiki.json();
      if (w.extract) {
        hits.unshift({
          title: w.title || q,
          snippet: w.extract,
          url: w.content_urls?.desktop?.page || "",
          source: "wikipedia",
        });
      }
    }
  } catch {
    /* optional */
  }

  return {
    ok: true,
    query: q,
    hits: hits.slice(0, limit),
    summary: hits[0]?.snippet || `No strong results for "${q}".`,
  };
}

module.exports = { webSearch };
