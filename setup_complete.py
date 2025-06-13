#!/usr/bin/env python3
"""
Fusion 360 MCP Complete Setup
============================

This script provides a complete out-of-the-box installation for Fusion 360 MCP integration.
It can install both the MCP server configuration and the real-time control system.

Usage: 
  python setup_complete.py                    # Install everything
  python setup_complete.py --mcp-only         # Only MCP setup
  python setup_complete.py --realtime-only    # Only real-time control
"""

import os
import sys
import json
import argparse
from pathlib import Path

def get_claude_config_path():
    """Get the Claude Desktop configuration file path"""
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"

def get_fusion360_addins_path():
    """Get the Fusion 360 add-ins directory path"""
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "Autodesk" / "Autodesk Fusion 360" / "API" / "AddIns"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Autodesk" / "Autodesk Fusion 360" / "API" / "AddIns"
    else:
        return Path.home() / ".config" / "Autodesk" / "Autodesk Fusion 360" / "API" / "AddIns"

def setup_mcp_configuration():
    """Set up MCP configuration for Claude Desktop"""
    print("Setting up MCP configuration...")
    
    config_path = get_claude_config_path()
    main_py_path = Path(__file__).parent / "src" / "main.py"
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            config = {}
    
    # Add or update the MCP server configuration
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["fusion360"] = {
        "command": "python",
        "args": [str(main_py_path.absolute()), "--mcp"]
    }
    
    # Write the configuration
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"[OK] MCP configuration saved to: {config_path}")
    return True

def setup_realtime_control():
    """Set up real-time control system"""
    print("Setting up real-time control system...")
    
    # Import the installation functions from install_realtime.py
    sys.path.insert(0, str(Path(__file__).parent))
    from install_realtime import (
        create_addon_manifest, create_addon_python, 
        create_chat_interface, create_usage_guide
    )
    
    # Get Fusion 360 add-ins directory
    addins_path = get_fusion360_addins_path()
    addon_dir = addins_path / "Fusion360MCP"
    
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
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Complete Fusion 360 MCP Setup')
    parser.add_argument('--mcp-only', action='store_true', 
                      help='Only set up MCP configuration')
    parser.add_argument('--realtime-only', action='store_true', 
                      help='Only set up real-time control')
    
    args = parser.parse_args()
    
    print("Fusion 360 MCP Complete Setup")
    print("=" * 40)
    
    success = True
    
    if args.mcp_only:
        success = setup_mcp_configuration()
    elif args.realtime_only:
        success = setup_realtime_control()
    else:
        # Install everything
        print("Installing complete Fusion 360 MCP integration...")
        print()
        
        success = setup_mcp_configuration() and setup_realtime_control()
    
    if success:
        print("\nSetup Complete!")
        print()
        
        if not args.realtime_only:
            print("MCP Integration:")
            print("- Restart Claude Desktop to load the MCP server")
            print("- Claude can now generate Fusion 360 scripts")
            print()
        
        if not args.mcp_only:
            print("Real-Time Control:")
            print("1. Start Fusion 360 (add-in loads automatically)")
            print("2. Run: python chat_interface.py")
            print("3. Use commands like 'create box 100 50 25'")
            print()
        
        print("Read REALTIME_USAGE.md for detailed instructions.")
    else:
        print("\nSetup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
