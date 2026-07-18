"use strict";
const { inferDesktopAction, asCallList } = require("../src/core/toolParse");

function label(msg) {
  return asCallList(inferDesktopAction(msg)).map((c) => {
    const a = JSON.parse(c.function.arguments);
    return c.function.name === "python_tool" ? `python:${a.name}:${a.args?.app_name || a.args?.text || ""}` : c.function.name;
  });
}

const cases = [
  "explorer kholo",
  "notepad kholo",
  "chrome chalao",
  "type hello world",
  'type "TONY"',
  "paste",
  'put "hi" on the clipboard',
  "open calculator",
  "search about SpaceX",
];
for (const m of cases) console.log(m, "=>", label(m).join(" | ") || "(none)");
