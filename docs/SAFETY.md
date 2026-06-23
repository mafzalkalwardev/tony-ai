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

Voice transcription can make mistakes, especially with mixed Urdu, Hindi, Roman Urdu, and Hinglish. Tony therefore only auto-runs voice commands when the parsed intent and safety level are clearly safe.

Risky voice commands still require confirmation. Tony accepts typed or spoken confirmations such as:

```text
yes
haan
han
ok
```

Always-listening wake word mode is not active in this version.

Blocked commands stay blocked even when they come from voice.

## V3 Laptop Operator Rules

Tony uses safe tools before any screen-control behavior. It can open known local apps, inspect the current workspace, detect project type, recommend run/test commands, and open localhost.

Tony asks approval before:

- Running project commands
- Running npm/yarn/pnpm scripts
- Running Python app scripts
- Installing dependencies
- Taking screenshots
- Browser automation
- Opening external URLs
- Screen control

Tony blocks:

- Deleting folders
- Reading `.env` contents
- Exposing secrets
- Sending messages or emails
- Payments
- Password changes
- Bulk SMS or calling
- Disabling antivirus or firewall
- Changing system security settings
- Formatting drives

Screenshots are saved locally only and may contain private information. Tony does not upload screenshots, OCR secrets, log in to websites, submit forms, scrape websites, or send messages in V3.

## V4 Live Voice And Recorder Rules

Live voice and wake mode are optional and disabled by default. Push-to-talk and text commands still work if wake-word setup is missing.

Tony asks approval before:

- Starting screen recording
- Starting action recording
- Taking screenshots
- Replaying macros
- Clicking or typing automatically
- Using browser automation
- Submitting forms
- Sending anything externally

Tony blocks:

- Intentionally recording passwords
- Recording bank or payment screens
- Revealing passwords, API keys, secrets, or tokens
- Auto-sending emails/messages
- Bulk SMS or calls
- Replaying destructive actions

Recordings are saved locally only. Tony does not upload recordings or screenshots.

## V5 GitHub, Business, And Code Safety

Safe:

- Repo analysis
- Code scan
- Report generation
- Client message draft generation
- Commit message draft generation
- Listing GitHub issues/PRs
- Daily plan and task listing
- Prompt generation

Needs approval:

- `git add`
- `git commit`
- `git push`
- GitHub issue creation
- GitHub PR creation
- Applying code fixes
- Editing files
- Installing dependencies
- Publishing or sending anything externally

Blocked:

- Reading or exposing `.env`
- Printing API keys, secrets, or tokens
- Force push
- Deleting repos or branches
- `git reset --hard`
- `git clean -fd`
- Removing origin
- Auto-sending emails, WhatsApp, SMS, or calls
- Payment actions
- Password changes

Tony V5 drafts messages and reports only. It does not send them automatically.

## V6 Vision, Observe, Teach, And Replay Safety

Tony asks approval before:

- Looking at the screen
- Analyzing a screenshot
- Starting Observe Mode
- Starting Teach Mode
- Saving workflows with screenshots
- Replaying workflows
- Controlling mouse or keyboard
- Focusing windows

Tony allows safely:

- Listing workflows
- Previewing workflows
- Dry-running workflows
- Stopping observe mode
- Stopping teach mode
- Stopping replay
- Summarizing workflows

Tony blocks:

- Recording passwords, OTP, or 2FA
- Recording banking, payment, or card screens
- Reading `.env`, secrets, API keys, or tokens
- Sending messages or emails automatically
- Submitting forms automatically
- Making payments
- Destructive file actions
- Force push and reset hard

Screenshots, observations, and workflows stay local under `tony/logs/`.
