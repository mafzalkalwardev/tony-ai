from tony.core.workflow_memory import WorkflowMemory


def test_workflow_memory_saves_workflow_and_steps(tmp_path):
    memory = WorkflowMemory(tmp_path / "workflow.db")
    workflow_id = memory.create_workflow("demo", workspace=str(tmp_path))
    memory.add_step(workflow_id, 1, "mouse_click", {"x": 1, "y": 2})

    workflow = memory.get_workflow(workflow_id)

    assert workflow is not None
    assert workflow["name"] == "demo"
    assert len(workflow["steps"]) == 1


def test_workflow_memory_skips_secret_steps(tmp_path):
    memory = WorkflowMemory(tmp_path / "workflow.db")
    workflow_id = memory.create_workflow("demo")
    memory.add_step(workflow_id, 1, "key_press", {"value": "password123"})

    workflow = memory.get_workflow(workflow_id)

    assert workflow is not None
    assert workflow["steps"] == []
