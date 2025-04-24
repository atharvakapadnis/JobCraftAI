"""
MCP Client implementation for JobCraftAI

This module implements a Model Context Protocol (MCP) client that can connect
to MCP servers and invoke tools.
"""

import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator

from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClient:
    """
    MCP Client implementation for JobCraftAI
    """
    
    def __init__(self, server_url: str):
        """
        Initialize the MCP client
        
        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url
        self.tools = {}
        self.session = None
    
    async def connect(self):
        """
        Connect to the MCP server and discover available tools
        """
        self.session = aiohttp.ClientSession()
        await self.discover_tools()
    
    async def close(self):
        """
        Close the connection to the MCP server
        """
        if self.session:
            await self.session.close()
            self.session = None
    
    async def discover_tools(self):
        """
        Discover available tools from the MCP server
        """
        if not self.session:
            await self.connect()
        
        try:
            request = {
                "type": "discover"
            }
            
            async with self.session.post(self.server_url, json=request) as response:
                if response.status != 200:
                    raise Exception(f"Error discovering tools: {response.status}")
                
                response_data = await response.json()
                if response_data.get("type") != "discover_response":
                    raise Exception(f"Unexpected response type: {response_data.get('type')}")
                
                tools = response_data.get("tools", [])
                self.tools = {tool["name"]: tool for tool in tools}
                
                logger.info(f"Discovered {len(self.tools)} tools from MCP server")
                return list(self.tools.values())
        except Exception as e:
            logger.error(f"Error discovering tools: {str(e)}")
            raise
    
    async def invoke_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to invoke
            params: Tool parameters
            
        Returns:
            Tool result
        """
        if not self.session:
            await self.connect()
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        try:
            request = {
                "type": "invoke",
                "tool": tool_name,
                "params": params
            }
            
            async with self.session.post(self.server_url, json=request) as response:
                if response.status != 200:
                    raise Exception(f"Error invoking tool: {response.status}")
                
                response_data = await response.json()
                if response_data.get("type") == "error":
                    raise Exception(f"Tool invocation error: {response_data.get('error', {}).get('message')}")
                
                if response_data.get("type") != "invoke_response":
                    raise Exception(f"Unexpected response type: {response_data.get('type')}")
                
                return response_data.get("result", {})
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {str(e)}")
            raise
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """
        Get the schema for a tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool schema
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        return self.tools[tool_name]