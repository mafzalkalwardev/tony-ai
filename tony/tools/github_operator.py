from __future__ import annotations

from pathlib import Path

from tony.tools.shell_tool import ShellResult, ShellTool


class GitHubOperator:
    def __init__(self, shell: ShellTool) -> None:
        self.shell = shell

    def check_gh_installed(self, path: Path | str) -> ShellResult:
        result = self.shell.run("gh --version", path)
        if result.exit_code != 0:
            return ShellResult("", "GitHub CLI not found. Install gh first.", result.exit_code)
        return result

    def auth_status(self, path: Path | str) -> ShellResult:
        if self.check_gh_installed(path).exit_code != 0:
            return self.check_gh_installed(path)
        result = self.shell.run("gh auth status", path)
        sanitized = result.stdout.replace("Token:", "Token: [hidden]")
        return ShellResult(sanitized, result.stderr, result.exit_code)

    def repo_view(self, path: Path | str) -> ShellResult:
        return self.shell.run("gh repo view", path)

    def list_issues(self, path: Path | str) -> ShellResult:
        return self.shell.run("gh issue list --limit 20", path)

    def list_prs(self, path: Path | str) -> ShellResult:
        return self.shell.run("gh pr list --limit 20", path)

    def create_issue(self, path: Path | str, title: str, body: str) -> ShellResult:
        return self.shell.run(f'gh issue create --title "{title}" --body "{body}"', path, require_safe=False)

    def create_pr(self, path: Path | str, title: str, body: str, base: str = "main", head: str = "") -> ShellResult:
        head_arg = f' --head "{head}"' if head else ""
        return self.shell.run(f'gh pr create --base "{base}"{head_arg} --title "{title}" --body "{body}"', path, require_safe=False)

    def generate_pr_summary(self, diff_text: str = "") -> str:
        return "# PR Summary\n\n- Purpose: describe the user-facing change\n- Changes: summarize modified files\n- Validation: include tests run\n\nDiff context:\n" + (diff_text[:3000] or "No diff provided.")

    def generate_commit_message(self, status_text: str = "") -> str:
        if "README" in status_text:
            return "docs: update project documentation"
        if "test" in status_text.lower():
            return "test: update coverage"
        return "chore: update Tony AI project"

    def prepare_commit(self, path: Path | str, files: list[str], message: str) -> ShellResult:
        quoted = " ".join(f'"{file}"' for file in files)
        return self.shell.run(f'git add {quoted}; git commit -m "{message}"', path, require_safe=False)

    def push_branch(self, path: Path | str) -> ShellResult:
        return self.shell.run("git push", path, require_safe=False)

