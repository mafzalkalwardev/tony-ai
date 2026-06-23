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
        self.safety = SafetySystem()
        self.memory = FakeMemory()
        self.executed = []

    def handle(self, command, approved=False, command_source="text", voice_transcript=None):
        self.executed.append(command)
        return "ok"


def test_simulated_voice_repo_status_routes_to_git_status():
    response = AssistantBrain(FakeAgent()).handle_command("repo status dikhao", source="voice")

    assert response["intent"] == "git_status"
    assert response["status"] == "completed"


def test_simulated_voice_git_push_asks_approval():
    response = AssistantBrain(FakeAgent()).handle_command("git push karo", source="voice")

    assert response["status"] == "waiting_for_approval"


def test_simulated_voice_rm_rf_is_blocked():
    response = AssistantBrain(FakeAgent()).handle_command("rm -rf project", source="voice")

    assert response["status"] == "blocked"
