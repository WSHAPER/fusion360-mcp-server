#!/usr/bin/env python3
"""
Fusion 360 Real-Time Control Installer
=====================================

This script installs the complete real-time chat control system for Fusion 360.
It sets up the add-in, creates necessary directories, and configures everything
to work out of the box.

Usage: python install_realtime.py
"""

import os
import sys
import json
import shutil
from pathlib import Path

def get_fusion360_addins_path():
    """Get the Fusion 360 add-ins directory path"""
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "Autodesk" / "Autodesk Fusion 360" / "API" / "AddIns"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Autodesk" / "Autodesk Fusion 360" / "API" / "AddIns"
    else:
        # Linux
        return Path.home() / ".config" / "Autodesk" / "Autodesk Fusion 360" / "API" / "AddIns"

def create_addon_manifest():
    """Create the add-in manifest file"""
    return {
        "autodeskProduct": "Fusion360",
        "type": "addin",
        "id": "Fusion360MCP",
        "author": "Fusion360-MCP-Server",
        "description": {
            "": "Real-time chat control for Fusion 360 via MCP"
        },
        "version": "1.0.0",
        "runOnStartup": True,
        "supportedOS": "windows|mac|linux",
        "editEnabled": True
    }

def create_addon_python():
    """Create the main add-in Python file"""
    return '''import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import threading
import socket
import json
import time

app = adsk.core.Application.get()
ui = app.userInterface

# Global variables for the server
server = None
server_thread = None
is_server_running = False

class Fusion360MCPCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            command = args.command
            command.execute.add(Fusion360MCPCommandExecuteHandler())
        except:
            ui.messageBox('Failed:\\n{}'.format(traceback.format_exc()))

class Fusion360MCPCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            ui.messageBox('Fusion 360 MCP Real-Time Control is active!\\nSocket server running on port 9999.')
        except:
            ui.messageBox('Failed:\\n{}'.format(traceback.format_exc()))

def start_control_server():
    """Start the socket server for real-time control"""
    global server, server_thread, is_server_running
    
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', 9999))
        server.listen(5)
        is_server_running = True
        
        ui.messageBox('Real-time control server started on port 9999')
        
        while is_server_running:
            try:
                client, addr = server.accept()
                client_thread = threading.Thread(target=handle_client, args=(client,))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if is_server_running:
                    ui.messageBox(f'Server error: {str(e)}')
                break
                
    except Exception as e:
        ui.messageBox(f'Failed to start server: {str(e)}')

def handle_client(client):
    """Handle individual client connections"""
    try:
        while True:
            data = client.recv(1024)
            if not data:
                break
                
            try:
                command = json.loads(data.decode())
                result = execute_command(command)
                response = json.dumps(result) + '\\n'
                client.send(response.encode())
            except json.JSONDecodeError:
                error_response = json.dumps({'error': 'Invalid JSON'}) + '\\n'
                client.send(error_response.encode())
                
    except Exception as e:
        pass
    finally:
        client.close()

def execute_command(command):
    """Execute a command from the chat interface"""
    try:
        action = command.get('action', '')
        
        if action == 'get_document':
            return get_current_document()
        elif action == 'create_box':
            return create_box(command.get('width', 10), command.get('height', 10), command.get('depth', 10))
        elif action == 'create_cylinder':
            return create_cylinder(command.get('radius', 5), command.get('height', 10))
        elif action == 'get_bodies_info':
            return get_bodies_info()
        else:
            return {'error': f'Unknown action: {action}'}
            
    except Exception as e:
        return {'error': str(e)}

def get_current_document():
    """Get information about the current document"""
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {'error': 'No active design document'}
            
        return {
            'success': True,
            'document_name': app.activeDocument.name,
            'design_type': design.designType,
            'bodies_count': design.rootComponent.bRepBodies.count
        }
    except Exception as e:
        return {'error': str(e)}

def create_box(width, height, depth):
    """Create a box with specified dimensions"""
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {'error': 'No active design document'}
            
        # Create a sketch
        sketches = design.rootComponent.sketches
        xyPlane = design.rootComponent.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        
        # Create rectangle
        rectangles = sketch.sketchCurves.sketchLines
        corner1 = adsk.core.Point3D.create(0, 0, 0)
        corner2 = adsk.core.Point3D.create(width/10, height/10, 0)  # Convert mm to cm
        rectangles.addTwoPointRectangle(corner1, corner2)
        
        # Extrude to create the box
        profile = sketch.profiles.item(0)
        extrudes = design.rootComponent.features.extrudeFeatures
        extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extrudeInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(depth/10))  # Convert mm to cm
        extrude = extrudes.add(extrudeInput)
        
        return {
            'success': True,
            'message': f'Created box: {width}x{height}x{depth}mm',
            'body_name': extrude.bodies.item(0).name
        }
        
    except Exception as e:
        return {'error': str(e)}

def create_cylinder(radius, height):
    """Create a cylinder with specified dimensions"""
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {'error': 'No active design document'}
            
        # Create a sketch
        sketches = design.rootComponent.sketches
        xyPlane = design.rootComponent.xYConstructionPlane
        sketch = sketches.add(xyPlane)
        
        # Create circle
        circles = sketch.sketchCurves.sketchCircles
        centerPoint = adsk.core.Point3D.create(0, 0, 0)
        circle = circles.addByCenterRadius(centerPoint, radius/10)  # Convert mm to cm
        
        # Extrude to create the cylinder
        profile = sketch.profiles.item(0)
        extrudes = design.rootComponent.features.extrudeFeatures
        extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extrudeInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height/10))  # Convert mm to cm
        extrude = extrudes.add(extrudeInput)
        
        return {
            'success': True,
            'message': f'Created cylinder: radius {radius}mm, height {height}mm',
            'body_name': extrude.bodies.item(0).name
        }
        
    except Exception as e:
        return {'error': str(e)}

def get_bodies_info():
    """Get information about all bodies in the design"""
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return {'error': 'No active design document'}
            
        bodies = design.rootComponent.bRepBodies
        body_list = []
        total_volume = 0
        
        for i in range(bodies.count):
            body = bodies.item(i)
            volume_cm3 = body.volume  # Fusion API returns volume in cm³
            total_volume += volume_cm3
            
            body_list.append({
                'name': body.name,
                'volume_cm3': round(volume_cm3, 2)
            })
        
        return {
            'success': True,
            'bodies_count': bodies.count,
            'bodies': body_list,
            'total_volume_cm3': round(total_volume, 2)
        }
        
    except Exception as e:
        return {'error': str(e)}

def stop_control_server():
    """Stop the socket server"""
    global server, is_server_running
    
    is_server_running = False
    if server:
        try:
            server.close()
        except:
            pass

def run(context):
    try:
        # Create command definition
        cmdDef = ui.commandDefinitions.itemById('Fusion360MCPCommand')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition('Fusion360MCPCommand', 
                                                             'MCP Real-Time Control', 
                                                             'Start MCP real-time control server')
        
        # Connect the command created handler
        cmdDef.commandCreated.add(Fusion360MCPCommandCreatedHandler())
        
        # Start the server in a separate thread
        server_thread = threading.Thread(target=start_control_server)
        server_thread.daemon = True
        server_thread.start()
        
    except:
        ui.messageBox('Failed:\\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        stop_control_server()
        
        # Clean up command definition
        cmdDef = ui.commandDefinitions.itemById('Fusion360MCPCommand')
        if cmdDef:
            cmdDef.deleteMe()
            
    except:
        ui.messageBox('Failed:\\n{}'.format(traceback.format_exc()))
'''

