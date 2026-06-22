# Commands

Tony V1 uses simple rules first. These examples show supported intent detection.

Typed commands and push-to-talk voice transcriptions use the same command parser. Tony shows recognized voice text before running it.

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
