from __future__ import annotations

from pathlib import Path


class CodeAnalyzer:
    IGNORE = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

    def scan_code(self, path: Path | str) -> str:
        todos = self.find_todos(path)
        imports = self.find_import_errors(path)
        deps = self.find_dependency_issues(path)
        readme = self.find_missing_readme_sections(path)
        return (
            "# Code Analysis\n\n"
            f"TODOs: {len(todos)}\n"
            f"Import concerns: {len(imports)}\n"
            f"Dependency notes: {len(deps)}\n"
            f"README gaps: {', '.join(readme) or 'none'}\n\n"
            "Suggestions are draft-only. Applying fixes requires approval."
        )

    def find_errors_from_logs(self, output: str) -> list[str]:
        markers = ["traceback", "modulenotfounderror", "syntaxerror", "npm err", "typeerror", "referenceerror"]
        lowered = output.lower()
        return [marker for marker in markers if marker in lowered]

    def explain_error_simple(self, error_text: str) -> str:
        if "modulenotfounderror" in error_text.lower():
            return "A Python package import is missing or the environment is not activated."
        if "syntaxerror" in error_text.lower():
            return "Python could not parse the code. Check the reported line for a typo."
        if "npm err" in error_text.lower():
            return "npm failed. Check package scripts, dependencies, and Node version."
        return "This error needs more context. Review the first traceback line and the command that caused it."

    def suggest_fix(self, error_text: str) -> str:
        explanation = self.explain_error_simple(error_text)
        return f"{explanation}\nSuggested next step: reproduce the error, inspect the exact file/line, then apply a focused fix with approval."

    def find_todos(self, path: Path | str) -> list[str]:
        root = Path(path)
        results = []
        for file in self._code_files(root):
            text = file.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(text.splitlines(), start=1):
                if "todo" in line.lower() or "fixme" in line.lower():
                    results.append(f"{file.relative_to(root)}:{i}: {line.strip()}")
        return results

    def find_missing_readme_sections(self, path: Path | str) -> list[str]:
        readme = Path(path) / "README.md"
        if not readme.exists():
            return ["README.md missing"]
        text = readme.read_text(encoding="utf-8", errors="replace").lower()
        return [section for section in ["setup", "run", "tests", "safety"] if section not in text]

    def find_dependency_issues(self, path: Path | str) -> list[str]:
        root = Path(path)
        issues = []
        if (root / "package.json").exists() and not (root / "node_modules").exists():
            issues.append("Node dependencies may not be installed.")
        if (root / "requirements.txt").exists() and not any((root / name).exists() for name in [".venv", "venv"]):
            issues.append("Python virtual environment not detected.")
        return issues

    def find_import_errors(self, path: Path | str) -> list[str]:
        root = Path(path)
        issues = []
        for file in self._code_files(root):
            text = file.read_text(encoding="utf-8", errors="replace")
            if "import " in text and "try:" not in text and "except ImportError" not in text:
                continue
        return issues

    def _code_files(self, root: Path):
        for file in root.rglob("*"):
            if file.is_file() and file.suffix.lower() in {".py", ".js", ".ts", ".tsx", ".jsx"}:
                if not any(part in self.IGNORE for part in file.parts):
                    yield file

