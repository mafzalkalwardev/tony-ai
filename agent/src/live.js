"use strict";

const { spawn } = require("child_process");
const path = require("path");
const { ROOT } = require("./config");

const kids = [];

function run(label, command, args, opts = {}) {
  console.log(`[live] starting ${label}: ${command} ${args.join(" ")}`);
  const child = spawn(command, args, {
    cwd: ROOT,
    stdio: "inherit",
    shell: process.platform === "win32",
    env: { ...process.env, ...opts.env },
  });
  child.on("exit", (code, signal) => {
    console.log(`[live] ${label} exited code=${code} signal=${signal}`);
  });
  kids.push(child);
  return child;
}

function shutdown() {
  console.log("[live] shutting down children…");
  for (const c of kids) {
    try {
      c.kill();
    } catch {
      /* ignore */
    }
  }
  process.exit(0);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

// Python bridge
run("bridge", "python", ["-m", "bridge.server"]);

// Gateway
setTimeout(() => {
  run("gateway", "node", ["agent/src/gateway/server.js"]);
}, 800);

// Daemon
setTimeout(() => {
  run("daemon", "node", ["agent/src/daemon/index.js"]);
}, 1600);

console.log("[live] Tony live stack launching (bridge + gateway + daemon). Ctrl+C to stop.");
