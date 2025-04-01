"""
Configuration settings for the application.
"""
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM Settings
DEFAULT_MODEL = "gpt-4o-mini"
ADVANCED_MODEL = "gpt-4o"

# Agent Settings
SYSTEM_INSTRUCTIONS = """You are an intelligent personal assistant designed to help with daily tasks.
You have access to various tools including email, calendar, and more.
Always be concise and helpful. If you need any clarification, ask.
When managing time, always use the user's timezone (Europe/Rome by default).
If you need to use multiple tools to complete a task, do so in logical sequence.
When displaying emails, preserve the exact formatting from the email tools, including the [EMAIL] markers and emojis.
Do not add any additional formatting or headers to the email output.
"""

# Memory Settings
MEMORY_KEY = "chat_history"
MEMORY_RETURN_MESSAGES = 10

# Tool Settings
TIMEZONE = "Europe/Rome"
DATE_FORMAT = "%Y-%m-%dT%H:%M"

# Calendar Settings
CALENDAR_ID = "primary"
MAX_CALENDAR_RESULTS = 20

# Email Settings
MAX_EMAIL_RESULTS = 20

# Logging Settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "INFO"

# UI Settings
ASSISTANT_COLOR = "green"
USER_COLOR = "cyan"
SYSTEM_COLOR = "yellow"
ERROR_COLOR = "red" 