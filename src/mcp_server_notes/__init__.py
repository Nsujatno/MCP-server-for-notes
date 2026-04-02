from .mcp_instance import mcp
from . import server  # noqa: F401 — triggers resource/tool/prompt registration

def main():
    """Main entry point for the MCP server."""
    mcp.run(transport="stdio")

__all__ = ["main", "mcp"]
