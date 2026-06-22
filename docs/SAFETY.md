# Safety

Tony Core v1 uses three safety levels.

## SAFE

Safe actions can run immediately. Examples:

- `git status`
- `git diff`
- `dir`
- `ls`
- `pwd`
- Open current folder
- Open VS Code
- Read non-secret files
- Summarize text

## NEEDS_APPROVAL

Tony shows the planned action and asks:

```text
Approve this action? yes/no
```

Examples:

- `git commit`
- `git push`
- `pip install`
- `npm install`
- Editing project files
- Creating many files
- Running unknown scripts
- Browser automation

## BLOCKED

Tony refuses blocked actions. Examples:

- `rm -rf`
- `del /s`
- `rmdir /s`
- `format`
- `cipher /w`
- Reading or exposing `.env`
- Password, secret, or API key exposure
- Payments
- Password changes
- Bulk messages or emails without approval

The block and approval lists live in `config/permissions.json`.

## Voice Safety

Push-to-talk voice commands are transcribed and shown in the UI before Tony runs them. The recognized text goes through the same parser, safety classifier, and approval flow as typed commands.

Risky voice commands still require confirmation. Tony accepts typed or spoken confirmations such as:

```text
yes
haan
han
ok
```

Always-listening wake word mode is not active in this version.
