from tony.core.command_normalizer import CommandNormalizer
from tony.core.intent_router import IntentRouter


def test_command_normalizer_mixed_language_examples():
    normalizer = CommandNormalizer()

    assert normalizer.normalize("Tony repo status dikhao") == "repo status"
    assert normalizer.normalize("Tony VS Code kholo") == "open vscode"
    assert normalizer.normalize("project run karo") == "run project"
    assert normalizer.normalize("error check karo") == "analyze project"
    assert normalizer.normalize("git push karo") == "git push"
    assert normalizer.normalize("screen record karo") == "start screen recording"
    assert normalizer.normalize("recording band karo") == "stop recording"
    assert normalizer.normalize(".env read karo") == "read .env"
    assert normalizer.normalize("terminal kholo") == "open terminal"


def test_intent_router_maps_common_commands():
    router = IntentRouter()

    assert router.route("repo status dikhao")["intent"] == "git_status"
    assert router.route("VS Code kholo")["intent"] == "open_vscode"
    assert router.route("terminal kholo")["intent"] == "open_terminal"
    assert router.route("project analyze karo")["intent"] == "analyze_project"
    assert router.route("screen record karo")["intent"] == "start_screen_recording"
    assert router.route("client message banao")["intent"] == "generate_client_message"


def test_intent_router_asks_clarifying_questions_for_vague_commands():
    router = IntentRouter()

    website = router.route("open website")
    assert website["needs_clarification"] is True
    assert "Which website" in website["clarifying_question"]

    message = router.route("message banao")
    assert message["needs_clarification"] is True
    assert "message" in message["clarifying_question"]
