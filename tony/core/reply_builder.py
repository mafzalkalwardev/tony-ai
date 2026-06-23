from __future__ import annotations


class ReplyBuilder:
    user_name = "Muhammad Afzal"

    def online(self) -> str:
        return f"Welcome back, {self.user_name}. Tony is online."

    def listening(self) -> str:
        return f"Yes, {self.user_name}. I'm listening."

    def transcript(self, text: str) -> str:
        return f"I heard you say: {text}."

    def completed(self, result: str = "") -> str:
        if result:
            return f"Done, {self.user_name}. Here is what I found.\n\n{result}"
        return f"Done, {self.user_name}."

    def approval(self, command: str) -> str:
        return f"This action needs your approval before I continue: {command}. Type yes to approve or no to cancel."

    def blocked(self, reason: str) -> str:
        return f"I blocked that because it looks dangerous: {reason}."

    def clarification(self, question: str) -> str:
        return f"I can do that, but I need one detail first: {question}"

    def error(self, error: str) -> str:
        return f"I ran into a problem, {self.user_name}. Here is the error in simple words: {error}"

    def voice_missing(self) -> str:
        return "Voice is not ready yet. Text commands still work."

    def cancelled(self) -> str:
        return "Action cancelled."

    def not_ready(self) -> str:
        return f"That skill is not ready yet, {self.user_name}."
