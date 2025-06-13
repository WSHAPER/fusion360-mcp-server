"""
Quick test for Fusion 360 MCP real-time integration
"""

import socket
import json
import time

def quick_test():
    print("Testing Fusion 360 MCP connection...")
    
    try:
        # Test connection
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect(('127.0.0.1', 9999))
        
        # Send status command
        command = {'type': 'get_server_status'}
        client.send(json.dumps(command).encode('utf-8'))
        
        # Get response
        response = client.recv(4096)
        result = json.loads(response.decode('utf-8'))
        
        client.close()
        
        print("SUCCESS: Connected to Fusion 360!")
        print(f"Status: {result}")
        
        # Test creating a simple object
        print("\nTesting object creation...")
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(10)
        client.connect(('127.0.0.1', 9999))
        
        box_command = {
            'type': 'create_object',
            'object_type': 'box',
            'parameters': {'width': 75, 'height': 50, 'depth': 25}
        }
        
        client.send(json.dumps(box_command).encode('utf-8'))
        response = client.recv(4096)
        result = json.loads(response.decode('utf-8'))
        
        client.close()
        
        if result.get('status') == 'success':
            print("SUCCESS: Object creation works!")
            print(f"Created: {result.get('message')}")
            print("\nReal-time control is working perfectly!")
        else:
            print(f"Object creation failed: {result.get('message')}")
            
    except ConnectionRefusedError:
        print("FAILED: Cannot connect to Fusion 360")
        print("Make sure:")
        print("1. Fusion 360 is running")
        print("2. MCP add-in is loaded (Shift+S > Add-Ins > Fusion360MCP > Run)")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == '__main__':
    quick_test()
