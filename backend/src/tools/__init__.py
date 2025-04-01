"""
Tools package initialization.
"""

# Make tools available when importing the package
from src.tools.base import BaseTool, ToolRegistry, register_tool
from src.tools.calendar_tools import (
    AddEventTool,
    GetEventsByTimeTool,
    GetEventsByQueryTool,
    DeleteEventTool,
    ModifyEventTool,
    GetTodaysEventsTool,
)
from src.tools.email_tools import (
    FetchLatestEmailsTool,
    SearchEmailsTool,
    FetchEmailsByDateTool,
)
from src.tools.utility_tools import (
    GetCurrentTimeTool,
    GetDateInfoTool,
    CalculateDateDifferenceTool,
    GenerateDateRangeTool,
    ParseDateTool,
    GetYesterdayDateTool,
)

# Initialize all tools
def initialize_tools():
    """Initialize all tools."""
    # This function doesn't need to do anything explicit since tools are registered
    # using decorators, but can be used to ensure all tools are imported
    pass

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "register_tool",
    "AddEventTool",
    "GetEventsByTimeTool",
    "GetEventsByQueryTool",
    "DeleteEventTool",
    "ModifyEventTool",
    "GetTodaysEventsTool",
    "FetchLatestEmailsTool",
    "SearchEmailsTool",
    "FetchEmailsByDateTool",
    "GetCurrentTimeTool",
    "GetDateInfoTool",
    "CalculateDateDifferenceTool",
    "GenerateDateRangeTool",
    "ParseDateTool",
    "GetYesterdayDateTool",
] 