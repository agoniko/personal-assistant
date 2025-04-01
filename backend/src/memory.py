"""
Memory system for storing conversation history and other contextual information.
"""
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import os
from pydantic import BaseModel, Field
from src.config import MEMORY_KEY, MEMORY_RETURN_MESSAGES

class Message(BaseModel):
    """Represents a single message in the conversation."""
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationMemory:
    """Manages conversation history and provides context for the agents."""
    
    def __init__(self, 
                 memory_file: Optional[str] = None, 
                 max_tokens: int = 8000):
        """
        Initialize the conversation memory system.
        
        Args:
            memory_file: Optional path to save/load memory from.
            max_tokens: Maximum number of tokens to maintain in memory.
        """
        self.messages: List[Message] = []
        self.memory_file = memory_file
        self.max_tokens = max_tokens
        self._load_memory()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: The role of the message sender (user, assistant, system, or tool).
            content: The content of the message.
            metadata: Optional metadata for the message.
        """
        metadata = metadata or {}
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self._save_memory()
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """
        Get the conversation history.
        
        Args:
            limit: Optional limit on the number of messages to return.
            
        Returns:
            List of messages.
        """
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages = []
        self._save_memory()
    
    def as_openai_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Convert memory to OpenAI message format.
        
        Args:
            limit: Optional limit on the number of messages to return.
            
        Returns:
            List of dictionaries in OpenAI message format.
        """
        messages = self.get_messages(limit)
        result = []
        
        for message in messages:
            msg_dict = {"role": message.role, "content": message.content}
            
            # Add tool_call_id and name for tool messages
            if message.role == "tool" and "tool_call_id" in message.metadata:
                msg_dict["tool_call_id"] = message.metadata["tool_call_id"]
                msg_dict["name"] = message.metadata.get("name", "")
            
            # Add tool calls for assistant messages if present
            if message.role == "assistant" and "tool_calls" in message.metadata:
                # Add type field to each tool call
                tool_calls = message.metadata["tool_calls"]
                for tool_call in tool_calls:
                    if "type" not in tool_call:
                        tool_call["type"] = "function"
                        
                msg_dict["tool_calls"] = tool_calls
            
            result.append(msg_dict)
        
        return result
    
    def _save_memory(self) -> None:
        """Save memory to file if a memory file is specified."""
        if not self.memory_file:
            return
        
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        with open(self.memory_file, "w") as f:
            json.dump([m.model_dump() for m in self.messages], f, indent=2)
    
    def _load_memory(self) -> None:
        """Load memory from file if it exists."""
        if not self.memory_file or not os.path.exists(self.memory_file):
            return
        
        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
                self.messages = [Message(**m) for m in data]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading memory: {e}")
            self.messages = [] 