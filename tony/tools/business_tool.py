from __future__ import annotations


class BusinessTool:
    DEFAULT_STYLE = "professional, simple, confident, clear"

    def generate_client_message(self, context: str, tone: str = DEFAULT_STYLE) -> str:
        return f"Draft client message ({tone}):\n\nHi,\n\nHere is a quick update: {context or 'the work is progressing well.'}\n\nI will keep you posted on the next milestone.\n\nBest regards,\nMuhammad Afzal"

    def generate_delivery_note(self, project_summary: str) -> str:
        return f"Delivery Note\n\nSummary:\n{project_summary}\n\nDelivered items:\n- Completed requested work\n- Verified core behavior\n\nPlease review and share feedback."

    def generate_progress_update(self, task_summary: str) -> str:
        return f"Progress Update\n\nCompleted: {task_summary}\nNext: testing, polish, and delivery review."

    def generate_invoice_note(self, details: str) -> str:
        return f"Invoice note draft only:\n\nWork completed: {details}\nPayment instructions should be added manually after review."

    def generate_project_proposal_outline(self, details: str) -> str:
        return f"Proposal Outline\n\n1. Goal\n{details}\n\n2. Scope\n3. Timeline\n4. Deliverables\n5. Assumptions\n6. Next steps"

    def generate_meeting_summary(self, notes: str) -> str:
        return f"Meeting Summary\n\nKey notes:\n{notes}\n\nAction items:\n- Confirm scope\n- Assign next tasks\n- Set delivery date"

    def generate_follow_up_message(self, context: str) -> str:
        return f"Follow-up draft:\n\nHi,\n\nJust following up on {context or 'our previous discussion'}. Please let me know your thoughts when convenient.\n\nBest,\nMuhammad Afzal"

    def generate_apology_or_delay_message(self, context: str) -> str:
        return f"Delay message draft:\n\nHi,\n\nI wanted to update you transparently. {context or 'The work needs a little more time to finish properly.'} I am working on it and will share the next update soon.\n\nThank you for your patience."

