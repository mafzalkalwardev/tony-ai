from tony.core.command_parser import CommandParser


def test_vs_code_kholo_maps_to_open_vscode():
    parsed = CommandParser().parse("VS Code kholo")
    assert parsed.intent == "open_vscode"


def test_repo_status_dikhao_maps_to_git_status():
    parsed = CommandParser().parse("repo status dikhao")
    assert parsed.intent == "git_status"


def test_push_karo_maps_to_git_push():
    parsed = CommandParser().parse("push karo")
    assert parsed.intent == "git_push"

