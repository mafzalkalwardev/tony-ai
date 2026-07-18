"use strict";

const fs = require("fs");
const path = require("path");
const { config } = require("../config");

function walkMarkdown(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const name of fs.readdirSync(dir)) {
    if (name.startsWith(".")) continue;
    const full = path.join(dir, name);
    const st = fs.statSync(full);
    if (st.isDirectory()) walkMarkdown(full, out);
    else if (/\.md$/i.test(name)) out.push(full);
  }
  return out;
}

function extractWikiLinks(text) {
  const links = [];
  const re = /\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]/g;
  let m;
  while ((m = re.exec(text))) links.push(m[1].trim());
  return links;
}

function extractTags(text) {
  const tags = [];
  const re = /(^|\s)#([a-zA-Z0-9_/-]{2,40})/g;
  let m;
  while ((m = re.exec(text))) tags.push(m[2].toLowerCase());
  return [...new Set(tags)];
}

function tokenize(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s_-]+/gu, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2)
    .slice(0, 400);
}

function graphPath() {
  return path.join(config.dataDir, "brain_graph.json");
}

function rebuildGraph() {
  const root = config.vaultDir;
  const files = walkMarkdown(root);
  const nodes = new Map();
  const edges = [];

  function ensureNode(id, type, meta = {}) {
    if (!nodes.has(id)) nodes.set(id, { id, type, ...meta });
    else Object.assign(nodes.get(id), meta);
  }

  for (const file of files) {
    const rel = path.relative(root, file).replace(/\\/g, "/");
    const raw = fs.readFileSync(file, "utf8");
    const title = path.basename(file, ".md");
    const nodeId = `note:${rel}`;
    ensureNode(nodeId, "note", {
      title,
      path: rel,
      preview: raw.slice(0, 220).replace(/\s+/g, " "),
      updatedAt: fs.statSync(file).mtime.toISOString(),
      words: tokenize(raw).length,
    });

    for (const link of extractWikiLinks(raw)) {
      const target = `wiki:${link}`;
      ensureNode(target, "wiki", { title: link });
      edges.push({ from: nodeId, to: target, kind: "wikilink" });
    }
    for (const tag of extractTags(raw)) {
      const tagId = `tag:${tag}`;
      ensureNode(tagId, "tag", { title: `#${tag}` });
      edges.push({ from: nodeId, to: tagId, kind: "tag" });
    }

    // keyword hubs (top terms)
    const counts = {};
    for (const w of tokenize(raw)) counts[w] = (counts[w] || 0) + 1;
    const top = Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);
    for (const [term, n] of top) {
      if (n < 2) continue;
      const termId = `term:${term}`;
      ensureNode(termId, "term", { title: term });
      edges.push({ from: nodeId, to: termId, kind: "mentions", weight: n });
    }
  }

  const graph = {
    builtAt: new Date().toISOString(),
    vault: root,
    nodeCount: nodes.size,
    edgeCount: edges.length,
    nodes: [...nodes.values()],
    edges,
  };
  fs.mkdirSync(config.dataDir, { recursive: true });
  fs.writeFileSync(graphPath(), JSON.stringify(graph, null, 2), "utf8");

  // Also write an Obsidian-friendly index note
  const indexDir = path.join(root, "Agentic Brain");
  fs.mkdirSync(indexDir, { recursive: true });
  const indexNote = [
    `# Tony Brain Graph`,
    "",
    `Built: ${graph.builtAt}`,
    `Notes indexed: ${files.length}`,
    `Nodes: ${graph.nodeCount} · Edges: ${graph.edgeCount}`,
    "",
    "## Recent notes",
    ...files
      .slice(-15)
      .reverse()
      .map((f) => `- [[${path.basename(f, ".md")}]] — ${path.relative(root, f).replace(/\\/g, "/")}`),
    "",
  ].join("\n");
  fs.writeFileSync(path.join(indexDir, "GRAPH.md"), indexNote, "utf8");

  return {
    ok: true,
    notes: files.length,
    nodeCount: graph.nodeCount,
    edgeCount: graph.edgeCount,
    path: graphPath(),
  };
}

function loadGraph() {
  if (!fs.existsSync(graphPath())) rebuildGraph();
  try {
    return JSON.parse(fs.readFileSync(graphPath(), "utf8"));
  } catch {
    return rebuildGraph() && JSON.parse(fs.readFileSync(graphPath(), "utf8"));
  }
}

