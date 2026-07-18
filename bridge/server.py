"""Tony Python tool bridge — exposes safe desktop tools to the Node agent."""

from __future__ import annotations

import base64
import json
import os
import tempfile
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("TONY_BRIDGE_TOKEN", "tony-bridge-token")
PORT = int(os.environ.get("TONY_BRIDGE_PORT", "8790"))
_ws = (os.environ.get("TONY_BRIDGE_WORKSPACE") or "").strip()
DEFAULT_WORKSPACE = Path(_ws).expanduser().resolve() if _ws else ROOT

# Ensure repo root is on sys.path for `tony.*` imports
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tony.core.safety import SafetyLevel, SafetySystem  # noqa: E402
from tony.core.screen_context import ScreenContext  # noqa: E402
from tony.tools.app_tool import AppTool  # noqa: E402
from tony.tools.file_tool import FileTool  # noqa: E402
from tony.tools.git_tool import GitTool  # noqa: E402
from tony.tools.shell_tool import ShellTool  # noqa: E402
from tony.tools.vision_tool import VisionTool  # noqa: E402
from tony.tools.window_tool import WindowTool  # noqa: E402
from tony.tools.screenshot_tool import ScreenshotTool  # noqa: E402


safety = SafetySystem()
shell = ShellTool(safety)
git = GitTool(shell)
apps = AppTool()
files = FileTool()
windows = WindowTool()
screenshots = ScreenshotTool()

PHASE3_TOOLS = [
    "git_status",
    "git_diff",
    "git_log",
    "list_dir",
    "read_file",
    "open_app",
    "screen_context",
    "shell_safe",
    "voice_converse_fallback",
    "tts_speak",
    "list_windows",
    "focus_window",
    "type_text",
    "hotkey",
    "mouse_click",
    "mouse_move",
    "scroll",
    "clipboard_get",
    "clipboard_set",
    "copy_file",
    "move_file",
    "screenshot",
    "camera_capture",
    "desktop_status",
    "system_power",
]


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _auth_ok(handler: BaseHTTPRequestHandler) -> bool:
    auth = handler.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip() == TOKEN
    return handler.headers.get("X-Tony-Token", "") == TOKEN


def _workspace(args: dict) -> Path:
    raw = args.get("workspace") or str(DEFAULT_WORKSPACE)
    return Path(raw).expanduser().resolve()


def _needs_approval(tool: str) -> bool:
    return tool in {
        "shell_safe",
        "open_app",
        "screen_context",
        "git_commit",
        "git_push",
        "create_file",
        "screenshot",
        "camera_capture",
        "focus_window",
        "type_text",
        "hotkey",
        "mouse_click",
        "mouse_move",
        "scroll",
        "clipboard_set",
        "copy_file",
        "move_file",
        "system_power",
    }


SAFE_SHELL_PREFIXES = (
    "git status",
    "git diff",
    "git log",
    "dir ",
    "ls ",
    "Get-ChildItem",
    "pwd",
    "echo ",
)


