from __future__ import annotations

from tony.core.business_memory import BusinessMemory


class TaskPlanner:
    VALID_PRIORITIES = {"low", "medium", "high", "urgent"}

    def __init__(self, memory: BusinessMemory) -> None:
        self.memory = memory

    def create_task(self, title: str, description: str = "", priority: str = "medium") -> str:
        priority = priority if priority in self.VALID_PRIORITIES else "medium"
        task_id = self.memory.add_task(title, description, priority)
        return f"Task #{task_id} added: {title} ({priority})"

    def list_tasks(self) -> str:
        tasks = self.memory.list_tasks()
        if not tasks:
            return "No tasks saved yet."
        return "\n".join(f"#{task_id} [{priority}] {title} - {status}" for task_id, title, priority, status in tasks)

    def mark_task_done(self, task_id: int) -> str:
        self.memory.mark_task_done(task_id)
        return f"Task #{task_id} marked done."

    def update_task(self, task_id: int) -> str:
        return f"Task #{task_id} update is a V5 placeholder. Editing details will be added later."

    def create_daily_plan(self) -> str:
        tasks = self.memory.list_tasks(status="open")
        body = "Daily Plan\n\n1. Review urgent tasks\n2. Continue active project work\n3. Run tests before delivery\n4. Prepare client-safe update"
        if tasks:
            body += "\n\nOpen tasks:\n" + "\n".join(f"- #{t[0]} {t[1]} ({t[2]})" for t in tasks[:5])
        self.memory.save_daily_plan(body)
        return body

    def create_project_plan(self, project_name: str) -> str:
        return f"Project Plan: {project_name}\n\n1. Confirm scope\n2. Analyze repo\n3. Implement in small steps\n4. Test\n5. Prepare delivery report"

    def suggest_next_steps(self, project_summary: str) -> str:
        return f"Suggested next steps:\n- Verify current status\n- Run tests\n- Address highest-risk issue\n- Prepare delivery note\n\nContext:\n{project_summary[:1000]}"

