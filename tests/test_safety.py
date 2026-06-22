from tony.core.safety import SafetyLevel, SafetySystem


def test_git_status_is_safe():
    safety = SafetySystem()
    assert safety.classify("git status", "git_status").level == SafetyLevel.SAFE


def test_git_push_needs_approval():
    safety = SafetySystem()
    assert safety.classify("git push", "git_push").level == SafetyLevel.NEEDS_APPROVAL


def test_rm_rf_is_blocked():
    safety = SafetySystem()
    assert safety.classify("rm -rf project", "run_shell_command").level == SafetyLevel.BLOCKED


def test_spoken_yes_with_punctuation_is_approval():
    safety = SafetySystem()
    assert safety.is_approved_text("yes.")
