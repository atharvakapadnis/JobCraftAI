import inspect
import typing
import logging
from typing import Callable, Dict, Any, List, Optional, Type, Union, get_type_hints
from pydantic import BaseModel
from functools import wraps

class ToolMetadata(BaseModel):
    """Metadata for an MCP tool."""
    name: str
    description: str = ""
    function: Callable
    parameters: Dict[str, Any] = {}
    return_type: Type = Any
    return_description: str = ""

class FastMCP:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.tools: Dict[str, ToolMetadata] = {}
        self.logger = logging.getLogger("fastmcp")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info(f"MCP server initialized for project: {project_name}")

    def tool(self, name: str = None, description: str = None):
        """
        Decorator to register a function as an MCP tool.

        Args:
            name: Optional custom name for the tool. If not provided, uses the function name.
            description: Optional description for the tool. If not provided, uses the function docstring.
        """

        def decorator(func):
            # Get function signature for parameter info
            sig = inspect.signature(func)
            func_name = name or func.__name__
            func_desc = description or inspect.getdoc(func) or ""

            # Extract parameter information from type hints
            type_hints = get_type_hints(func)
            parameters = {}

            for param_name, param in sig.parameters.items():
                param_type = type_hints.get(param_name, Any)
                default = (
                    param.default
                    if param.default is not inspect.Parameter.empty
                    else None
                )
                is_required = param.default is inspect.Parameter.empty

                # Handle different parameter types
                parameters[param_name] = {
                    "type": param_type,
                    "required": is_required,
                    "default": default,
                    "description": "",  # We could extract this from docstring in a more advanced implementation
                }

            # Extract return type
            return_type = type_hints.get("return", Any)

            # Register the tool
            self.tools[func_name] = ToolMetadata(
                name=func_name,
                description=func_desc,
                function=func,
                parameters=parameters,
                return_type=return_type,
            )

            self.logger.info(f"Registered tool: {func_name}")

            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.debug(f"Executing tool: {func_name}")
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    self.logger.error(f"Error executing tool {func_name}: {str(e)}")
                    raise

            return wrapper

        return decorator

    def list_tools(self) -> List[str]:
        """Return a list of all registered tool names."""
        return list(self.tools.keys())

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool."""
        if tool_name not in self.tools:
            return None

        tool = self.tools[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                name: {
                    "type": str(param["type"]),
                    "required": param["required"],
                    "default": param["default"],
                    "description": param["description"],
                }
                for name, param in tool.parameters.items()
            },
            "return_type": str(tool.return_type),
        }

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name with the provided parameters."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool = self.tools[tool_name]
        return tool.function(**kwargs)