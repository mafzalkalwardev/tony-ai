"use strict";

const { config } = require("../config");

async function bridgeHealth() {
  try {
    const res = await fetch(`${config.bridge.url}/health`, {
      headers: { Authorization: `Bearer ${config.bridge.token}` },
      signal: AbortSignal.timeout(2500),
    });
    if (!res.ok) return { ok: false, status: res.status };
    return { ok: true, ...(await res.json()) };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

async function callPythonTool(name, args = {}, { approved = false } = {}) {
  const res = await fetch(`${config.bridge.url}/tools/${encodeURIComponent(name)}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.bridge.token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      args,
      approved,
      workspace: args.workspace || config.bridge.workspace,
    }),
    signal: AbortSignal.timeout(60_000),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    return {
      ok: false,
      status: res.status,
      error: body.error || body.detail || `bridge HTTP ${res.status}`,
      ...body,
    };
  }
  return body;
}

module.exports = { callPythonTool, bridgeHealth };
