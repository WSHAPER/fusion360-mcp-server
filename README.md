# Fusion 360 MCP Server

A Model Context Protocol (MCP) server that interfaces between Claude and Autodesk Fusion 360. This server provides two powerful modes of operation:

1. **MCP Mode**: Generate Fusion 360 scripts through Claude Desktop
2. **Real-Time Control**: Chat-based live control of Fusion 360

## 🧠 Overview

This project allows you to:
- Parse natural language prompts (e.g., "Make a box with rounded corners")
- Resolve them into Fusion tool actions (e.g., CreateSketch → DrawRectangle → Extrude → Fillet)
- Generate Python scripts for Fusion 360 execution
- **NEW**: Control Fusion 360 in real-time through chat commands

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- Autodesk Fusion 360

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/fusion360-mcp-server.git
   cd fusion360-mcp-server
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Complete Installation (Recommended)

Install everything with one command:

```bash
python setup_complete.py
```

This installs:
- MCP server configuration for Claude Desktop
- Real-time control add-in for Fusion 360
- Chat interface for natural language commands

### Alternative: Individual Components

**Real-time control only:**
```bash
python setup_complete.py --realtime-only
```

**MCP configuration only:**
```bash
python setup_complete.py --mcp-only
```

### Getting Started

After installation:
1. **Restart Claude Desktop** (for MCP integration)
2. **Start Fusion 360** (add-in loads automatically)
3. **Run the chat interface**: `python chat_interface.py`
4. **Try commands**: `create box 100 50 25`

## 💬 Real-Time Chat Control

### Chat Commands

Once installed, you can control Fusion 360 with natural language:

```
💬 Enter command: create box 200 100 50
✅ Created box: 200x100x50mm

💬 Enter command: make cylinder radius 35 height 90
✅ Created cylinder: radius 35mm, height 90mm

💬 Enter command: list bodies
📊 Design contains 2 bodies
📐 Total volume: 2403.33 cm³
  • Box: 1000.00 cm³
  • Cylinder: 1403.33 cm³
```

### Supported Chat Commands

- `create box 100 50 25` - Creates a box (width × height × depth in mm)
- `make cylinder radius 30 height 80` - Creates a cylinder
- `show document` - Get current document information
- `list bodies` - Show all bodies and their volumes

## 🔌 MCP Integration

To use this server with Claude Desktop, add it to your MCP configuration:

**Windows**: `C:\Users\[username]\AppData\Roaming\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fusion360": {
      "command": "python",
      "args": ["C:\\path\\to\\fusion360-mcp-server\\src\\main.py", "--mcp"]
    }
  }
}
```

## 📦 Available Tools

### Create
- **CreateSketch**: Creates a new sketch on a specified plane
- **DrawRectangle**: Draws a rectangle in the active sketch
- **DrawCircle**: Draws a circle in the active sketch
- **Extrude**: Extrudes a profile into a 3D body
- **Revolve**: Revolves a profile around an axis

### Modify
- **Fillet**: Adds a fillet to selected edges
- **Chamfer**: Adds a chamfer to selected edges
- **Shell**: Hollows out a solid body with a specified wall thickness
- **Combine**: Combines two bodies using boolean operations

### Export
- **ExportBody**: Exports a body to a file

## 🎯 Usage Examples

### MCP Mode (Script Generation)

```bash
# Start the HTTP server
cd src
python main.py

# Call tools via API
curl -X POST http://127.0.0.1:8000/call_tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool_calls": [
      {
        "tool_name": "CreateSketch",
        "parameters": {"plane": "xy"}
      },
      {
        "tool_name": "DrawRectangle",
        "parameters": {"width": 10, "depth": 10}
      },
      {
        "tool_name": "Extrude",
        "parameters": {"height": 5}
      }
    ]
  }'
```

### Real-Time Mode

```bash
# Start the chat interface
python chat_interface.py

# Use natural language commands
create box 150 100 75
make cylinder radius 25 height 50
show document
list bodies
```

## 🧩 Architecture

The system consists of three main components:

1. **MCP Server** (`src/main.py`) - Generates Fusion 360 scripts
2. **Real-Time Add-in** - Socket server running inside Fusion 360
3. **Chat Interface** - Natural language command processor

```
Claude Desktop ←→ MCP Server ←→ Generated Scripts
     ↓
Chat Interface ←→ Socket ←→ Fusion 360 Add-in ←→ Live Control
```

## 🛠️ Troubleshooting

### Real-Time Control Issues

**Add-in not loading:**
1. Check Fusion 360: Tools → Add-Ins → Scripts and Add-Ins
2. Manually add the add-in if needed
3. Restart Fusion 360

**Connection fails:**
1. Ensure Fusion 360 is running
2. Check that the add-in loaded successfully
3. Verify port 9999 is not blocked

### MCP Issues

**Claude Desktop not recognizing server:**
1. Check the JSON syntax in config file
2. Verify the path to `main.py` is correct
3. Restart Claude Desktop

## 📝 Generated Scripts

The MCP server generates executable Fusion 360 Python scripts:

```python
import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        
        # Generated tool calls here...
        
        ui.messageBox('Operation completed successfully')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
```

## 🧪 Extending the System

### Adding New Tools

1. Add tool definition to `src/tool_registry.json`
2. Add script template to `src/script_generator.py`
3. Add real-time command to the add-in

### Adding Chat Commands

1. Extend `parse_chat_command()` in `chat_interface.py`
2. Add corresponding function to the Fusion 360 add-in
3. Update the command help text

## 📚 Documentation Links

- [Fusion 360 API Docs](https://help.autodesk.com/view/fusion360/ENU/)
- [Python API Class Reference](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-4190E5AD-BE6F-4682-A6D1-67D944D3DD58)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)

## 🎉 What's New

- **Real-time chat control** - Control Fusion 360 live through natural language
- **Automatic installation** - One-click setup with `install_realtime.py`
- **Socket-based communication** - Low-latency commands to Fusion 360
- **Natural language parsing** - Human-friendly command interface
- **Volume tracking** - Automatic calculation of model volumes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
