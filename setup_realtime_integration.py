"""
Fusion 360 MCP Real-Time Integration Setup

This script sets up the complete real-time integration between Fusion 360 and 
external applications through the MCP protocol.
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path

def get_fusion360_addon_path():
    """Get the Fusion 360 add-ins directory path."""
    if sys.platform == "win32":
        return os.path.expanduser(r"~\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns")
    else:
        return os.path.expanduser("~/.config/Autodesk/Autodesk Fusion 360/API/AddIns")

def check_fusion360_running():
    """Check if Fusion 360 is currently running."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            return 'Fusion360.exe' in result.stdout
        else:
            # For macOS/Linux, this would need different commands
            return False
    except:
        return False

def install_addon():
    """Install the Fusion 360 MCP add-in."""
    print("Installing Fusion 360 MCP Add-in...")
    
    # Get paths
    script_dir = Path(__file__).parent
    addon_source = script_dir / "fusion360_addon"
    addon_dest = Path(get_fusion360_addon_path()) / "Fusion360MCP"
    
    try:
        # Create destination directory
        addon_dest.mkdir(parents=True, exist_ok=True)
        
        # Copy add-in files
        if (addon_source / "Fusion360MCP.py").exists():
            shutil.copy2(addon_source / "Fusion360MCP.py", addon_dest / "Fusion360MCP.py")
            print(f"SUCCESS: Copied Python file to {addon_dest}")
        else:
            print(f"ERROR: Source file not found: {addon_source / 'Fusion360MCP.py'}")
            return False
        
        if (addon_source / "Fusion360MCP.manifest").exists():
            shutil.copy2(addon_source / "Fusion360MCP.manifest", addon_dest / "Fusion360MCP.manifest")
            print(f"SUCCESS: Copied manifest file to {addon_dest}")
        else:
            print(f"ERROR: Manifest file not found: {addon_source / 'Fusion360MCP.manifest'}")
            return False
        
        print("SUCCESS: Add-in installation completed")
        return True
        
    except Exception as e:
        print(f"ERROR: Add-in installation failed: {str(e)}")
        return False

def check_python_dependencies():
    """Check if required Python dependencies are available."""
    print("Checking Python dependencies...")
    
    try:
        import socket
        import json
        import threading
        print("SUCCESS: All required Python modules are available")
        return True
    except ImportError as e:
        print(f"ERROR: Missing Python module: {str(e)}")
        return False

def test_installation():
    """Test if the installation is working."""
    print("Testing installation...")
    
    # Import test module
    try:
        test_script = Path(__file__).parent / "tests" / "test_realtime_integration.py"
        if test_script.exists():
            print("SUCCESS: Test script found")
            
            # Check if Fusion 360 is running
            if check_fusion360_running():
                print("SUCCESS: Fusion 360 is running")
                print("To complete testing:")
                print("1. In Fusion 360, press Shift+S")
                print("2. Go to Add-Ins tab")
                print("3. Find 'Fusion360MCP' and click Run")
                print("4. After loading, run: python tests/test_realtime_integration.py")
            else:
                print("WARNING: Fusion 360 is not running")
                print("To test:")
                print("1. Start Fusion 360")
                print("2. Load the MCP add-in (Shift+S > Add-Ins > Fusion360MCP > Run)")
                print("3. Run: python tests/test_realtime_integration.py")
            
            return True
        else:
            print(f"ERROR: Test script not found: {test_script}")
            return False
            
    except Exception as e:
        print(f"ERROR: Test setup failed: {str(e)}")
        return False

def create_quick_test():
    """Create a quick test script for immediate verification."""
    print("Creating quick test script...")
    
    test_content = '''"""
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
        print("\\nTesting object creation...")
        
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
            print("\\nReal-time control is working perfectly!")
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
'''
    
    try:
        quick_test_path = Path(__file__).parent / "quick_test.py"
        with open(quick_test_path, 'w') as f:
            f.write(test_content)
        print(f"SUCCESS: Quick test created: {quick_test_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create quick test: {str(e)}")
        return False

def setup_realtime_integration():
    """Main setup function."""
    print("FUSION 360 MCP REAL-TIME INTEGRATION SETUP")
    print("=" * 50)
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Check dependencies
    if check_python_dependencies():
        success_count += 1
    
    # Step 2: Install add-in
    if install_addon():
        success_count += 1
    
    # Step 3: Create quick test
    if create_quick_test():
        success_count += 1
    
    # Step 4: Test installation
    if test_installation():
        success_count += 1
    
    # Results
    print("\n" + "=" * 50)
    print("SETUP RESULTS")
    print(f"Steps completed: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("SETUP COMPLETED SUCCESSFULLY!")
        print("\nNEXT STEPS:")
        print("1. Start Fusion 360 (if not already running)")
        print("2. Press Shift+S to open Scripts and Add-Ins")
        print("3. Click 'Add-Ins' tab")
        print("4. Find 'Fusion360MCP' and click 'Run'")
        print("5. Wait for confirmation dialog")
        print("6. Run 'python quick_test.py' to verify")
        print("\nAfter setup, you can control Fusion 360 in real-time!")
        
        return True
    else:
        print("SETUP INCOMPLETE")
        print("Please check the error messages above")
        return False

if __name__ == '__main__':
    setup_realtime_integration()
