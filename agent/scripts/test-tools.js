const {
  inferDesktopAction,
  parsePseudoToolCalls,
  stripPseudoToolMarkup,
} = require("../src/core/toolParse");

const inferred = inferDesktopAction("can you open youtube in this session of edge?");
console.log("infer", JSON.stringify(inferred, null, 2));

const pseudo = parsePseudoToolCalls(
  '<python_tool name="open_app" approved=true args={"app_name": "YouTube"}></python_tool>'
);
console.log("pseudo", JSON.stringify(pseudo, null, 2));

console.log("strip", stripPseudoToolMarkup("hi <python_tool name=\"x\"></python_tool> there"));
