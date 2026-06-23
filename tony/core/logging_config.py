from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(log_dir: Path | str = "tony/logs") -> None:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    app_log = path / "app.log"
    error_log = path / "errors.log"

    root = logging.getLogger()
    if any(getattr(handler, "_tony_handler", False) for handler in root.handlers):
        return

    root.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    app_handler = logging.FileHandler(app_log, encoding="utf-8")
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    app_handler._tony_handler = True

    error_handler = logging.FileHandler(error_log, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler._tony_handler = True

    root.addHandler(app_handler)
    root.addHandler(error_handler)
