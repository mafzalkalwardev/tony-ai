from tony.tools.github_operator import GitHubOperator
from tony.tools.shell_tool import ShellResult


class MissingGhShell:
    def run(self, command, path, timeout=60, require_safe=True):
        return ShellResult("", "missing", 127)


def test_github_operator_handles_missing_gh(tmp_path):
    operator = GitHubOperator(MissingGhShell())

    result = operator.check_gh_installed(tmp_path)

    assert result.exit_code == 127
    assert "GitHub CLI not found" in result.stderr
