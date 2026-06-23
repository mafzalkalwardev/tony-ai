from tony.core.observation_manager import ObservationManager
from tony.core.safety import SafetyLevel, SafetySystem


def test_observe_mode_default_off():
    manager = ObservationManager()

    assert manager.mode == "idle"
    assert manager.is_running() is False


def test_replay_workflow_needs_approval():
    decision = SafetySystem().classify("Tony last workflow replay karo", "replay_workflow")

    assert decision.level == SafetyLevel.NEEDS_APPROVAL


def test_dry_run_workflow_safe():
    decision = SafetySystem().classify("Tony dry run karo", "dry_run_workflow")

    assert decision.level == SafetyLevel.SAFE


def test_password_recording_blocked():
    decision = SafetySystem().classify("Tony password record karo", "start_teach_mode")

    assert decision.level == SafetyLevel.BLOCKED


def test_payment_screen_recording_blocked():
    decision = SafetySystem().classify("Tony payment screen record karo", "start_teach_mode")

    assert decision.level == SafetyLevel.BLOCKED
