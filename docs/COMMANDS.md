# Commands

Tony V1 uses simple rules first. These examples show supported intent detection.

Typed commands and push-to-talk voice transcriptions use the same command parser. Tony shows recognized voice text before running it.

## Spoken Examples

```text
Wake up Tony, Daddy's Home
Tony repo status dikhao
Tony VS Code kholo
Tony error check karo
Tony git push karo but pehle approval lena
```

The wake phrase is reserved for future always-listening mode. In V2, click `Push to Talk` first.

## Open VS Code

```text
VS Code kholo
Tony, VS Code open karo
Visual Studio Code kholo
```

## Open Folder

```text
folder kholo
open folder
directory kholo
```

## Git Status

```text
repo status dikhao
git status
GitHub status dikhao
```

## Git Diff

```text
git diff dikhao
repo diff
```

## Git Commit

```text
commit karo
git commit "update docs"
```

Tony asks for approval before committing.

## Git Push

```text
push karo
git push karo
```

Tony asks for approval before pushing.

## Analyze Project

```text
is repo ka error check karo
project issue check karo
masla dekho
analyze project
```

## Run Shell Command

```text
run npm test
backend start karo
server chalao
```

Unknown shell commands require approval.

## Blocked Example

```text
rm -rf project
del /s important-folder
.env dikhao
```

Tony blocks these.

## Voice Confirmation

```text
yes
haan
han
ok
no
nahi
nahin
```

## V3 Laptop Operator

```text
Tony project analyze karo
Tony project run karo
Tony tests chalao
Tony dependencies install karo
Tony terminal kholo
Tony file explorer kholo
Tony localhost 3000 kholo
Tony screenshot lo
Tony ye folder workspace banao
notepad kholo
calculator kholo
```

Project run, tests, installs, screenshots, and browser automation use the approval system.

## V4 Live Voice And Recorder

```text
Wake Up, Tony!
Wake up Tony, Daddy's Home
Tony live listening start karo
Tony live listening stop karo
Wake mode on karo
Wake mode off karo
Tony screen record karo
Tony meri actions record karo
Tony recording band karo
Tony last macro replay karo
Tony mic check karo
Tony waves dikhao
```

Screen recording, action recording, and macro replay require approval. Dangerous privacy-sensitive requests are blocked.

## V5 GitHub, Business, Reports, Prompts

```text
Tony repo analyze karo
Tony code analyze karo
Tony errors explain karo
Tony fix suggest karo
Tony commit message banao
Tony GitHub status dikhao
Tony issues dikhao
Tony PRs dikhao
Tony client ko update message likh do
Tony delivery report banao
Tony aaj ka plan banao
Tony tasks dikhao
Tony Codex ke liye prompt banao
Tony debugging workflow start karo
Tony push karo
Tony force push karo
Tony .env read karo
```

Drafts and reports are local. GitHub writes, commits, pushes, PRs, and issues require approval. Force push and secret reads are blocked.

## V6 Vision, Observe, Teach, Workflow Memory

```text
Tony screen dekho
Tony look at my screen
Tony observe mode start karo
Tony observe mode stop karo
Tony watch me
Tony mujhe dekh ke seekho
Tony workflow save karo
Tony workflows dikhao
Tony preview workflow
Tony dry run karo
Tony last workflow replay karo
Tony replay band karo
```

Screen observe, screenshot analysis, teaching, and replay require approval. Workflow list, preview, dry run, stop, and summarize are safe.
