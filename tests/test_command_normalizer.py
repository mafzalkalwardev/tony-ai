from tony.core.command_normalizer import CommandNormalizer


def test_release_command_normalizer_examples():
    normalizer = CommandNormalizer()

    assert normalizer.normalize("Tony repo status dikhao") == "repo status"
    assert normalizer.normalize("VS Code kholo") == "open vscode"
    assert normalizer.normalize("project analyze karo") == "analyze project"
    assert normalizer.normalize("screen record karo") == "start screen recording"
    assert normalizer.normalize("recording band karo") == "stop recording"
    assert normalizer.normalize("Wake up Tony Daddy's Home repo status dikhao") == "repo status"
    assert normalizer.normalize("Tony mujhe dekh ke seekho") == "start teach mode"
    assert normalizer.normalize("Tony dot env read karo") == "read .env"
