#!/usr/bin/env python3
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
    box_pattern = r'(?:create|make)\s+box\s+(\d+)\s+(\d+)\s+(\d+)'
    box_match = re.search(box_pattern, text)
    if box_match:
        return {
            'action': 'create_box',
            'width': int(box_match.group(1)),
            'height': int(box_match.group(2)),
            'depth': int(box_match.group(3))
        }
    
    # Cylinder creation: "create cylinder 30 80" or "make cylinder radius 30 height 80"
    cyl_pattern1 = r'(?:create|make)\s+cylinder\s+(\d+)\s+(\d+)'
    cyl_pattern2 = r'(?:create|make)\s+cylinder\s+radius\s+(\d+)\s+height\s+(\d+)'
    
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
            result = f"Design contains {bodies_info['bodies_count']} bodies\n"
            result += f"Total volume: {bodies_info['total_volume_cm3']} cm³\n"
            for body in bodies_info['bodies']:
                result += f"  - {body['name']}: {body['volume_cm3']} cm³\n"
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
