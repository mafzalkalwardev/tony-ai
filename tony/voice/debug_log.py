from __future__ import annotations

import logging
from pathlib import Path


def voice_debug(message: str) -> None:
    log_path = Path("tony/logs/voice_debug.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("tony.voice")
    logger.setLevel(logging.INFO)
    if not any(getattr(handler, "_tony_voice_debug", False) for handler in logger.handlers):
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        handler._tony_voice_debug = True
        logger.addHandler(handler)
        logger.propagate = False
    logger.info(message)
