"""
MCP Protocol definitions for JobCraftAI

This module defines the MCP protocol structures and interfaces.
"""

from typing import Dict, Any, List, Optional, Protocol, runtime_checkable

@runtime_checkable
class MCPServerProtocol(Protocol):
    """
    Protocol for MCP servers
    """
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP request
        
        Args:
            request: MCP request object
            
        Returns:
            MCP response object
        """
        ...
    
    async def handle_discover(self) -> Dict[str, Any]:
        """
        Handle a discover request
        
        Returns:
            MCP discover response
        """
        ...
    
    async def handle_invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an invoke request
        
        Args:
            request: MCP invoke request
            
        Returns:
            MCP invoke response
        """
        ...

@runtime_checkable
class MCPClientProtocol(Protocol):
    """
    Protocol for MCP clients
    """
    
    async def connect(self):
        """
        Connect to the MCP server
        """
        ...
    
    async def close(self):
        """
        Close the connection to the MCP server
        """
        ...
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover available tools from the MCP server
        
        Returns:
            List of available tools
        """
        ...
    
    async def invoke_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to invoke
            params: Tool parameters
            
        Returns:
            Tool result
        """
        ...
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        Get the schema for a tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool schema
        """
        ...

# MCP request types
class MCPRequestType:
    DISCOVER = "discover"
    INVOKE = "invoke"

# MCP response types
class MCPResponseType:
    DISCOVER_RESPONSE = "discover_response"
    INVOKE_RESPONSE = "invoke_response"
    ERROR = "error"