def create_chat_interface():
    """Create the chat interface script"""
    return '''#!/usr/bin/env python3
"""
Fusion 360 Chat Interface
========================

Real-time chat control for Fusion 360. Use natural language commands to control Fusion 360.

Examples:
- "create box 100 50 25"
- "make cylinder radius 30 height 80"
- "show current document"
- "list all bodies"
"""

import socket
import json
import re
import sys

def connect_to_fusion():
    """Connect to the Fusion 360 control server"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 9999))
        return client
    except Exception as e:
        print(f"[ERROR] Cannot connect to Fusion 360. Make sure the add-in is loaded and running.")
        print(f"Error: {e}")
        return None

def send_command(client, command):
    """Send a command to Fusion 360 and get the response"""
    try:
        client.send(json.dumps(command).encode())
        response = client.recv(4096)
        return json.loads(response.decode().strip())
    except Exception as e:
        return {'error': f'Communication error: {e}'}

def parse_chat_command(text):
    """Parse natural language commands into API calls"""
    text = text.lower().strip()
    
    # Box creation: "create box 100 50 25" or "make box 100 50 25"
    box_pattern = r'(?:create|make)\\s+box\\s+(\\d+)\\s+(\\d+)\\s+(\\d+)'
    box_match = re.search(box_pattern, text)
    if box_match:
        return {
            'action': 'create_box',
            'width': int(box_match.group(1)),
            'height': int(box_match.group(2)),
            'depth': int(box_match.group(3))
        }
    
    # Cylinder creation: "create cylinder 30 80" or "make cylinder radius 30 height 80"
    cyl_pattern1 = r'(?:create|make)\\s+cylinder\\s+(\\d+)\\s+(\\d+)'
    cyl_pattern2 = r'(?:create|make)\\s+cylinder\\s+radius\\s+(\\d+)\\s+height\\s+(\\d+)'
    
    cyl_match = re.search(cyl_pattern2, text) or re.search(cyl_pattern1, text)
    if cyl_match:
        return {
            'action': 'create_cylinder',
            'radius': int(cyl_match.group(1)),
            'height': int(cyl_match.group(2))
        }
    
    # Document info
    if 'document' in text or 'info' in text:
        return {'action': 'get_document'}
    
    # Bodies info
    if 'bodies' in text or 'list' in text or 'volume' in text:
        return {'action': 'get_bodies_info'}
    
    return None

def format_response(response):
    """Format the response for display"""
    if 'error' in response:
        return f"[ERROR] {response['error']}"
    
    if response.get('success'):
        if 'message' in response:
            return f"[OK] {response['message']}"
        elif 'document_name' in response:
            return f"Document: {response['document_name']} ({response['bodies_count']} bodies)"
        elif 'bodies_count' in response:
            bodies_info = response
            result = f"Design contains {bodies_info['bodies_count']} bodies\\n"
            result += f"Total volume: {bodies_info['total_volume_cm3']} cm³\\n"
            for body in bodies_info['bodies']:
                result += f"  - {body['name']}: {body['volume_cm3']} cm³\\n"
            return result.strip()
    
    return f"[OK] Command executed: {response}"

def main():
    print("Fusion 360 Chat Control Interface")
    print("=" * 40)
    print("Commands:")
    print("  create box 100 50 25")
    print("  make cylinder radius 30 height 80")
    print("  show document")
    print("  list bodies")
    print("  quit")
    print("=" * 40)
    
    client = connect_to_fusion()
    if not client:
        return
    
    print("Connected to Fusion 360!")
    print()
    
    try:
        while True:
            try:
                command_text = input("Enter command: ").strip()
                
                if command_text.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not command_text:
                    continue
                
                command = parse_chat_command(command_text)
                if not command:
                    print("I don't understand that command. Try:")
                    print("   create box 100 50 25")
                    print("   make cylinder radius 30 height 80")
                    continue
                
                response = send_command(client, command)
                print(format_response(response))
                print()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                
    finally:
        client.close()
        print("Disconnected from Fusion 360")

if __name__ == "__main__":
    main()
'''

