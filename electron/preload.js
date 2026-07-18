"use strict";

const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("ultron", {
  app: "ultron",
  isElectron: true,
  version: "1.0.0",
});
