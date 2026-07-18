"use strict";

/**
 * ULTRON — Electron personal assistant shell around Tony's hybrid brain.
 * Starts the live stack (bridge + gateway + daemon) and opens the Command Deck.
 */
const { app, BrowserWindow, shell, Menu, Tray, nativeImage } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const http = require("http");

const ROOT = path.resolve(__dirname, "..");
const GATEWAY = process.env.TONY_PORT || "8787";
const HUD = `http://127.0.0.1:${GATEWAY}/`;

let mainWindow = null;
let tray = null;
let liveChild = null;
let quitting = false;

function probeGateway() {
  return new Promise((resolve) => {
    const req = http.get(HUD.replace(/\/$/, "") + "/health", { timeout: 2000 }, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

function startLiveStack() {
  if (liveChild) return;
  console.log("[ultron] starting Tony live stack…");
  liveChild = spawn("node", ["agent/src/live.js"], {
    cwd: ROOT,
    env: {
      ...process.env,
      TONY_APP: "ultron",
      TONY_COMPANION_MODE: process.env.TONY_COMPANION_MODE || "true",
    },
    stdio: "inherit",
    shell: process.platform === "win32",
  });
  liveChild.on("exit", (code) => {
    console.log("[ultron] live stack exited", code);
    liveChild = null;
  });
}

async function waitForGateway(maxMs = 45000) {
  const start = Date.now();
  while (Date.now() - start < maxMs) {
    if (await probeGateway()) return true;
    await new Promise((r) => setTimeout(r, 800));
  }
  return false;
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 960,
    minHeight: 640,
    title: "ULTRON — Personal Assistant",
    backgroundColor: "#02060a",
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  mainWindow.loadURL(HUD);
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("close", (e) => {
    if (!quitting && process.platform === "win32") {
      e.preventDefault();
      mainWindow.hide();
    }
  });
}

function createTray() {
  try {
    const img = nativeImage.createEmpty();
    tray = new Tray(img);
    tray.setToolTip("ULTRON Personal Assistant");
    tray.setContextMenu(
      Menu.buildFromTemplate([
        {
          label: "Open ULTRON",
          click: () => {
            if (mainWindow) {
              mainWindow.show();
              mainWindow.focus();
            }
          },
        },
        {
          label: "Reload Deck",
          click: () => mainWindow?.reload(),
        },
        { type: "separator" },
        {
          label: "Quit",
          click: () => {
            quitting = true;
            app.quit();
          },
        },
      ])
    );
    tray.on("double-click", () => mainWindow?.show());
  } catch (err) {
    console.warn("[ultron] tray skipped", err.message);
  }
}

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });

  app.whenReady().then(async () => {
    Menu.setApplicationMenu(null);
    const up = await probeGateway();
    if (!up) startLiveStack();
    const ready = await waitForGateway();
    createWindow();
    createTray();
    if (!ready) {
      mainWindow.loadURL(
        `data:text/html,<html><body style="background:#02060a;color:#6ed6c6;font-family:sans-serif;padding:2rem"><h1>ULTRON</h1><p>Starting Tony core… refresh in a moment.</p></body></html>`
      );
      setTimeout(() => mainWindow.loadURL(HUD), 5000);
    }
  });
}

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    /* keep running in tray on win — only quit via menu */
  }
});

app.on("before-quit", () => {
  quitting = true;
  if (liveChild) {
    try {
      liveChild.kill();
    } catch {
      /* ignore */
    }
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
  else mainWindow?.show();
});
