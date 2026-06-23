from tony.core.task_runner import WakeWorker
from tony.voice.stt import TranscriptionResult


class FakeLiveState:
    wake_mode_enabled = True


class FakeMemory:
    def log_wake_event(self, phrase):
        self.phrase = phrase


class FakeWakeEngine:
    def detect_wake_phrase(self, text=""):
        return "wake up tony" in text.lower()


class FakeAgent:
    def __init__(self):
        self.live_state = FakeLiveState()
        self.wake_engine = FakeWakeEngine()
        self.memory = FakeMemory()
        self.calls = 0

    def enable_wake_mode(self):
        self.live_state.wake_mode_enabled = True
        return "on"

    def transcribe_wake_phrase_chunk(self, level_callback=None, status_callback=None):
        self.calls += 1
        if level_callback:
            level_callback(0.5)
        if status_callback:
            status_callback("Transcribing")
        if self.calls == 1:
            return TranscriptionResult("", "I could not hear a clear command. Please try again.")
        return TranscriptionResult("Wake Up Tony")


def test_wake_worker_emits_wake_transcript_after_unclear_chunk():
    worker = WakeWorker(FakeAgent())
    transcripts = []
    finished = []
    levels = []

    worker.signals.wake_transcript_ready.connect(transcripts.append)
    worker.signals.finished.connect(finished.append)
    worker.signals.level.connect(levels.append)

    worker.run()

    assert transcripts == ["Wake Up Tony"]
    assert finished == ["Wake Up Tony"]
    assert levels
