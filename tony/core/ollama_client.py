from __future__ import annotations

import json
from pathlib import Path

import requests


_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
_SETTINGS_PATH = _CONFIG_DIR / "settings.json"


class OllamaClient:
    def __init__(self, settings_path: Path | str = _SETTINGS_PATH) -> None:
        self.settings = json.loads(Path(settings_path).read_text(encoding="utf-8"))
        self.base_url = self.settings.get("ollama_base_url", "http://localhost:11434").rstrip("/")
        self.model = self.settings.get("ollama_model", "qwen3:4b")

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.RequestException:
            return "Ollama is not running. Start Ollama and install a model, then try again."

