"use strict";

const { config } = require("./config");
const { runAgent } = require("./core/agent");

async function main() {
  const [, , cmd, ...rest] = process.argv;
  if (cmd === "health") {
    const res = await fetch(`http://127.0.0.1:${config.port}/health`);
    console.log(await res.text());
    return;
  }
  if (cmd === "run") {
    const message = rest.join(" ") || "Hello Tony";
    const out = await runAgent(message);
    console.log(out.reply);
    return;
  }
  if (cmd === "chat") {
    const readline = require("readline");
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    console.log("Tony chat (Ctrl+C to exit)");
    const ask = () =>
      rl.question("> ", async (line) => {
        if (!line.trim()) return ask();
        const out = await runAgent(line.trim());
        console.log(out.reply);
        ask();
      });
    ask();
    return;
  }
  console.log("Usage: node agent/src/cli.js <chat|run|health> [message]");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
