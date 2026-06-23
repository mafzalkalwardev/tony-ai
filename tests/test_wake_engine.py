from tony.voice.wake_engine import WakeEngine


def test_short_wake_phrase_detected():
    engine = WakeEngine()
    assert engine.detect_wake_phrase(text="Wake Up, Tony!")


def test_full_wake_phrase_detected():
    engine = WakeEngine()
    assert engine.detect_wake_phrase(text="Wake up Tony, Daddy's Home")


def test_tony_only_requires_high_confidence():
    engine = WakeEngine()
    assert not engine.detect_wake_phrase(text="Tony", confidence=0.5)
    assert engine.detect_wake_phrase(text="Tony", confidence=0.95)


def test_wake_phrase_variations():
    engine = WakeEngine()
    assert engine.detect_wake_phrase(text="tony wake up")
    assert engine.detect_wake_phrase(text="hey tony")
