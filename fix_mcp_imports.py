#!/usr/bin/env python3
"""
Fix MCP module imports
"""

def fix_mcp_tools():
    tools_file = "/mnt/c/Users/rooma/PycharmProjects/neo_alexadria/backend/app/modules/mcp/tools.py"
    
    with open(tools_file, 'r') as f:
        content = f.read()
    
    # Fix all backend imports
    replacements = [
        ("from backend.app.modules.search.service import SearchService", "from ..search.service import SearchService"),
        ("from backend.app.shared.database import get_db", "from ...shared.database import get_sync_db"),
        ("from backend.app.modules.graph.router import get_hover_information", "from ..graph.router import get_hover_information"),
        ("from backend.app.modules.graph.service import GraphService", "from ..graph.service import GraphService"),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(tools_file, 'w') as f:
        f.write(content)
    
    print("✅ Fixed MCP tools imports")

if __name__ == "__main__":
    fix_mcp_tools()
