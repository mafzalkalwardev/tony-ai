from tony.core.assistant_brain import AssistantBrain
from tony.core.safety import SafetySystem


class FakeMemory:
    def log_task(self, *args, **kwargs):
        pass

    def log_task_output(self, *args, **kwargs):
        pass

    def log_voice_transcript(self, *args, **kwargs):
        pass


class FakeAgent:
    def __init__(self):
        self.memory = FakeMemory()
        self.safety = SafetySystem()
        self.executed = []

    def handle(self, command, approved=False, command_source="text", voice_transcript=None):
        self.executed.append((command, approved, command_source, voice_transcript))
        return f"executed {command}"


def test_text_and_voice_commands_use_same_pipeline():
    agent = FakeAgent()
    brain = AssistantBrain(agent)

    text_response = brain.handle_command("repo status dikhao", source="text")
    voice_response = brain.handle_command("Tony repo status dikhao", source="voice")

    assert text_response["intent"] == voice_response["intent"] == "git_status"
    assert text_response["normalized_text"] == voice_response["normalized_text"] == "repo status"
    assert agent.executed[0][2] == "text"
    assert agent.executed[1][2] == "voice"


def test_repo_status_returns_safe_completed_route():
    response = AssistantBrain(FakeAgent()).handle_command("repo status dikhao")

    assert response["status"] == "completed"
    assert response["intent"] == "git_status"
    assert response["safety"] == "SAFE"


def test_git_push_waits_for_approval_then_yes_executes():
    agent = FakeAgent()
    brain = AssistantBrain(agent)

    pending = brain.handle_command("git push karo", source="voice")

    assert pending["status"] == "waiting_for_approval"
    assert pending["intent"] == "git_push"
    assert not agent.executed

    approved = brain.handle_command("yes", source="voice")

    assert approved["status"] == "completed"
    assert agent.executed[-1][0] == "git push karo"
    assert agent.executed[-1][1] is True
    assert agent.executed[-1][2] == "voice"


def test_rm_rf_is_blocked():
    response = AssistantBrain(FakeAgent()).handle_command("rm -rf project")

    assert response["status"] == "blocked"
    assert response["safety"] == "BLOCKED"


def test_vague_command_asks_clarification():
    response = AssistantBrain(FakeAgent()).handle_command("open website")

    assert response["status"] == "clarification"
    assert "Which website" in response["reply"]


def test_empty_transcript_does_nothing_helpfully():
    response = AssistantBrain(FakeAgent()).handle_command("", source="voice")

    assert response["status"] == "clarification"
    assert "did not catch" in response["reply"]


def test_wake_phrase_only_is_acknowledged():
    response = AssistantBrain(FakeAgent()).handle_command("Wake Up Tony", source="voice")

    assert response["status"] == "completed"
    assert response["intent"] == "wake_phrase"
