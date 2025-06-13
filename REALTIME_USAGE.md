# Fusion 360 Real-Time Control Usage

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
3. Navigate to: `C:\Users\admin\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns\Fusion360MCP`
4. Select the Fusion360MCP folder

## Integration with MCP

This real-time control system works alongside the MCP server. You can:
1. Use Claude Desktop with MCP for script generation
2. Use the chat interface for real-time control
3. Combine both approaches for maximum flexibility

Happy 3D modeling!