function searchBrain(query, { limit = 8 } = {}) {
  const q = String(query || "").toLowerCase().trim();
  if (!q) return { ok: false, error: "query required" };
  const root = config.vaultDir;
  const files = walkMarkdown(root);
  const hits = [];
  for (const file of files) {
    const raw = fs.readFileSync(file, "utf8");
    const lower = raw.toLowerCase();
    if (!lower.includes(q) && !path.basename(file).toLowerCase().includes(q)) continue;
    const idx = lower.indexOf(q);
    const start = Math.max(0, idx - 60);
    const snippet = raw.slice(start, start + 160).replace(/\s+/g, " ");
    hits.push({
      path: path.relative(root, file).replace(/\\/g, "/"),
      title: path.basename(file, ".md"),
      snippet,
      score: (lower.split(q).length - 1) * 2 + (path.basename(file).toLowerCase().includes(q) ? 5 : 0),
    });
  }
  hits.sort((a, b) => b.score - a.score);
  return { ok: true, query: q, hits: hits.slice(0, limit) };
}

function relatedNodes(query, { limit = 12 } = {}) {
  const graph = loadGraph();
  const q = String(query || "").toLowerCase().trim();
  let matched = q
    ? graph.nodes.filter(
        (n) =>
          String(n.title || "").toLowerCase().includes(q) ||
          String(n.id || "").toLowerCase().includes(q) ||
          String(n.preview || "").toLowerCase().includes(q)
      )
    : [];

  // Default HUD view: recent notes + tags so the canvas always looks alive
  if (matched.length < 4) {
    const notes = graph.nodes
      .filter((n) => n.type === "note")
      .sort((a, b) => String(b.updatedAt || "").localeCompare(String(a.updatedAt || "")))
      .slice(0, Math.max(limit, 8));
    const tags = graph.nodes.filter((n) => n.type === "tag").slice(0, 6);
    const wiki = graph.nodes.filter((n) => n.type === "wiki").slice(0, 4);
    const byId = new Map([...notes, ...tags, ...wiki, ...matched].map((n) => [n.id, n]));
    matched = [...byId.values()];
  }

  const ids = new Set(matched.map((n) => n.id));
  const related = [];
  for (const e of graph.edges) {
    if (ids.has(e.from) || ids.has(e.to)) related.push(e);
  }

  // Pull in neighbors so edges render fully
  for (const e of related) {
    for (const id of [e.from, e.to]) {
      if (!ids.has(id)) {
        const n = graph.nodes.find((x) => x.id === id);
        if (n) {
          matched.push(n);
          ids.add(id);
        }
      }
    }
  }

  return {
    ok: true,
    query,
    nodes: matched.slice(0, Math.max(limit, 18)),
    edges: related.slice(0, limit * 3),
    stats: { nodeCount: graph.nodeCount, edgeCount: graph.edgeCount, builtAt: graph.builtAt },
  };
}

function writeNote({ title, body, folder = "Agentic Brain/Inbox" } = {}) {
  const cleanTitle = String(title || "note")
    .replace(/[<>:"/\\|?*]/g, "-")
    .slice(0, 80)
    .trim() || "note";
  const dir = path.join(config.vaultDir, folder);
  fs.mkdirSync(dir, { recursive: true });
  const stamp = new Date().toISOString().slice(0, 10);
  const file = path.join(dir, `${cleanTitle}-${stamp}.md`);
  const content = [
    `# ${cleanTitle}`,
    "",
    `created: ${new Date().toISOString()}`,
    `tags: #tony #brain`,
    "",
    String(body || "").trim(),
    "",
  ].join("\n");
  fs.writeFileSync(file, content, "utf8");
  // light rebuild so graph stays fresh
  try {
    rebuildGraph();
  } catch {
    /* ignore */
  }
  return { ok: true, path: path.relative(config.vaultDir, file).replace(/\\/g, "/") };
}

function brainStats() {
  const graph = fs.existsSync(graphPath()) ? loadGraph() : null;
  const notes = walkMarkdown(config.vaultDir).length;
  return {
    vault: config.vaultDir,
    notes,
    nodeCount: graph?.nodeCount || 0,
    edgeCount: graph?.edgeCount || 0,
    builtAt: graph?.builtAt || null,
  };
}

function brainPromptHints(query = "") {
  const hits = query ? searchBrain(query, { limit: 4 }).hits || [] : [];
  if (!hits.length) return "";
  return [
    "Obsidian brain hits:",
    ...hits.map((h) => `- ${h.title}: ${h.snippet}`),
  ].join("\n");
}

module.exports = {
  rebuildGraph,
  loadGraph,
  searchBrain,
  relatedNodes,
  writeNote,
  brainStats,
  brainPromptHints,
};
