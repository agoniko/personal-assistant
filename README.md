# Personal Assistant with Agentic AI

A powerful personal assistant using OpenAI's latest agentic features to help with email management, calendar events, and more.

## Features

- **Multiple Specialized Agents**: Uses separate agents for calendar, email, and general tasks
- **Powerful Tool System**: Modular, well-structured tools for different capabilities
- **Persistent Memory**: Conversation history is saved between sessions
- **Streaming Responses**: Real-time responses with visible tool execution
- **Enhanced Date/Time Handling**: Advanced date parsing and timezone management

## Architecture

The system is built around several key components:

- **MultiAgentSystem**: Orchestrates multiple agents with different specializations
- **AgentManager**: Handles the core interaction with OpenAI's API and tool execution
- **ToolRegistry**: Manages the registration and execution of tools
- **ConversationMemory**: Maintains conversation history and context

### Tools

Tools are organized into categories:

- **Calendar Tools**: Add, modify, delete, and query calendar events
- **Email Tools**: Fetch and search emails by various criteria
- **Utility Tools**: Handle date/time operations, parsing, and more

## Setup

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Set up Google API credentials for Gmail and Calendar access (follow Google API documentation)
   - Place your `credentials.json` file in the `keys` directory

## Usage

The system includes a wrapper script (`run.py`) that checks prerequisites and handles various run modes:

```bash
python run.py
```

Run with multiple agents:

```bash
python run.py --multi
```

Run in debug mode:

```bash
python run.py --debug
```

Check prerequisites without running:

```bash
python run.py --check
```

## Tool Capabilities

### Calendar Tools
- Add events to Google Calendar
- Find events by time range or keywords
- Get today's events
- Modify or delete existing events

### Email Tools
- Fetch latest emails from inbox
- Search emails by keywords
- Get emails from specific date ranges

### Utility Tools
- Get current time in user's timezone
- Parse natural language date descriptions
- Calculate date differences
- Generate date ranges

## Customization

You can customize the system behavior in the `config.py` file, including:

- Default timezone
- LLM models to use
- System instructions
- Maximum results for queries

## Implementation Details

The system is designed with extensibility in mind:

1. **BaseTool Class**: All tools inherit from this class and use the `@register_tool` decorator
2. **Modular Tool Design**: Each tool is self-contained with clear inputs/outputs
3. **Memory System**: Structured conversation history with metadata support
4. **Streaming API Integration**: Real-time responses with tool execution visibility
5. **Error Handling**: Robust error handling at multiple levels

## Future Improvements

- Implement more specialized agents (finance, task management, etc.)
- Add more sophisticated routing logic between agents
- Enhance memory with vector embeddings for better context recall
- Add support for more Google services and third-party integrations

## License

MIT
