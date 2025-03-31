"""
Base tool class and tool registration system.
"""
from typing import Dict, Any, List, Optional, Callable, Type, ClassVar
from pydantic import BaseModel, Field, create_model
import inspect
from abc import ABC, abstractmethod
import json
import sys
import os

# Add parent directory to path if running as a script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class BaseTool(ABC):
    """Base class for all tools."""
    
    name: ClassVar[str]
    description: ClassVar[str]
    
    @classmethod
    def get_name(cls) -> str:
        """Get the name of the tool."""
        return cls.name
    
    @classmethod
    def get_description(cls) -> str:
        """Get the description of the tool."""
        return cls.description
    
    @classmethod
    def create_arguments_model(cls) -> Type[BaseModel]:
        """Create a Pydantic model for the tool's arguments based on the execute method."""
        method = cls.execute
        signature = inspect.signature(method)
        
        # Skip the first parameter (self)
        parameters = list(signature.parameters.values())[1:]
        
        fields = {}
        for param in parameters:
            # Set field as required if no default value
            if param.default is inspect.Parameter.empty:
                fields[param.name] = (param.annotation, ...)
            else:
                fields[param.name] = (param.annotation, Field(default=param.default))
        
        # Create and return the model dynamically
        return create_model(f"{cls.__name__}Arguments", **fields)
    
    @classmethod
    def get_openai_schema(cls) -> Dict[str, Any]:
        """Convert the tool to OpenAI's function schema format."""
        model = cls.create_arguments_model()
        schema = model.model_json_schema()
        
        return {
            "type": "function",
            "function": {
                "name": cls.get_name(),
                "description": cls.get_description(),
                "parameters": schema
            }
        }
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool with the given arguments."""
        pass

class ToolRegistry:
    """Registry for all available tools."""
    
    _tools: Dict[str, Type[BaseTool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """Register a tool class."""
        cls._tools[tool_class.get_name()] = tool_class
        return tool_class
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[Type[BaseTool]]:
        """Get a tool class by name."""
        return cls._tools.get(name)
    
    @classmethod
    def get_all_tools(cls) -> List[Type[BaseTool]]:
        """Get all registered tool classes."""
        return list(cls._tools.values())
    
    @classmethod
    def get_openai_tools_schema(cls) -> List[Dict[str, Any]]:
        """Get the OpenAI tools schema for all registered tools."""
        return [tool.get_openai_schema() for tool in cls.get_all_tools()]
    
    @classmethod
    def execute_tool(cls, name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool by name with the given arguments."""
        tool_class = cls.get_tool(name)
        if not tool_class:
            raise ValueError(f"Tool '{name}' not found")
        
        tool_instance = tool_class()
        return tool_instance.execute(**args)

def register_tool(cls: Type[BaseTool]) -> Type[BaseTool]:
    """Decorator to register a tool class."""
    return ToolRegistry.register(cls) 