"""
Fusion 360 MCP Integration Add-in - Real-Time Control

This add-in provides socket-based real-time control for Fusion 360,
allowing external applications to control Fusion 360 directly via JSON commands.
"""

import adsk.core
import adsk.fusion
import traceback
import socket
import threading
import json
import os
import sys

# Add the MCP server source directory to Python path for imports
mcp_server_path = r"C:\Users\admin\Documents\github\fusion360-mcp-server\src"
if mcp_server_path not in sys.path:
    sys.path.insert(0, mcp_server_path)

try:
    from script_generator import generate_script, TOOL_REGISTRY, TOOLS_BY_NAME
except ImportError:
    TOOL_REGISTRY = []
    TOOLS_BY_NAME = {}
    def generate_script(tool_name, parameters):
        return f"# MCP server not available\n# Tool: {tool_name}\n# Parameters: {parameters}"

# Global variables
app = adsk.core.Application.get()
ui = app.userInterface
server = None
server_thread = None
is_server_running = False

def run(context):
    """Called when the add-in is started."""
    global server, server_thread, is_server_running
    
    try:
        # Start the control server
        start_control_server()
        
        app.log('Fusion 360 MCP Real-Time Control Server started')
        app.log('Server listening on 127.0.0.1:9999')
        
        # Show success message
        ui.messageBox(
            'Fusion 360 MCP Integration loaded successfully!\n\n'
            'Real-time control server is running on 127.0.0.1:9999\n'
            'You can now control Fusion 360 from external applications.',
            'MCP Integration Ready'
        )
        
    except Exception as e:
        error_msg = f'Failed to load MCP Integration:\n{traceback.format_exc()}'
        ui.messageBox(error_msg)
        app.log(error_msg)

def stop(context):
    """Called when the add-in is stopped."""
    global server, is_server_running
    
    try:
        # Stop the server
        is_server_running = False
        if server:
            server.close()
            
        app.log('Fusion 360 MCP Real-Time Control Server stopped')
        
    except Exception as e:
        ui.messageBox(f'Failed to stop MCP Integration:\n{traceback.format_exc()}')

def start_control_server():
    """Start the socket server for real-time control."""
    global server, server_thread, is_server_running
    
    try:
        # Create server socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', 9999))
        server.listen(5)
        
        is_server_running = True
        
        # Start server thread
        server_thread = threading.Thread(target=server_worker, daemon=True)
        server_thread.start()
        
        app.log('Control server started on 127.0.0.1:9999')
        
    except Exception as e:
        app.log(f'Error starting control server: {str(e)}')
        raise

def server_worker():
    """Main server loop - runs in background thread."""
    global server, is_server_running
    
    app.log('Server worker thread started')
    
    try:
        while is_server_running:
            try:
                # Accept client connections
                client_socket, address = server.accept()
                app.log(f'Client connected from {address}')
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=handle_client, 
                    args=(client_socket, address), 
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if is_server_running:  # Only log if we're supposed to be running
                    app.log(f'Error accepting client connection: {str(e)}')
                break
                
    except Exception as e:
        app.log(f'Server worker error: {str(e)}')
    
    app.log('Server worker thread ended')

def handle_client(client_socket, address):
    """Handle commands from a connected client."""
    try:
        while is_server_running:
            # Receive data from client
            data = client_socket.recv(4096)
            if not data:
                break
                
            try:
                # Parse JSON command
                command = json.loads(data.decode('utf-8'))
                app.log(f'Received command: {command}')
                
                # Execute command and get response
                response = execute_command(command)
                
                # Send response back to client
                response_json = json.dumps(response).encode('utf-8')
                client_socket.send(response_json)
                
            except json.JSONDecodeError:
                error_response = {
                    'status': 'error',
                    'message': 'Invalid JSON format'
                }
                client_socket.send(json.dumps(error_response).encode('utf-8'))
                
            except Exception as e:
                error_response = {
                    'status': 'error', 
                    'message': f'Command execution failed: {str(e)}'
                }
                client_socket.send(json.dumps(error_response).encode('utf-8'))
                
    except Exception as e:
        app.log(f'Client handler error: {str(e)}')
    finally:
        client_socket.close()
        app.log(f'Client {address} disconnected')

def execute_command(command):
    """Execute a command and return the response."""
    try:
        cmd_type = command.get('type')
        
        if cmd_type == 'get_document_info':
            return get_document_info()
        elif cmd_type == 'get_model_info':
            return get_model_info()
        elif cmd_type == 'create_object':
            return create_object(command.get('object_type'), command.get('parameters', {}))
        elif cmd_type == 'execute_mcp_tool':
            return execute_mcp_tool(command.get('tool_name'), command.get('parameters', {}))
        elif cmd_type == 'list_mcp_tools':
            return list_mcp_tools()
        elif cmd_type == 'get_server_status':
            return get_server_status()
        else:
            return {'status': 'error', 'message': f'Unknown command type: {cmd_type}'}
            
    except Exception as e:
        return {'status': 'error', 'message': f'Command execution error: {str(e)}'}

def get_document_info():
    """Get information about the current document."""
    try:
        design = app.activeProduct
        
        if not design:
            return {'status': 'error', 'message': 'No active document'}
            
        doc_info = {
            'status': 'success',
            'data': {
                'name': design.parentDocument.name,
                'is_saved': design.parentDocument.isSaved,
                'units': design.fusionUnitsManager.defaultLengthUnits,
                'body_count': design.rootComponent.bRepBodies.count,
                'sketch_count': design.rootComponent.sketches.count,
                'feature_count': design.rootComponent.features.count
            }
        }
        
        app.log(f'Document info retrieved: {doc_info["data"]["name"]}')
        return doc_info
        
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to get document info: {str(e)}'}

