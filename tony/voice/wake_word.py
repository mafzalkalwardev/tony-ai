"""Wake phrase placeholder for a future opt-in always-listening mode."""

WAKE_PHRASE = "Wake up Tony, Daddy's Home"


def is_wake_word_enabled() -> bool:
    """V2 foundation only: always-listening wake word mode is not active yet."""
    return False


def get_wake_phrase() -> str:
    return WAKE_PHRASE


def is_wake_phrase(text: str) -> bool:
    normalized = _normalize(text)
    accepted = {
        _normalize(WAKE_PHRASE),
        "wake up tony",
        "wake up tony daddy home",
        "wake up tony daddy s home",
        "wake up tony daddy's home",
        "tony daddy home",
        "hey tony",
        "tony wake up",
    }
    return normalized in accepted


def _normalize(text: str) -> str:
    cleaned = text.lower().replace("'", " ")
    for char in [",", ".", "!", "?", "’", "‘", "“", "”"]:
        cleaned = cleaned.replace(char, " ")
    return " ".join(cleaned.split())
