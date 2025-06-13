"""
Fusion 360 Real-Time Integration Test

This script tests the complete real-time integration between external applications
and Fusion 360 through the MCP add-in.
"""

import socket
import json
import time
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_connection():
    """Test basic connection to Fusion 360."""
    print("=== Testing Fusion 360 Real-Time Connection ===")
    print()
    
    try:
        # Test connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect(('127.0.0.1', 9999))
        
        # Send status command
        command = {'type': 'get_server_status'}
        client_socket.send(json.dumps(command).encode('utf-8'))
        
        # Get response
        response = client_socket.recv(4096)
        result = json.loads(response.decode('utf-8'))
        
        client_socket.close()
        
        print("✅ SUCCESS: Connected to Fusion 360!")
        print(f"📊 Server Status: {result}")
        return True
        
    except ConnectionRefusedError:
        print("❌ FAILED: Cannot connect to Fusion 360 MCP server")
        print("\nTo fix this:")
        print("1. Open Fusion 360")
        print("2. Press Shift+S (Scripts and Add-Ins)")
        print("3. Click Add-Ins tab")
        print("4. Find 'Fusion360MCP' and click Run")
        print("5. Wait for confirmation dialog")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: Connection failed: {str(e)}")
        return False

def test_object_creation():
    """Test creating objects in Fusion 360."""
    print("\n=== Testing Object Creation ===")
    
    try:
        # Test creating a box
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect(('127.0.0.1', 9999))
        
        box_command = {
            'type': 'create_object',
            'object_type': 'box',
            'parameters': {'width': 100, 'height': 60, 'depth': 40}
        }
        
        client_socket.send(json.dumps(box_command).encode('utf-8'))
        response = client_socket.recv(4096)
        result = json.loads(response.decode('utf-8'))
        
        client_socket.close()
        
        if result.get('status') == 'success':
            print("✅ Box creation: SUCCESS")
            print(f"📦 Created: {result.get('message')}")
            print(f"🧊 Body: {result.get('data', {}).get('body_name')}")
            print(f"📏 Volume: {result.get('data', {}).get('volume', 0):.2f} cm³")
            
            # Test creating a cylinder
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)
            client_socket.connect(('127.0.0.1', 9999))
            
            cylinder_command = {
                'type': 'create_object',
                'object_type': 'cylinder',
                'parameters': {'radius': 30, 'height': 80}
            }
            
            client_socket.send(json.dumps(cylinder_command).encode('utf-8'))
            response = client_socket.recv(4096)
            result = json.loads(response.decode('utf-8'))
            
            client_socket.close()
            
            if result.get('status') == 'success':
                print("✅ Cylinder creation: SUCCESS")
                print(f"🔵 Created: {result.get('message')}")
                print(f"📏 Volume: {result.get('data', {}).get('volume', 0):.2f} cm³")
                return True
            else:
                print(f"❌ Cylinder creation failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Box creation failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Object creation error: {str(e)}")
        return False

def test_model_info():
    """Test getting model information."""
    print("\n=== Testing Model Information Retrieval ===")
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect(('127.0.0.1', 9999))
        
        command = {'type': 'get_model_info'}
        client_socket.send(json.dumps(command).encode('utf-8'))
        
        response = client_socket.recv(8192)
        result = json.loads(response.decode('utf-8'))
        
        client_socket.close()
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            bodies = data.get('bodies', [])
            sketches = data.get('sketches', [])
            
            print("✅ Model info retrieval: SUCCESS")
            print(f"📄 Document: {data.get('document')}")
            print(f"🧊 Bodies: {len(bodies)}")
            print(f"✏️  Sketches: {len(sketches)}")
            
            if bodies:
                total_volume = sum(body.get('volume', 0) for body in bodies)
                print(f"📊 Total volume: {total_volume:.2f} cm³")
                
                print("\nBodies in model:")
                for i, body in enumerate(bodies, 1):
                    print(f"  {i}. {body.get('name')} - {body.get('volume', 0):.2f} cm³")
            
            return True
        else:
            print(f"❌ Model info failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Model info error: {str(e)}")
        return False

def test_mcp_tools():
    """Test MCP tools integration."""
    print("\n=== Testing MCP Tools Integration ===")
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect(('127.0.0.1', 9999))
        
        command = {'type': 'list_mcp_tools'}
        client_socket.send(json.dumps(command).encode('utf-8'))
        
        response = client_socket.recv(8192)
        result = json.loads(response.decode('utf-8'))
        
        client_socket.close()
        
        if result.get('status') == 'success':
            tools = result.get('data', {}).get('tools', [])
            print("✅ MCP tools listing: SUCCESS")
            print(f"🛠️  Available tools: {len(tools)}")
            
            if tools:
                print("\nMCP Tools:")
                for tool in tools[:5]:  # Show first 5
                    print(f"  - {tool.get('name')}: {tool.get('description')}")
                
                if len(tools) > 5:
                    print(f"  ... and {len(tools) - 5} more tools")
            
            return True
        else:
            print(f"❌ MCP tools failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ MCP tools error: {str(e)}")
        return False

def run_complete_test():
    """Run the complete integration test suite."""
    print("🧪 FUSION 360 REAL-TIME INTEGRATION TEST SUITE")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Connection
    if test_connection():
        tests_passed += 1
    
    # Test 2: Object Creation
    if test_object_creation():
        tests_passed += 1
    
    # Test 3: Model Info
    if test_model_info():
        tests_passed += 1
    
    # Test 4: MCP Tools
    if test_mcp_tools():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print("🧪 TEST RESULTS")
    print(f"📊 Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Fusion 360 real-time integration is working perfectly!")
        print("💬 You can now control Fusion 360 from chat commands!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("🔧 Check the error messages above for troubleshooting")
    
    return tests_passed == total_tests

if __name__ == '__main__':
    run_complete_test()
