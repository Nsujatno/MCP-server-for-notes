from mcp.server.fastmcp import FastMCP

# Shared MCP instance — imported by all modules
mcp = FastMCP("Notes", json_response=True)
