# Workflow Memory

Tony stores workflow memory locally in SQLite:

```text
tony/logs/tony_memory.db
```

## Tables

- `workflows`
- `workflow_steps`
- `workflow_runs`
- `screen_observations`

## Usage

```text
Tony workflows dikhao
Tony preview workflow
Tony dry run karo
Tony last workflow replay karo
```

List, preview, dry run, stop, and summarize are safe. Replay requires approval every time. Tony blocks workflows containing password, payment, banking, secret, token, auto-send, or destructive markers.
