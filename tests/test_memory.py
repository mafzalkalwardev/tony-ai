from tony.core.memory import MemoryStore


def test_memory_store_creates_database_and_logs_task(tmp_path):
    db_path = tmp_path / "memory.db"
    memory = MemoryStore(db_path)

    memory.log_task("repo status", "git_status", "git status", "ok", safety_level="SAFE")
    memory.log_task_output("repo status", "completed", output="ok")

    assert db_path.exists()
