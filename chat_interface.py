"""
Fusion 360 Chat Interface Example

This demonstrates how to create a simple chat interface for controlling Fusion 360
in real-time using natural language commands.
"""

import socket
import json
import re

class Fusion360ChatInterface:
    """Simple chat interface for Fusion 360 control."""
    
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 9999
    
    def send_command(self, command):
        """Send a command to Fusion 360."""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(10)
            client.connect((self.host, self.port))
            
            client.send(json.dumps(command).encode('utf-8'))
            response = client.recv(8192)
            result = json.loads(response.decode('utf-8'))
            
            client.close()
            return result
        except Exception as e:
            return {'status': 'error', 'message': f'Connection failed: {str(e)}'}
    
    def parse_chat_command(self, text):
        """Parse natural language chat commands."""
        text = text.lower().strip()
        
        # Document information commands
        if any(phrase in text for phrase in ['get document', 'current document', 'document info']):
            return {'type': 'get_document_info'}
        
        if any(phrase in text for phrase in ['model info', 'show model', 'model details']):
            return {'type': 'get_model_info'}
        
        # Object creation commands
        if 'create box' in text or 'make box' in text:
            # Extract dimensions if provided
            dimensions = re.findall(r'(\d+)', text)
            if len(dimensions) >= 3:
                return {
                    'type': 'create_object',
                    'object_type': 'box',
                    'parameters': {
                        'width': int(dimensions[0]),
                        'height': int(dimensions[1]),
                        'depth': int(dimensions[2])
                    }
                }
            else:
                return {
                    'type': 'create_object',
                    'object_type': 'box',
                    'parameters': {'width': 50, 'height': 50, 'depth': 30}
                }
        
        if 'create cylinder' in text or 'make cylinder' in text:
            dimensions = re.findall(r'(\d+)', text)
            if len(dimensions) >= 2:
                return {
                    'type': 'create_object',
                    'object_type': 'cylinder',
                    'parameters': {
                        'radius': int(dimensions[0]),
                        'height': int(dimensions[1])
                    }
                }
            else:
                return {
                    'type': 'create_object',
                    'object_type': 'cylinder',
                    'parameters': {'radius': 25, 'height': 50}
                }
        
        # MCP tool commands
        if 'list tools' in text or 'available tools' in text:
            return {'type': 'list_mcp_tools'}
        
        if 'server status' in text or 'status' in text:
            return {'type': 'get_server_status'}
        
        return None
    
    def format_response(self, result, original_command):
        """Format the response for display."""
        if result.get('status') == 'error':
            return f"❌ Error: {result.get('message')}"
        
        if original_command.get('type') == 'get_document_info':
            data = result.get('data', {})
            return f"""📄 Document Information:
  Name: {data.get('name')}
  Bodies: {data.get('body_count')}
  Sketches: {data.get('sketch_count')}
  Features: {data.get('feature_count')}
  Saved: {data.get('is_saved')}"""
        
        elif original_command.get('type') == 'get_model_info':
            data = result.get('data', {})
            bodies = data.get('bodies', [])
            total_volume = sum(body.get('volume', 0) for body in bodies)
            
            response = f"🧊 Model contains {len(bodies)} bodies:\n"
            for body in bodies:
                response += f"  • {body.get('name')}: {body.get('volume', 0):.2f} cm³\n"
            response += f"📊 Total volume: {total_volume:.2f} cm³"
            return response
        
        elif original_command.get('type') == 'create_object':
            if result.get('status') == 'success':
                data = result.get('data', {})
                return f"✅ {result.get('message')}\n📦 Volume: {data.get('volume', 0):.2f} cm³"
        
        elif original_command.get('type') == 'list_mcp_tools':
            tools = result.get('data', {}).get('tools', [])
            response = f"🛠️ Available MCP Tools ({len(tools)}):\n"
            for tool in tools[:10]:  # Show first 10
                response += f"  • {tool.get('name')}: {tool.get('description')}\n"
            if len(tools) > 10:
                response += f"  ... and {len(tools) - 10} more tools"
            return response
        
        elif original_command.get('type') == 'get_server_status':
            data = result.get('data', {})
            status_icon = '🟢' if data.get('server_running') else '🔴'
            return f"""{status_icon} Server Status:
  Running: {data.get('server_running')}
  Fusion Active: {data.get('fusion_active')}
  MCP Tools: {data.get('mcp_tools_available')}
  Address: {data.get('server_address')}"""
        
        return f"✅ Command executed successfully: {result.get('message', 'Done')}"
    
    def chat_loop(self):
        """Main chat loop."""
        print("🎮 Fusion 360 Chat Interface")
        print("=" * 40)
        print("Type your commands in natural language!")
        print("Examples:")
        print("  - 'create box 100 60 40'")
        print("  - 'make cylinder radius 30 height 80'")
        print("  - 'get document info'")
        print("  - 'show model details'")
        print("  - 'list available tools'")
        print("Type 'quit' to exit")
        print("=" * 40)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Parse the command
                command = self.parse_chat_command(user_input)
                
                if command is None:
                    print("❓ I didn't understand that command. Try:")
                    print("  - 'create box [width] [height] [depth]'")
                    print("  - 'create cylinder [radius] [height]'")
                    print("  - 'get document info'")
                    print("  - 'show model details'")
                    continue
                
                # Send command to Fusion 360
                print("⏳ Sending command to Fusion 360...")
                result = self.send_command(command)
                
                # Format and display response
                response = self.format_response(result, command)
                print(f"🤖 Fusion 360: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Main function."""
    interface = Fusion360ChatInterface()
    
    # Test connection first
    print("Testing connection to Fusion 360...")
    test_result = interface.send_command({'type': 'get_server_status'})
    
    if test_result.get('status') == 'error':
        print("❌ Cannot connect to Fusion 360!")
        print("Make sure:")
        print("1. Fusion 360 is running")
        print("2. MCP add-in is loaded (Shift+S > Add-Ins > Fusion360MCP > Run)")
        return
    
    print("✅ Connected to Fusion 360!")
    interface.chat_loop()

if __name__ == '__main__':
    main()
