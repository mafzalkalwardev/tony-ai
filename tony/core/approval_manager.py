from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PendingApproval:
    command: str
    intent: str
    reason: str
    source: str = "text"


class ApprovalManager:
    def __init__(self) -> None:
        self.pending: PendingApproval | None = None

    def request(self, command: str, intent: str, reason: str, source: str = "text") -> PendingApproval:
        self.pending = PendingApproval(command, intent, reason, source)
        return self.pending

    def clear(self) -> None:
        self.pending = None

    def has_pending(self) -> bool:
        return self.pending is not None

