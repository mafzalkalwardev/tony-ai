from tony.tools.business_tool import BusinessTool


def test_client_message_generation_returns_draft():
    draft = BusinessTool().generate_client_message("project is ready")
    assert "Draft client message" in draft
    assert "project is ready" in draft


def test_delivery_note_generation_works():
    note = BusinessTool().generate_delivery_note("Website completed")
    assert "Delivery Note" in note
    assert "Website completed" in note


def test_no_external_send_function_auto_runs():
    tool = BusinessTool()
    assert not hasattr(tool, "send_message")

