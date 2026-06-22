"""Wake phrase placeholder for a future opt-in always-listening mode."""

WAKE_PHRASE = "Wake up Tony, Daddy's Home"


def is_wake_word_enabled() -> bool:
    """V2 foundation only: always-listening wake word mode is not active yet."""
    return False


def get_wake_phrase() -> str:
    return WAKE_PHRASE
