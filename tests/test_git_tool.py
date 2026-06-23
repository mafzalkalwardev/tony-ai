from tony.tools.git_tool import GitTool
from tony.tools.shell_tool import ShellResult


class FakeShell:
    def __init__(self):
        self.commands = []

    def run(self, command, path, timeout=60, require_safe=True):
        self.commands.append((command, require_safe))
        return ShellResult("ok", "", 0)


def test_git_tool_uses_subprocess_wrapper_safely(tmp_path):
    shell = FakeShell()
    git = GitTool(shell)

    result = git.git_status(tmp_path)

    assert result.stdout == "ok"
    assert shell.commands[-1] == ("git status --short", True)


def test_git_push_marks_safe_wrapper_bypass_for_approval_layer(tmp_path):
    shell = FakeShell()
    git = GitTool(shell)

    git.git_push(tmp_path)

    assert shell.commands[-1] == ("git push", False)
