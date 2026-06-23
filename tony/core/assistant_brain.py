from __future__ import annotations

from tony.core.command_normalizer import CommandNormalizer
from tony.core.context_manager import ContextManager
from tony.core.intent_router import IntentRouter
from tony.core.reply_builder import ReplyBuilder
from tony.core.safety import SafetyLevel, SafetySystem
from tony.core.skill_registry import SkillRegistry
from tony.voice.wake_word import is_wake_phrase


class AssistantBrain:
    def __init__(
        self,
        agent=None,
        normalizer: CommandNormalizer | None = None,
        router: IntentRouter | None = None,
        safety: SafetySystem | None = None,
        registry: SkillRegistry | None = None,
        replies: ReplyBuilder | None = None,
        context: ContextManager | None = None,
    ) -> None:
        self.agent = agent
        self.normalizer = normalizer or CommandNormalizer()
        self.router = router or IntentRouter(self.normalizer, getattr(agent, "workspace", None))
        self.safety = safety or getattr(agent, "safety", None) or SafetySystem()
        self.registry = registry or SkillRegistry(agent)
        self.replies = replies or ReplyBuilder()
        self.context = context or ContextManager(getattr(agent, "memory", None))

    def handle_command(self, raw_text: str, source: str = "text") -> dict:
        raw_text = (raw_text or "").strip()
        self.context.save_input(raw_text, source)

        if not raw_text:
            reply = "I did not catch a command. Please try again."
            return self._response("clarification", raw_text, "", "unknown", "unknown", "", reply, "")

        if self._has_pending_approval() and self.safety.is_approved_text(raw_text):
            return self._execute_pending(source)
        if self._has_pending_approval() and self.safety.is_rejected_text(raw_text):
            self.context.clear_pending_approval()
            return self._response("cancelled", raw_text, "", "unknown", "unknown", "", self.replies.cancelled(), "")

        normalized = self.normalizer.normalize(raw_text)
        if not normalized and is_wake_phrase(raw_text):
            reply = self.replies.listening()
            return self._response("completed", raw_text, "", "wake_phrase", "voice", "SAFE", reply, reply)
        if not normalized:
            reply = "I heard you, but I did not catch a command. Please try again."
            return self._response("clarification", raw_text, "", "unknown", "unknown", "", reply, "")
        route = self.router.route(normalized)
        normalized = route.get("normalized_text") or normalized

        if route.get("needs_clarification"):
            reply = self.replies.clarification(route.get("clarifying_question", "What should I use?"))
            return self._response("clarification", raw_text, normalized, route["intent"], route["skill"], "", reply, "")

        safety_text = f"{normalized} {raw_text}".strip()
        decision = self.safety.classify(safety_text, route.get("intent"))
        safety_level = decision.level.value

        if source in {"voice", "wake"} and self.agent:
            try:
                self.agent.memory.log_voice_transcript(raw_text, safety_level, route.get("intent", "unknown"), decision.level == SafetyLevel.SAFE)
            except Exception:
                pass

        if decision.level == SafetyLevel.BLOCKED:
            self.context.set_mode("blocked")
            self.context.save_error(route["intent"], decision.reason)
            reply = self.replies.blocked(decision.reason)
            self._log_task(raw_text, route, "blocked", safety_level, reply, source, raw_text if source in {"voice", "wake"} else None)
            return self._response("blocked", raw_text, normalized, route["intent"], route["skill"], safety_level, reply, "")

        if decision.level == SafetyLevel.NEEDS_APPROVAL:
            pending = {
                "raw_text": raw_text,
                "normalized_text": normalized,
                "route": route,
                "source": source,
                "safety": safety_level,
            }
            self.context.set_pending_approval(pending)
            reply = self.replies.approval(normalized or raw_text)
            self._log_task(raw_text, route, "waiting_for_approval", safety_level, reply, source, raw_text if source in {"voice", "wake"} else None)
            return self._response("waiting_for_approval", raw_text, normalized, route["intent"], route["skill"], safety_level, reply, "")

        return self._execute(route, raw_text, normalized, source, safety_level, approved=False)

    def _execute_pending(self, approval_source: str) -> dict:
        pending = self.context.clear_pending_approval() or {}
        route = pending.get("route") or {}
        raw_text = pending.get("raw_text", "")
        normalized = pending.get("normalized_text", "")
        source = pending.get("source", approval_source)
        safety_level = pending.get("safety", SafetyLevel.NEEDS_APPROVAL.value)
        return self._execute(route, raw_text, normalized, source, safety_level, approved=True)

    def _execute(self, route: dict, raw_text: str, normalized: str, source: str, safety_level: str, approved: bool) -> dict:
        if not self.registry.is_ready(route):
            reply = self.replies.not_ready()
            return self._response("error", raw_text, normalized, route.get("intent", "unknown"), route.get("skill", "unknown"), safety_level, reply, reply)

        try:
            self.context.set_mode("working")
            result = self.registry.execute(route, normalized, source=source, raw_text=raw_text, approved=approved)
            self.context.set_mode("replying")
            self.context.save_result(route["intent"], result)
            reply = self.replies.completed(result)
            self._log_task(raw_text, route, "completed", safety_level, result, source, raw_text if source in {"voice", "wake"} else None)
            return self._response("completed", raw_text, normalized, route["intent"], route["skill"], safety_level, reply, result)
        except Exception as exc:
            error = str(exc)
            self.context.save_error(route.get("intent", "unknown"), error)
            reply = self.replies.error(error)
            return self._response("error", raw_text, normalized, route.get("intent", "unknown"), route.get("skill", "unknown"), safety_level, reply, error)
        finally:
            if self.context.current_mode != "waiting_for_approval":
                self.context.set_mode("idle")

    def _response(
        self,
        status: str,
        raw_text: str,
        normalized_text: str,
        intent: str,
        skill: str,
        safety: str,
        reply: str,
        result: str,
    ) -> dict:
        return {
            "status": status,
            "raw_text": raw_text,
            "normalized_text": normalized_text,
            "intent": intent,
            "skill": skill,
            "safety": safety,
            "reply": reply,
            "result": result,
            "should_speak": status in {"completed", "blocked", "waiting_for_approval", "clarification", "error", "cancelled"},
        }

    def _has_pending_approval(self) -> bool:
        return self.context.pending_approval is not None

    def _log_task(self, raw_text: str, route: dict, status: str, safety: str, result: str, source: str, transcript: str | None) -> None:
        if not self.agent:
            return
        try:
            self.agent.memory.log_task(
                raw_text,
                route.get("intent", "unknown"),
                route.get("action", ""),
                result,
                command_source=source,
                safety_level=safety,
                voice_transcript=transcript,
            )
            self.agent.memory.log_task_output(raw_text, status, output=result if status != "blocked" else "", error=result if status == "blocked" else "")
        except Exception:
            pass
