from app.agent.tools import TOOL_DEFINITIONS


def test_tool_definitions_valid():
    """All tool definitions must have required fields."""
    for tool in TOOL_DEFINITIONS:
        assert tool["type"] == "function"
        function = tool["function"]
        assert "name" in function
        assert "description" in function
        assert "parameters" in function
        parameters = function["parameters"]
        assert parameters["type"] == "object"
        assert "properties" in parameters


def test_tool_names_unique():
    names = [tool["function"]["name"] for tool in TOOL_DEFINITIONS]
    assert len(names) == len(set(names))


def test_expected_tools_present():
    names = {tool["function"]["name"] for tool in TOOL_DEFINITIONS}
    expected = {
        "list_courses",
        "add_course",
        "delete_course",
        "get_free_slots",
        "create_study_plan",
        "list_tasks",
        "update_task",
        "complete_task",
        "set_reminder",
        "list_reminders",
        "ask_user",
    }
    assert expected.issubset(names)