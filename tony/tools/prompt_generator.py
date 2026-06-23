from __future__ import annotations


class PromptGenerator:
    SECRET_MARKERS = ["api key", "secret", "token", "password", ".env"]

    def generate_codex_prompt(self, goal: str, project_context: str = "") -> str:
        return self._clean(f"Continue this project. Goal: {goal}\n\nProject context:\n{project_context}\n\nInspect first, keep changes scoped, run tests, and report results.")

    def generate_debug_prompt(self, error: str, files: str = "") -> str:
        return self._clean(f"Debug this issue.\n\nError summary:\n{error}\n\nRelevant files:\n{files}\n\nFind root cause, propose a focused fix, implement carefully, and run tests.")

    def generate_refactor_prompt(self, module: str) -> str:
        return self._clean(f"Refactor module `{module}` safely. Preserve behavior, improve clarity, and add/update tests.")

    def generate_ui_prompt(self, description: str) -> str:
        return self._clean(f"Improve the UI: {description}\nKeep it responsive, accessible, and consistent with the existing design.")

    def generate_github_prompt(self, task: str) -> str:
        return self._clean(f"Use GitHub workflow safely for this task: {task}\nSummarize diffs, checks, and approval points.")

    def generate_client_delivery_prompt(self, context: str) -> str:
        return self._clean(f"Draft a professional client delivery update using this context:\n{context}")

    def _clean(self, text: str) -> str:
        cleaned = text
        for marker in self.SECRET_MARKERS:
            cleaned = cleaned.replace(marker, "[redacted]")
        return cleaned