def run_tool(name: str, args: dict, approved: bool) -> dict:
    ws = _workspace(args)

    if name == "git_status":
        result = git.git_status(ws)
        return {"ok": True, "tool": name, "text": result.as_text(), "exit_code": result.exit_code}

    if name == "git_diff":
        result = git.git_diff(ws)
        return {"ok": True, "tool": name, "text": result.as_text(), "exit_code": result.exit_code}

    if name == "git_log":
        limit = int(args.get("limit", 5))
        result = git.git_log(ws, limit=limit)
        return {"ok": True, "tool": name, "text": result.as_text(), "exit_code": result.exit_code}

    if name == "list_dir":
        target = Path(args.get("path") or ws)
        if not target.exists():
            return {"ok": False, "error": f"path not found: {target}"}
        entries = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
        return {"ok": True, "tool": name, "entries": entries[:200]}

    if name == "read_file":
        path = args.get("path")
        if not path:
            return {"ok": False, "error": "path required"}
        text = files.read_file(path)
        return {"ok": True, "tool": name, "text": text[:50_000]}

    if name == "open_app":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "open_app requires approved=true"}
        app_name = args.get("app") or args.get("app_name") or "explorer"
        url = args.get("url")
        text = apps.open_app(app_name, ws, url=url)
        return {"ok": True, "tool": name, "text": text}

    if name == "screen_context":
        decision = safety.classify("observe screen", "observe_screen")
        if decision.level == SafetyLevel.BLOCKED:
            return {"ok": False, "error": decision.reason}
        if decision.level == SafetyLevel.NEEDS_APPROVAL and not approved:
            return {
                "ok": False,
                "needs_approval": True,
                "error": "screen_context requires approved=true",
            }
        ctx = ScreenContext().capture_context(VisionTool(), workspace_path=ws)
        return {
            "ok": True,
            "tool": name,
            "summary": ctx.summarize_context(),
            "sensitive": ctx.is_sensitive(),
            "window": ctx.active_window_title,
            "process": ctx.process_name,
        }

    if name == "shell_safe":
        command = str(args.get("command") or "").strip()
        if not command:
            return {"ok": False, "error": "command required"}
        decision = safety.classify(command, "run_shell_command")
        if decision.level == SafetyLevel.BLOCKED:
            return {"ok": False, "error": decision.reason}
        if decision.level == SafetyLevel.NEEDS_APPROVAL and not approved:
            return {"ok": False, "needs_approval": True, "error": decision.reason}
        lowered = command.lower()
        if not any(lowered.startswith(p.lower()) for p in SAFE_SHELL_PREFIXES) and not approved:
            return {
                "ok": False,
                "needs_approval": True,
                "error": "shell_safe only allows read-only prefixes unless approved=true",
            }
        result = shell.run(command, ws, require_safe=True)
        return {"ok": result.exit_code == 0, "tool": name, "text": result.as_text(), "exit_code": result.exit_code}

    if name == "voice_converse_fallback":
        return voice_fallback(args)

    if name == "tts_speak":
        from tony.voice.tts import TextToSpeech

        text = str(args.get("text") or "")
        out = TextToSpeech().speak(text)
        ok = out == "Spoken."
        return {"ok": ok, "tool": name, "text": out, "spoken": ok}

    if name == "list_windows":
        titles = windows.list_open_windows()
        return {"ok": True, "tool": name, "windows": titles[:40], "active": windows.get_active_window_title()}

    if name == "focus_window":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "focus_window requires approved=true"}
        title = str(args.get("title") or args.get("window") or "").strip()
        text = windows.focus_window(title)
        return {"ok": True, "tool": name, "text": text}

    if name == "type_text":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "type_text requires approved=true"}
        return desktop_type_text(args)

    if name == "hotkey":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "hotkey requires approved=true"}
        return desktop_hotkey(args)

    if name == "mouse_click":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "mouse_click requires approved=true"}
        return desktop_click(args)

    if name == "mouse_move":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "mouse_move requires approved=true"}
        return desktop_move(args)

    if name == "scroll":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "scroll requires approved=true"}
        return desktop_scroll(args)

    if name == "clipboard_get":
        return desktop_clipboard_get()

    if name == "clipboard_set":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "clipboard_set requires approved=true"}
        return desktop_clipboard_set(args)

    if name == "copy_file":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "copy_file requires approved=true"}
        src = args.get("src") or args.get("source")
        dest = args.get("dest") or args.get("destination")
        if not src or not dest:
            return {"ok": False, "error": "src and dest required"}
        text = files.copy_file(src, dest)
        return {"ok": True, "tool": name, "text": text}

    if name == "move_file":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "move_file requires approved=true"}
        src = args.get("src") or args.get("source")
        dest = args.get("dest") or args.get("destination")
        if not src or not dest:
            return {"ok": False, "error": "src and dest required"}
        text = files.move_file(src, dest)
        return {"ok": True, "tool": name, "text": text}

    if name == "screenshot":
        decision = safety.classify("take screenshot", "take_screenshot")
        if decision.level == SafetyLevel.BLOCKED:
            return {"ok": False, "error": decision.reason}
        if decision.level == SafetyLevel.NEEDS_APPROVAL and not approved:
            return {"ok": False, "needs_approval": True, "error": "screenshot requires approved=true"}
        path = screenshots.take_screenshot()
        return {"ok": True, "tool": name, "text": path}

    if name == "camera_capture":
        if not approved:
            return {"ok": False, "needs_approval": True, "error": "camera_capture requires approved=true"}
        return camera_capture(args)

    if name == "desktop_status":
        return {
            "ok": True,
            "tool": name,
            "active_window": windows.get_active_window_title(),
            "window_count": len(windows.list_open_windows()),
            "workspace": str(ws),
            "phase": 4,
        }

    if name == "system_power":
        if not approved:
            return {
                "ok": False,
                "needs_approval": True,
                "error": "system_power requires approved=true (explicit user ask)",
            }
        return desktop_system_power(args)

    return {"ok": False, "error": f"unknown tool: {name}", "needs_approval": _needs_approval(name)}