def create_usage_guide(addon_dir):
    """Create the usage guide content"""
    return f'''# Fusion 360 Real-Time Control Usage

## Installation Complete!

The real-time control system has been installed. Here's how to use it:

## Step 1: Start Fusion 360
1. Open Autodesk Fusion 360
2. The MCP Real-Time Control add-in should load automatically
3. You'll see a confirmation dialog when the socket server starts

## Step 2: Use Chat Control
Run the chat interface:
```bash
python chat_interface.py
```

## Chat Commands

### Create Objects
- `create box 100 50 25` - Creates a box with width=100mm, height=50mm, depth=25mm
- `make cylinder radius 30 height 80` - Creates a cylinder with radius=30mm, height=80mm

### Get Information
- `show document` - Get current document info
- `list bodies` - Show all bodies and volumes

### Example Session
```
Enter command: create box 200 100 50
[OK] Created box: 200x100x50mm

Enter command: make cylinder radius 35 height 90
[OK] Created cylinder: radius 35mm, height 90mm

Enter command: list bodies
Design contains 2 bodies
Total volume: 2403.33 cm³
  - Box: 1000.00 cm³
  - Cylinder: 1403.33 cm³
```

## Troubleshooting

### Add-in not loading
1. Check that Fusion 360 add-ins are enabled
2. Restart Fusion 360
3. Check the Scripts and Add-Ins panel in Fusion 360

### Connection fails
1. Make sure Fusion 360 is running
2. Ensure the add-in loaded successfully
3. Check that port 9999 is not blocked by firewall

### Manual add-in loading
1. In Fusion 360: Tools → Add-Ins → Scripts and Add-Ins
2. Click the "+" button next to Add-Ins
3. Navigate to: `{addon_dir}`
4. Select the Fusion360MCP folder

## Integration with MCP

This real-time control system works alongside the MCP server. You can:
1. Use Claude Desktop with MCP for script generation
2. Use the chat interface for real-time control
3. Combine both approaches for maximum flexibility

Happy 3D modeling!
'''

