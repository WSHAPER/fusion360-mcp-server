#!/usr/bin/env python3
"""
Fusion 360 MCP Server

This module implements a Model Context Protocol (MCP) server for Fusion 360 API integration.
It follows the JSON-RPC 2.0 specification as required by Claude Desktop.
"""

import json
import sys
import logging
from typing import Dict, Any, List, Optional

# Import script generator
from script_generator import (
    generate_script,
    generate_multi_tool_script,
    TOOL_REGISTRY,
    TOOLS_BY_NAME,
)

# Set up logging to stderr for debugging
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)

class MCPServer:
    """Model Context Protocol server implementation."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.capabilities = {
            "tools": {}
        }
    
    def handle_message(self, message: str) -> Optional[str]:
        """
        Handle an incoming JSON-RPC 2.0 message.
        
        Args:
            message: The raw JSON message string.
            
        Returns:
            The response JSON string, or None for notifications.
        """
        try:
            request = json.loads(message.strip())
        except json.JSONDecodeError as e:
            return self._create_error_response(
                None, -32700, f"Parse error: {e}"
            )
        
        # Extract request components
        jsonrpc = request.get("jsonrpc")
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Validate JSON-RPC 2.0 format
        if jsonrpc != "2.0":
            return self._create_error_response(
                request_id, -32600, "Invalid Request: jsonrpc must be '2.0'"
            )
        
        if not method:
            return self._create_error_response(
                request_id, -32600, "Invalid Request: missing method"
            )
        
        # Handle notifications (no id field)
        if "id" not in request:
            self._handle_notification(method, params)
            return None
        
        # Handle requests
        try:
            result = self._handle_request(method, params)
            return self._create_success_response(request_id, result)
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}")
            return self._create_error_response(
                request_id, -32603, f"Internal error: {e}"
            )
    
    def _handle_notification(self, method: str, params: Dict[str, Any]):
        """Handle a notification (no response expected)."""
        logger.info(f"Received notification: {method}")
    
    def _handle_request(self, method: str, params: Dict[str, Any]) -> Any:
        """
        Handle a request and return the result.
        
        Args:
            method: The method name.
            params: The method parameters.
            
        Returns:
            The result data.
        """
        if method == "initialize":
            return self._handle_initialize(params)
        elif method == "tools/list":
            return self._handle_tools_list()
        elif method == "tools/call":
            return self._handle_tools_call(params)
        else:
            raise ValueError(f"Method not found: {method}")
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the initialize request.
        
        Args:
            params: The initialization parameters.
            
        Returns:
            The server capabilities.
        """
        logger.info("Initializing MCP server")
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "fusion360-mcp-server",
                "version": "0.1.0"
            }
        }
    
    def _handle_tools_list(self) -> Dict[str, Any]:
        """
        Handle the tools/list request.
        
        Returns:
            The list of available tools.
        """
        tools = []
        for tool in TOOL_REGISTRY:
            # Convert tool parameters to JSON Schema format
            properties = {}
            required = []
            
            for param_name, param_info in tool["parameters"].items():
                prop = {
                    "type": param_info["type"],
                    "description": param_info["description"]
                }
                
                # Handle array types
                if param_info["type"] == "array" and "items" in param_info:
                    prop["items"] = param_info["items"]
                
                properties[param_name] = prop
                
                # Add to required if no default value
                if "default" not in param_info:
                    required.append(param_name)
            
            tools.append({
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            })
        
        return {"tools": tools}
    
    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the tools/call request.
        
        Args:
            params: The tool call parameters.
            
        Returns:
            The tool call result.
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Missing tool name")
        
        if tool_name not in TOOLS_BY_NAME:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Generate the Fusion 360 script
        script = generate_script(tool_name, arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Generated Fusion 360 script for {tool_name}:\n\n```python\n{script}\n```\n\nCopy and paste this script into Fusion 360's Scripts and Add-Ins dialog to execute it."
                }
            ]
        }
    
    def _create_success_response(self, request_id: Any, result: Any) -> str:
        """
        Create a JSON-RPC 2.0 success response.
        
        Args:
            request_id: The request ID.
            result: The result data.
            
        Returns:
            The JSON response string.
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        return json.dumps(response)
    
    def _create_error_response(self, request_id: Any, code: int, message: str) -> str:
        """
        Create a JSON-RPC 2.0 error response.
        
        Args:
            request_id: The request ID.
            code: The error code.
            message: The error message.
            
        Returns:
            The JSON response string.
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        return json.dumps(response)


def main():
    """Main entry point for the MCP server."""
    server = MCPServer()
    
    logger.info("Starting Fusion 360 MCP Server")
    
    try:
        # Read from stdin and write to stdout
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            logger.debug(f"Received: {line}")
            
            response = server.handle_message(line)
            if response:
                print(response, flush=True)
                logger.debug(f"Sent: {response}")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