def get_model_info():
    """Get detailed model information."""
    try:
        design = app.activeProduct
        
        if not design:
            return {'status': 'error', 'message': 'No active document'}
            
        component = design.rootComponent
        
        # Get bodies info
        bodies_info = []
        for i in range(component.bRepBodies.count):
            body = component.bRepBodies.item(i)
            bodies_info.append({
                'name': body.name,
                'volume': body.volume,
                'material': body.material.name if body.material else 'None'
            })
        
        # Get sketches info
        sketches_info = []
        for i in range(component.sketches.count):
            sketch = component.sketches.item(i)
            sketches_info.append({
                'name': sketch.name,
                'profile_count': sketch.profiles.count,
                'curve_count': sketch.sketchCurves.count
            })
        
        model_info = {
            'status': 'success',
            'data': {
                'document': design.parentDocument.name,
                'bodies': bodies_info,
                'sketches': sketches_info,
                'timeline_position': design.timeline.markerPosition
            }
        }
        
        return model_info
        
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to get model info: {str(e)}'}

def create_object(object_type, parameters):
    """Create an object based on type and parameters."""
    try:
        design = app.activeProduct
        
        if not design:
            return {'status': 'error', 'message': 'No active document'}
            
        component = design.rootComponent
        
        if object_type == 'box':
            return create_box(component, parameters)
        elif object_type == 'cylinder':
            return create_cylinder(component, parameters)
        else:
            return {'status': 'error', 'message': f'Unknown object type: {object_type}'}
            
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to create {object_type}: {str(e)}'}

def create_box(component, params):
    """Create a parametric box."""
    try:
        # Get parameters with defaults
        width = float(params.get('width', 50))  # mm
        height = float(params.get('height', 50))  # mm
        depth = float(params.get('depth', 30))  # mm
        
        # Convert mm to cm (Fusion's internal units)
        width_cm = width / 10
        height_cm = height / 10
        depth_cm = depth / 10
        
        # Create sketch
        sketches = component.sketches
        xy_plane = component.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Draw rectangle
        origin = adsk.core.Point3D.create(0, 0, 0)
        corner = adsk.core.Point3D.create(width_cm, height_cm, 0)
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(origin, corner)
        
        # Extrude
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        distance = adsk.core.ValueInput.createByReal(depth_cm)
        extrude_input.setDistanceExtent(False, distance)
        
        extrude = extrudes.add(extrude_input)
        
        # Name the body
        body = extrude.bodies.item(0)
        body.name = f'Box_{width}x{height}x{depth}'
        
        result = {
            'status': 'success',
            'message': f'Created box: {width}mm x {height}mm x {depth}mm',
            'data': {
                'body_name': body.name,
                'volume': body.volume
            }
        }
        
        app.log(f'Created box: {width}mm x {height}mm x {depth}mm')
        return result
        
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to create box: {str(e)}'}

def create_cylinder(component, params):
    """Create a cylinder."""
    try:
        radius = float(params.get('radius', 25)) / 10  # Convert mm to cm
        height = float(params.get('height', 50)) / 10  # Convert mm to cm
        
        # Create sketch
        sketches = component.sketches
        xy_plane = component.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Draw circle
        center = adsk.core.Point3D.create(0, 0, 0)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
        
        # Extrude
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        distance = adsk.core.ValueInput.createByReal(height)
        extrude_input.setDistanceExtent(False, distance)
        
        extrude = extrudes.add(extrude_input)
        
        # Name the body
        body = extrude.bodies.item(0)
        body.name = f'Cylinder_R{radius*10}_H{height*10}'
        
        result = {
            'status': 'success',
            'message': f'Created cylinder: radius {radius*10}mm, height {height*10}mm',
            'data': {
                'body_name': body.name,
                'volume': body.volume
            }
        }
        
        return result
        
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to create cylinder: {str(e)}'}

def execute_mcp_tool(tool_name, parameters):
    """Execute an MCP tool and return the result."""
    try:
        if tool_name not in TOOLS_BY_NAME:
            return {'status': 'error', 'message': f'Unknown MCP tool: {tool_name}'}
        
        # Generate script using MCP
        script_code = generate_script(tool_name, parameters)
        
        # Execute the generated script
        exec(script_code, globals())
        
        result = {
            'status': 'success',
            'message': f'Executed MCP tool: {tool_name}',
            'data': {
                'tool_name': tool_name,
                'parameters': parameters,
                'script_generated': True
            }
        }
        
        app.log(f'Executed MCP tool: {tool_name} with parameters: {parameters}')
        return result
        
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to execute MCP tool {tool_name}: {str(e)}'}

def list_mcp_tools():
    """List available MCP tools."""
    try:
        tools_list = []
        for tool in TOOL_REGISTRY:
            tools_list.append({
                'name': tool['name'],
                'description': tool['description'],
                'parameters': list(tool['parameters'].keys())
            })
        
        return {
            'status': 'success',
            'data': {
                'tools': tools_list,
                'count': len(tools_list)
            }
        }
        
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to list MCP tools: {str(e)}'}

def get_server_status():
    """Get server status information."""
    try:
        return {
            'status': 'success',
            'data': {
                'server_running': is_server_running,
                'fusion_active': app.activeProduct is not None,
                'mcp_tools_available': len(TOOL_REGISTRY) > 0,
                'server_address': '127.0.0.1:9999'
            }
        }
    except Exception as e:
        return {'status': 'error', 'message': f'Failed to get server status: {str(e)}'}
