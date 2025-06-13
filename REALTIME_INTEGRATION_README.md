# Fusion 360 Real-Time Chat Control Integration

This integration enables real-time control of Fusion 360 from external applications, including chat interfaces like Claude Desktop. You can create 3D objects, execute parametric operations, and query model information using natural language commands.

## 🚀 Quick Start

### 1. Setup Installation
```bash
# Run the automated setup script
python setup_realtime_integration.py
```

### 2. Load Add-in in Fusion 360
1. Start Fusion 360
2. Press `Shift+S` (Scripts and Add-Ins dialog)
3. Click **"Add-Ins"** tab
4. Find **"Fusion360MCP"** in the list
5. Click **"Run"** button
6. Wait for confirmation: *"Fusion 360 MCP Integration loaded successfully!"*

### 3. Test Connection
```bash
# Run quick test to verify integration
python quick_test.py
```

**Expected Result**: 
```
SUCCESS: Connected to Fusion 360!
SUCCESS: Object creation works!
Real-time control is working perfectly!
```

## 💬 Chat Commands

Once the integration is active, you can control Fusion 360 using these commands:

### Object Creation
- **"Create a box 100x60x40"** → Creates box with specified dimensions (mm)
- **"Make a cylinder radius 30 height 80"** → Creates cylinder
- **"Create small box 50x50x25"** → Creates smaller box

### Information Queries  
- **"Get current document info"** → Document name, body count, etc.
- **"Show model details"** → List all bodies with volumes
- **"How many objects in the model?"** → Object count and total volume

### MCP Tools
- **"List available tools"** → Shows all parametric modeling tools
- **"Create sketch on XY plane"** → Uses MCP CreateSketch tool
- **"Draw rectangle 100x60"** → Uses MCP DrawRectangle tool
- **"Extrude 25mm"** → Uses MCP Extrude tool

## 🔧 API Reference

### Python Client Interface

```python
from src.fusion360_client import Fusion360Client

# Connect to Fusion 360
client = Fusion360Client()
client.connect()

# Create objects
result = client.create_box(width=100, height=60, depth=40)
result = client.create_cylinder(radius=30, height=80)

# Get information
doc_info = client.get_document_info()
model_info = client.get_model_info()

# Execute MCP tools
result = client.execute_mcp_tool('CreateSketch', {'plane': 'xy'})
tools = client.list_mcp_tools()

client.disconnect()
```

### Direct Socket Communication

```python
import socket
import json

# Connect to Fusion 360
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9999))

# Create box command
command = {
    'type': 'create_object',
    'object_type': 'box',
    'parameters': {'width': 100, 'height': 60, 'depth': 40}
}

# Send command and get response
client.send(json.dumps(command).encode('utf-8'))
response = json.loads(client.recv(4096).decode('utf-8'))

client.close()
```

## 🛠️ Available Commands

### Document Commands
- `get_document_info` → Document name, save status, units, counts
- `get_model_info` → Detailed body and sketch information

### Object Creation Commands
- `create_object` with `object_type: 'box'` → Box creation
- `create_object` with `object_type: 'cylinder'` → Cylinder creation

### MCP Tool Commands  
- `list_mcp_tools` → List all available parametric tools
- `execute_mcp_tool` → Execute specific MCP tool with parameters

### Status Commands
- `get_server_status` → Server health and availability

## 📁 File Structure

```
fusion360-mcp-server/
├── fusion360_addon/          # Fusion 360 add-in files
│   ├── Fusion360MCP.py      # Main add-in with socket server
│   └── Fusion360MCP.manifest # Add-in metadata
├── src/
│   ├── fusion360_client.py  # Python client interface
│   ├── main.py             # Original MCP server
│   └── script_generator.py # MCP tool definitions
├── tests/
│   └── test_realtime_integration.py # Comprehensive tests
├── setup_realtime_integration.py    # Automated setup
└── quick_test.py                    # Quick verification test
```

## 🔍 Troubleshooting

### Connection Refused Error
```
❌ FAILED: Cannot connect to Fusion 360 MCP server
```
**Solution**: 
1. Ensure Fusion 360 is running
2. Load the MCP add-in: `Shift+S` → Add-Ins → Fusion360MCP → Run
3. Check for error messages in Fusion 360's Text Commands window

### Add-in Not Found
```
❌ Add-in 'Fusion360MCP' not found in Fusion 360
```
**Solution**:
1. Run `python setup_realtime_integration.py` again
2. Check add-in installation path:
   - Windows: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\Fusion360MCP\`
   - macOS: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Fusion360MCP/`

### Object Creation Fails
```
❌ Object creation failed: No active document
```
**Solution**:
1. Create or open a document in Fusion 360
2. Ensure you're in the Design workspace
3. Try the command again

### MCP Tools Not Available  
```
❌ MCP tools not available
```
**Solution**:
1. Check that `script_generator.py` exists in the `src/` directory
2. Verify the path in the add-in matches your installation
3. Restart Fusion 360 and reload the add-in

## 🧪 Testing

### Run Complete Test Suite
```bash
python tests/test_realtime_integration.py
```

### Manual Testing Steps
1. **Test Connection**: `python quick_test.py`
2. **Test Object Creation**: Create box and cylinder via API
3. **Test Information Retrieval**: Get document and model info  
4. **Test MCP Integration**: List and execute MCP tools

## 🔌 Integration with Claude Desktop

This system integrates seamlessly with Claude Desktop's MCP protocol:

1. **MCP Server**: Generates Fusion 360 scripts from natural language
2. **Real-Time Add-in**: Executes commands directly in Fusion 360
3. **Chat Interface**: Enables conversational 3D modeling

### Example Workflow
```
You: "Create a box 200mm wide, 100mm deep, 50mm tall"
    ↓
Claude Desktop MCP → Fusion 360 Add-in → Real-time object creation
    ↓
3D box appears in Fusion 360 immediately
```

## 📋 System Requirements

- **Fusion 360**: 2020 or later
- **Python**: 3.6 or later  
- **Operating System**: Windows, macOS, or Linux
- **Network**: Local socket communication (127.0.0.1:9999)

## 🎯 Use Cases

- **Conversational CAD**: Design 3D models through natural language
- **Automation**: Batch create objects with varying parameters
- **Educational**: Learn 3D modeling through interactive commands
- **Prototyping**: Rapidly iterate designs via chat interface
- **Integration**: Connect Fusion 360 to external design workflows

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/improvement`
3. Test your changes with the provided test suite
4. Submit pull request with description of changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

🎉 **Congratulations!** You now have real-time chat control of Fusion 360. Design 3D models through conversation and watch them appear instantly in Fusion 360!
