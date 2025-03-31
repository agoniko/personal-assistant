"""
Agent manager for orchestrating multiple agents with different capabilities.
"""
from typing import List, Dict, Any, Optional, Union, Generator
import json
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
import time
from colorama import Fore, Style, init
from pydantic import BaseModel, Field

from src.memory import ConversationMemory
from src.tools.base import ToolRegistry
import src.config as config

# Initialize colorama
init()

class ToolCallResult(BaseModel):
    """Model for tool call results."""
    tool_name: str
    tool_call_id: str
    result: str

class AgentManager:
    """
    Manages multiple agents with different capabilities and handles their interactions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent manager.
        
        Args:
            api_key: OpenAI API key (defaults to the one in config).
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API Key is required")
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize conversation memory
        self.memory = ConversationMemory(
            memory_file="data/conversation_history.json"
        )
        
        # Add system message to memory if it's empty
        if not self.memory.get_messages():
            self.memory.add_message("system", config.SYSTEM_INSTRUCTIONS)
    
    def chat(self, user_input: str) -> str:
        """
        Process a user input and generate a response.
        
        Args:
            user_input: The user's input message.
            
        Returns:
            The agent's response as a string.
        """
        # Add user message to memory
        self.memory.add_message("user", user_input)
        
        # Get messages from memory
        messages = self.memory.as_openai_messages()
        
        # Get available tools
        tools = ToolRegistry.get_openai_tools_schema()
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=config.DEFAULT_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        # Get the response message
        response_message = response.choices[0].message
        
        # Process tool calls if any
        if response_message.tool_calls:
            # Save the assistant's message with tool calls
            tool_calls_metadata = {
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in response_message.tool_calls
                ]
            }
            self.memory.add_message("assistant", response_message.content or "", tool_calls_metadata)
            
            # Execute each tool call
            tool_results = []
            for tool_call in response_message.tool_calls:
                result = self._execute_tool_call(tool_call)
                tool_results.append(result)
                
                # Add tool result to memory
                self.memory.add_message(
                    "tool",
                    result.result,
                    {
                        "tool_call_id": result.tool_call_id,
                        "name": result.tool_name
                    }
                )
            
            # Get messages from memory again with tool results
            messages = self.memory.as_openai_messages()
            
            # Call the OpenAI API again with tool results
            second_response = self.client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=messages
            )
            
            # Get the final response
            final_response = second_response.choices[0].message.content
            
            # Add the final response to memory
            self.memory.add_message("assistant", final_response)
            
            return final_response
        else:
            # No tool calls, just return the response
            self.memory.add_message("assistant", response_message.content)
            return response_message.content
    
    def stream_chat(self, user_input: str) -> Generator[Dict[str, Any], None, None]:
        """
        Process a user input and stream the response.
        
        Args:
            user_input: The user's input message.
            
        Yields:
            Dictionaries containing the response chunk data.
        """
        # Add user message to memory
        self.memory.add_message("user", user_input)
        
        # Get messages from memory
        messages = self.memory.as_openai_messages()
        
        # Get available tools
        tools = ToolRegistry.get_openai_tools_schema()
        
        # Call the OpenAI API with streaming
        stream = self.client.chat.completions.create(
            model=config.DEFAULT_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=True
        )
        
        # Variables to track streaming state
        collected_chunks = []
        collected_messages = []
        collected_tool_calls = {}
        current_tool_call = None
        
        # Process the streaming response
        for chunk in stream:
            collected_chunks.append(chunk)
            
            # Check for content in the chunk
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                collected_messages.append(content)
                yield {"type": "content", "content": content}
            
            # Check for tool calls in the chunk
            if chunk.choices[0].delta.tool_calls:
                for tool_call_delta in chunk.choices[0].delta.tool_calls:
                    index = tool_call_delta.index
                    
                    # Initialize a new tool call if needed
                    if index not in collected_tool_calls:
                        collected_tool_calls[index] = {
                            "id": "",
                            "type": "function",
                            "function": {"name": "", "arguments": ""}
                        }
                    
                    # Update the tool call with new information
                    if tool_call_delta.id:
                        collected_tool_calls[index]["id"] = tool_call_delta.id
                    
                    if tool_call_delta.function:
                        if tool_call_delta.function.name:
                            collected_tool_calls[index]["function"]["name"] += tool_call_delta.function.name
                        if tool_call_delta.function.arguments:
                            collected_tool_calls[index]["function"]["arguments"] += tool_call_delta.function.arguments
        
        # Check if we collected any tool calls
        if collected_tool_calls:
            # Add the assistant's message with tool calls to memory
            assistant_content = "".join(collected_messages) if collected_messages else None
            
            # Convert to the format expected by memory
            tool_calls_metadata = {
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    } for tc in collected_tool_calls.values()
                ]
            }
            
            self.memory.add_message("assistant", assistant_content or "", tool_calls_metadata)
            
            # Execute each tool call and yield results
            for index, tool_call in collected_tool_calls.items():
                try:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    # Yield that we're executing a tool
                    yield {"type": "tool_start", "name": function_name}
                    
                    # Execute the tool
                    result = ToolRegistry.execute_tool(function_name, function_args)
                    
                    # Add tool result to memory
                    self.memory.add_message(
                        "tool",
                        result,
                        {
                            "tool_call_id": tool_call["id"],
                            "name": function_name
                        }
                    )
                    
                    # Yield the tool result
                    yield {"type": "tool_result", "name": function_name, "result": result}
                except Exception as e:
                    error_message = f"Error executing tool {function_name}: {str(e)}"
                    yield {"type": "tool_error", "name": function_name, "error": error_message}
                    
                    # Add error to memory
                    self.memory.add_message(
                        "tool",
                        error_message,
                        {
                            "tool_call_id": tool_call["id"],
                            "name": function_name
                        }
                    )
            
            # Get messages from memory again with tool results
            messages = self.memory.as_openai_messages()
            
            # Call the OpenAI API again with tool results
            yield {"type": "second_response_start"}
            
            second_stream = self.client.chat.completions.create(
                model=config.DEFAULT_MODEL,
                messages=messages,
                stream=True
            )
            
            # Collect the final response
            final_response_chunks = []
            
            for chunk in second_stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    final_response_chunks.append(content)
                    yield {"type": "content", "content": content}
            
            # Add the final response to memory
            final_response = "".join(final_response_chunks)
            self.memory.add_message("assistant", final_response)
        else:
            # No tool calls, just add the response to memory
            assistant_content = "".join(collected_messages)
            self.memory.add_message("assistant", assistant_content)
    
    def _execute_tool_call(self, tool_call: Any) -> ToolCallResult:
        """
        Execute a tool call and return the result.
        
        Args:
            tool_call: The tool call object from OpenAI.
            
        Returns:
            A ToolCallResult object with the result of the tool call.
        """
        try:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            result = ToolRegistry.execute_tool(function_name, function_args)
            
            return ToolCallResult(
                tool_name=function_name,
                tool_call_id=tool_call.id,
                result=result
            )
        except Exception as e:
            error_message = f"Error executing tool {tool_call.function.name}: {str(e)}"
            
            return ToolCallResult(
                tool_name=tool_call.function.name,
                tool_call_id=tool_call.id,
                result=error_message
            )
    
    def clear_memory(self) -> None:
        """Clear the conversation memory."""
        self.memory.clear()
        # Add system message back
        self.memory.add_message("system", config.SYSTEM_INSTRUCTIONS)

class MultiAgentSystem:
    """
    A system that uses multiple specialized agents for different tasks.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the multi-agent system.
        
        Args:
            api_key: OpenAI API key (defaults to the one in config).
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API Key is required")
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize the main agent
        self.primary_agent = AgentManager(api_key)
        
        # Initialize memory for system coordination
        self.system_memory = ConversationMemory(
            memory_file="data/system_memory.json"
        )
        
        # Define agent roles
        self.agent_roles = {
            "router": "You analyze user requests and determine which specialized agent should handle them.",
            "calendar": "You specialize in managing calendar events and scheduling.",
            "email": "You specialize in reading and analyzing emails.",
            "general": "You handle general inquiries and tasks that don't fit other specialized roles."
        }
    
    def chat(self, user_input: str) -> str:
        """
        Determine which agent should handle the request and route it accordingly.
        
        Args:
            user_input: The user's input message.
            
        Returns:
            The response from the appropriate agent.
        """
        # For simplicity, we'll use the primary agent for now
        # In a full implementation, we would first use a router agent to determine
        # which specialized agent should handle the request
        return self.primary_agent.chat(user_input)
    
    def stream_chat(self, user_input: str) -> Generator[str, None, None]:
        """
        Stream the response from the appropriate agent.
        
        Args:
            user_input: The user's input message.
            
        Yields:
            Chunks of the response as they become available.
        """
        # For now, we'll just forward to the primary agent's stream_chat
        for chunk in self.primary_agent.stream_chat(user_input):
            # Convert the chunk dictionary to a formatted string based on chunk type
            if chunk["type"] == "content":
                yield chunk["content"]
            elif chunk["type"] == "tool_start":
                yield f"\n[{Fore.YELLOW}TOOL{Style.RESET_ALL}] Running {chunk['name']}...\n"
            elif chunk["type"] == "tool_result":
                result = chunk["result"].replace("\n", "\n  ")  # Indent result
                yield f"  {result}\n"
            elif chunk["type"] == "tool_error":
                yield f"\n[{Fore.RED}ERROR{Style.RESET_ALL}] {chunk['error']}\n"
            elif chunk["type"] == "second_response_start":
                yield f"\n[{Fore.GREEN}ASSISTANT{Style.RESET_ALL}] "
    
    def _route_request(self, user_input: str) -> str:
        """
        Determine which agent should handle the request.
        
        Args:
            user_input: The user's input message.
            
        Returns:
            The name of the agent that should handle the request.
        """
        # In a full implementation, we would use the router agent to analyze the request
        # and determine which specialized agent should handle it
        # For simplicity, we'll return "general" for now
        return "general"