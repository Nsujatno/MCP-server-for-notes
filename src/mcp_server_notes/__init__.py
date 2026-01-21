from .server import mcp

def main():
    """Main entry point for the MCP server."""
    mcp.run(transport="stdio")

__all__ = ["main", "mcp"]
