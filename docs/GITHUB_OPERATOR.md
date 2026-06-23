# GitHub Operator

Tony V5 uses the free GitHub CLI `gh`. It does not require GitHub API keys.

## Setup

```powershell
gh auth login
gh auth status
```

## Safe Commands

- GitHub auth status
- Repo info
- List issues
- List PRs
- Generate commit message draft
- Generate PR description draft

## Approval Required

- `git add`
- `git commit`
- `git push`
- `gh issue create`
- `gh pr create`
- `gh release create`

## Blocked

- Force push
- Delete repository
- Delete branch
- Reset hard
- Clean untracked files with `git clean -fd`
- Remove origin
- Printing auth tokens

