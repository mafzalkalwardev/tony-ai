from tony.voice.wake_word import is_wake_phrase


def test_exact_wake_phrase_detected():
    assert is_wake_phrase("Wake up Tony, Daddy's Home")


def test_wake_phrase_variations_detected():
    assert is_wake_phrase("wake up tony daddy home")
    assert is_wake_phrase("wake up tony")
    assert is_wake_phrase("tony daddy home")
    assert is_wake_phrase("hey tony")
    assert is_wake_phrase("tony wake up")


def test_tony_alone_does_not_wake():
    assert not is_wake_phrase("Tony")