def desktop_system_power(args: dict) -> dict:
    """Windows power control. Shutdown/restart use a cancelable delay by default."""
    import subprocess

    action = str(args.get("action") or args.get("mode") or "shutdown").lower().strip()
    # Default 60s so user can abort with: shutdown /a  OR  "cancel shutdown"
    delay = int(args.get("delay") if args.get("delay") is not None else 60)
    delay = max(0, min(delay, 600))

    try:
        if action in {"abort", "cancel", "abort_shutdown", "cancel_shutdown"}:
            subprocess.run(["shutdown", "/a"], check=False, capture_output=True, text=True)
            return {
                "ok": True,
                "tool": "system_power",
                "action": "abort",
                "text": "Shutdown cancelled (if one was pending).",
            }

        if action in {"sleep", "suspend"}:
            # Hibernate/sleep via powercfg / rundll — sleep
            subprocess.Popen(
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"],
                shell=False,
            )
            return {"ok": True, "tool": "system_power", "action": "sleep", "text": "Sleep requested."}

        if action in {"restart", "reboot"}:
            subprocess.run(
                ["shutdown", "/r", "/t", str(delay), "/c", "TONY: restart scheduled"],
                check=False,
                capture_output=True,
                text=True,
            )
            return {
                "ok": True,
                "tool": "system_power",
                "action": "restart",
                "delay": delay,
                "text": f"Restart in {delay}s. Say 'cancel shutdown' or run: shutdown /a",
            }

        if action in {"shutdown", "poweroff", "shut_down", "off"}:
            subprocess.run(
                ["shutdown", "/s", "/t", str(delay), "/c", "TONY: shutdown scheduled"],
                check=False,
                capture_output=True,
                text=True,
            )
            return {
                "ok": True,
                "tool": "system_power",
                "action": "shutdown",
                "delay": delay,
                "text": f"Shutting down in {delay}s. Say 'cancel shutdown' or run: shutdown /a",
            }

        return {"ok": False, "error": f"unknown action: {action}. Use shutdown|restart|sleep|abort"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def desktop_type_text(args: dict) -> dict:
    text = str(args.get("text") or "")
    if not text:
        return {"ok": False, "error": "text required"}
    # Block secrets-looking payloads
    if any(k in text.lower() for k in ("password", "otp", "api_key", "secret=", "bearer ")):
        return {"ok": False, "error": "refused: looks like a secret"}
    try:
        import pyautogui

        interval = float(args.get("interval", 0.02))
        pyautogui.write(text, interval=max(0.0, min(interval, 0.2)))
        return {"ok": True, "tool": "type_text", "chars": len(text)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def desktop_hotkey(args: dict) -> dict:
    keys = args.get("keys") or args.get("key")
    if isinstance(keys, str):
        keys = [k.strip() for k in keys.replace("+", " ").split() if k.strip()]
    if not isinstance(keys, list) or not keys:
        return {"ok": False, "error": "keys required e.g. ['ctrl','c']"}
    allowed = {"ctrl", "alt", "shift", "win", "tab", "enter", "esc", "space", "up", "down", "left", "right"}
    norm = [str(k).lower() for k in keys][:4]
    for k in norm:
        if k not in allowed and len(k) != 1:
            return {"ok": False, "error": f"key not allowed: {k}"}
    try:
        import pyautogui

        pyautogui.hotkey(*norm)
        return {"ok": True, "tool": "hotkey", "keys": norm}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def desktop_click(args: dict) -> dict:
    try:
        import pyautogui

        x = int(args.get("x", 0))
        y = int(args.get("y", 0))
        button = str(args.get("button", "left"))
        clicks = int(args.get("clicks", 1))
        if x < 0 or y < 0:
            return {"ok": False, "error": "x/y must be >= 0"}
        pyautogui.click(x=x, y=y, clicks=max(1, min(clicks, 3)), button=button)
        return {"ok": True, "tool": "mouse_click", "x": x, "y": y, "button": button}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def desktop_move(args: dict) -> dict:
    try:
        import pyautogui

        x = int(args.get("x", 0))
        y = int(args.get("y", 0))
        duration = float(args.get("duration", 0.2))
        pyautogui.moveTo(x, y, duration=max(0.0, min(duration, 2.0)))
        return {"ok": True, "tool": "mouse_move", "x": x, "y": y}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def desktop_scroll(args: dict) -> dict:
    try:
        import pyautogui

        clicks = int(args.get("clicks") or args.get("amount") or -3)
        pyautogui.scroll(max(-20, min(20, clicks)))
        return {"ok": True, "tool": "scroll", "clicks": clicks}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def desktop_clipboard_get() -> dict:
    try:
        import pyperclip  # type: ignore

        text = pyperclip.paste()
        return {"ok": True, "tool": "clipboard_get", "text": str(text)[:5000]}
    except Exception:
        try:
            import subprocess

            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", "Get-Clipboard"], text=True)
            return {"ok": True, "tool": "clipboard_get", "text": out[:5000]}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}


def desktop_clipboard_set(args: dict) -> dict:
    text = str(args.get("text") or "")
    if any(k in text.lower() for k in ("password", "otp", "api_key", "secret=", "bearer ")):
        return {"ok": False, "error": "refused: looks like a secret"}
    try:
        import pyperclip  # type: ignore

        pyperclip.copy(text)
        return {"ok": True, "tool": "clipboard_set", "chars": len(text)}
    except Exception:
        try:
            import subprocess

            subprocess.run(
                ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value @'\n{text}\n'@"],
                check=True,
            )
            return {"ok": True, "tool": "clipboard_set", "chars": len(text)}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}


