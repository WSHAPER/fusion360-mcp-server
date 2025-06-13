"""
Fusion 360 Real-Time Control Client

This client can connect to the Fusion 360 real-time control server and send commands.
It provides a Python interface for controlling Fusion 360 from external applications.
"""

import socket
import json
import time
import traceback

class Fusion360Client:
    """Client for communicating with Fusion 360 real-time control server."""
    
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self):
        """Connect to the Fusion 360 control server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to Fusion 360: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        if self.socket:
            self.socket.close()
            self.connected = False
    
    def send_command(self, command):
        """Send a command to Fusion 360 and return the response."""
        if not self.connected:
            return {'status': 'error', 'message': 'Not connected to Fusion 360'}
        
        try:
            # Send command
            command_json = json.dumps(command)
            self.socket.send(command_json.encode('utf-8'))
            
            # Receive response
            response_data = self.socket.recv(8192)
            response = json.loads(response_data.decode('utf-8'))
            
            return response
            
        except Exception as e:
            return {'status': 'error', 'message': f'Communication error: {str(e)}'}
    
    def get_document_info(self):
        """Get information about the current Fusion 360 document."""
        command = {'type': 'get_document_info'}
        return self.send_command(command)
    
    def get_model_info(self):
        """Get detailed model information."""
        command = {'type': 'get_model_info'}
        return self.send_command(command)
    
    def create_box(self, width=50, height=50, depth=30):
        """Create a box in Fusion 360."""
        command = {
            'type': 'create_object',
            'object_type': 'box',
            'parameters': {
                'width': width,
                'height': height,
                'depth': depth
            }
        }
        return self.send_command(command)
    
    def create_cylinder(self, radius=25, height=50):
        """Create a cylinder in Fusion 360."""
        command = {
            'type': 'create_object',
            'object_type': 'cylinder',
            'parameters': {
                'radius': radius,
                'height': height
            }
        }
        return self.send_command(command)
    
    def execute_mcp_tool(self, tool_name, parameters):
        """Execute an MCP tool in Fusion 360."""
        command = {
            'type': 'execute_mcp_tool',
            'tool_name': tool_name,
            'parameters': parameters
        }
        return self.send_command(command)
    
    def list_mcp_tools(self):
        """List available MCP tools."""
        command = {'type': 'list_mcp_tools'}
        return self.send_command(command)
    
    def get_server_status(self):
        """Get server status."""
        command = {'type': 'get_server_status'}
        return self.send_command(command)

# Convenience functions for easy use
def connect_to_fusion360():
    """Connect to Fusion 360 and return client object."""
    client = Fusion360Client()
    if client.connect():
        print("✅ Connected to Fusion 360 successfully!")
        return client
    else:
        print("❌ Failed to connect to Fusion 360")
        print("Make sure:")
        print("1. Fusion 360 is running")
        print("2. The MCP add-in is loaded and running")
        print("3. The real-time control server is active")
        return None

def test_fusion360_connection():
    """Test connection to Fusion 360 and show status."""
    client = connect_to_fusion360()
    if client:
        try:
            # Test basic commands
            status = client.get_server_status()
            print(f"Server Status: {status}")
            
            doc_info = client.get_document_info()
            print(f"Document Info: {doc_info}")
            
            client.disconnect()
            return True
        except Exception as e:
            print(f"Error testing connection: {str(e)}")
            return False
    return False

def create_sample_object():
    """Create a sample object in Fusion 360."""
    client = connect_to_fusion360()
    if client:
        try:
            # Create a sample box
            result = client.create_box(width=100, height=50, depth=25)
            print(f"Created object: {result}")
            
            client.disconnect()
            return result
        except Exception as e:
            print(f"Error creating object: {str(e)}")
            return None
    return None

# Chat command interface functions
def fusion_get_current_document():
    """Get current document information - for chat commands."""
    client = connect_to_fusion360()
    if client:
        try:
            doc_info = client.get_document_info()
            model_info = client.get_model_info()
            client.disconnect()
            
            return {
                'document': doc_info,
                'model': model_info
            }
        except Exception as e:
            return {'error': f'Failed to get document info: {str(e)}'}
    return {'error': 'Could not connect to Fusion 360'}

def fusion_create_object(object_type, **kwargs):
    """Create an object in Fusion 360 - for chat commands."""
    client = connect_to_fusion360()
    if client:
        try:
            if object_type.lower() == 'box':
                result = client.create_box(
                    width=kwargs.get('width', 50),
                    height=kwargs.get('height', 50), 
                    depth=kwargs.get('depth', 30)
                )
            elif object_type.lower() == 'cylinder':
                result = client.create_cylinder(
                    radius=kwargs.get('radius', 25),
                    height=kwargs.get('height', 50)
                )
            else:
                result = {'status': 'error', 'message': f'Unknown object type: {object_type}'}
            
            client.disconnect()
            return result
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to create {object_type}: {str(e)}'}
    return {'status': 'error', 'message': 'Could not connect to Fusion 360'}

def fusion_execute_mcp_tool(tool_name, parameters=None):
    """Execute an MCP tool - for chat commands."""
    if parameters is None:
        parameters = {}
        
    client = connect_to_fusion360()
    if client:
        try:
            result = client.execute_mcp_tool(tool_name, parameters)
            client.disconnect()
            return result
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to execute {tool_name}: {str(e)}'}
    return {'status': 'error', 'message': 'Could not connect to Fusion 360'}

def fusion_list_tools():
    """List available MCP tools - for chat commands."""
    client = connect_to_fusion360()
    if client:
        try:
            result = client.list_mcp_tools()
            client.disconnect()
            return result
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to list tools: {str(e)}'}
    return {'status': 'error', 'message': 'Could not connect to Fusion 360'}

if __name__ == '__main__':
    # Test the client
    print("Testing Fusion 360 Real-Time Control Client...")
    test_fusion360_connection()
