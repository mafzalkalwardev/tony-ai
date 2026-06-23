# Action Recorder

Tony V4 can record local actions and screen frames with approval.

## What It Records

- Mouse clicks
- Keyboard key names
- Timestamps
- Workspace path
- Optional screen frames from screen recording

Recordings are saved locally:

```text
tony/logs/action_recordings/
tony/logs/screen_recordings/
```

## Privacy Warning

Action recording may capture private information. Use only on safe screens. Do not record passwords, bank/payment pages, secrets, API keys, tokens, or private messages.

## Replay

Macro replay requires approval every time. Tony uses `pyautogui` only after approval and enables its failsafe.

Replay is blocked if a macro appears to include passwords, payments, message sending, destructive actions, or unknown sensitive external websites.

## Commands

```text
Tony meri actions record karo
Tony screen record karo
Tony recording band karo
Tony last macro replay karo
```