def camera_capture(args: dict) -> dict:
    """Grab one webcam frame locally (Phase 3)."""
    out_dir = ROOT / "tony" / "logs" / "camera"
    out_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime

    path = out_dir / f"camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    try:
        import cv2  # type: ignore

        cam_index = int(args.get("index", 0))
        cap = cv2.VideoCapture(cam_index)
        if not cap.isOpened():
            return {"ok": False, "error": f"webcam {cam_index} unavailable"}
        ok, frame = cap.read()
        cap.release()
        if not ok or frame is None:
            return {"ok": False, "error": "failed to read webcam frame"}
        cv2.imwrite(str(path), frame)
        return {
            "ok": True,
            "tool": "camera_capture",
            "path": str(path.resolve()),
            "note": "Frame saved locally. Vision understanding uses screen tools / future VLM.",
        }
    except ImportError:
        return {"ok": False, "error": "opencv-python not installed"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def voice_fallback(args: dict) -> dict:
    """STT (+ optional TTS) when Voicebox is unavailable."""
    from tony.voice.stt import SpeechToText
    from tony.voice.tts import TextToSpeech

    audio_b64 = args.get("audioBase64") or ""
    if not audio_b64:
        return {"ok": False, "error": "audioBase64 required"}
    raw = base64.b64decode(audio_b64)
    suffix = ".webm" if "webm" in str(args.get("mimeType") or "") else ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(raw)
        tmp_path = Path(tmp.name)
    try:
        stt = SpeechToText()
        # Prefer file transcription if available
        transcript = ""
        error = ""
        if hasattr(stt, "transcribe_file"):
            result = stt.transcribe_file(tmp_path)
            transcript = getattr(result, "text", "") or ""
            error = getattr(result, "error", "") or ""
        elif hasattr(stt, "transcribe_wav"):
            result = stt.transcribe_wav(tmp_path)
            transcript = getattr(result, "text", "") or ""
            error = getattr(result, "error", "") or ""
        else:
            # Minimal: try wave + internal model path
            try:
                from faster_whisper import WhisperModel

                model = WhisperModel("base", compute_type="int8")
                segments, _info = model.transcribe(str(tmp_path))
                transcript = " ".join(s.text.strip() for s in segments).strip()
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
        if not transcript:
            return {"ok": False, "error": error or "empty transcript", "transcript": ""}
        # Fallback does not run full agent — gateway will agent on transcript when returned empty reply
        return {"ok": True, "transcript": transcript, "text": transcript, "speech": None}
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # quieter
        sys.stderr.write("[bridge] " + (fmt % args) + "\n")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            if not _auth_ok(self):
                return _json_response(self, 401, {"ok": False, "error": "unauthorized"})
            return _json_response(
                self,
                200,
                {
                    "ok": True,
                    "service": "tony-python-bridge",
                    "port": PORT,
                    "workspace": str(DEFAULT_WORKSPACE),
                    "tools": PHASE3_TOOLS,
                },
            )
        return _json_response(self, 404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if not _auth_ok(self):
            return _json_response(self, 401, {"ok": False, "error": "unauthorized"})
        if not parsed.path.startswith("/tools/"):
            return _json_response(self, 404, {"ok": False, "error": "not found"})
        name = parsed.path[len("/tools/") :].strip("/")
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return _json_response(self, 400, {"ok": False, "error": "invalid json"})
        args = payload.get("args") or {}
        if "workspace" in payload and "workspace" not in args:
            args["workspace"] = payload["workspace"]
        approved = bool(payload.get("approved"))
        try:
            result = run_tool(name, args, approved)
            status = 200 if result.get("ok") or result.get("needs_approval") else 400
            if result.get("needs_approval"):
                status = 403
            return _json_response(self, status, result)
        except Exception as exc:  # noqa: BLE001
            return _json_response(
                self,
                500,
                {"ok": False, "error": str(exc), "trace": traceback.format_exc()[-2000:]},
            )


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[bridge] Tony Python bridge on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[bridge] stopped")


if __name__ == "__main__":
    main()
