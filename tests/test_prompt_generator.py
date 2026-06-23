from tony.tools.prompt_generator import PromptGenerator


def test_codex_prompt_includes_project_goal():
    prompt = PromptGenerator().generate_codex_prompt("build dashboard", "PyQt app")
    assert "build dashboard" in prompt
    assert "PyQt app" in prompt


def test_debug_prompt_includes_error_summary():
    prompt = PromptGenerator().generate_debug_prompt("Traceback here", "main.py")
    assert "Traceback here" in prompt
    assert "main.py" in prompt


def test_prompt_does_not_include_secret_marker():
    prompt = PromptGenerator().generate_codex_prompt("fix api key leak", ".env token")
    lowered = prompt.lower()
    assert "api key" not in lowered
    assert ".env" not in lowered