def install_realtime_control():
    """Main installation function"""
    print("Installing Fusion 360 Real-Time Control System")
    print("=" * 50)
    
    # Get Fusion 360 add-ins directory
    addins_path = get_fusion360_addins_path()
    addon_dir = addins_path / "Fusion360MCP"
    
    print(f"Target directory: {addon_dir}")
    
    # Create add-in directory
    addon_dir.mkdir(parents=True, exist_ok=True)
    
    # Create manifest file
    manifest_path = addon_dir / "Fusion360MCP.manifest"
    with open(manifest_path, 'w') as f:
        json.dump(create_addon_manifest(), f, indent=2)
    print(f"[OK] Created manifest: {manifest_path}")
    
    # Create main Python file
    python_path = addon_dir / "Fusion360MCP.py"
    with open(python_path, 'w') as f:
        f.write(create_addon_python())
    print(f"[OK] Created add-in: {python_path}")
    
    # Create chat interface in project root
    chat_path = Path(__file__).parent / "chat_interface.py"
    with open(chat_path, 'w') as f:
        f.write(create_chat_interface())
    print(f"[OK] Created chat interface: {chat_path}")
    
    # Create usage instructions
    instructions_path = Path(__file__).parent / "REALTIME_USAGE.md"
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(create_usage_guide(addon_dir))
    print(f"[OK] Created usage guide: {instructions_path}")
    
    print("\nInstallation Complete!")
    print("\nNext steps:")
    print("1. Start Fusion 360 (the add-in will load automatically)")
    print("2. Run: python chat_interface.py")
    print("3. Use commands like 'create box 100 50 25'")
    print(f"\nRead {instructions_path.name} for detailed usage instructions.")

if __name__ == "__main__":
    install_realtime_control()
