from mcp.server.fastmcp import FastMCP
import os
from pathlib import Path
from dotenv import load_dotenv

# env setup
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

VAULT_PATH_STR = os.getenv("OBSIDIAN_VAULT_PATH")

if not VAULT_PATH_STR:
    raise ValueError("OBSIDIAN_VAULT_PATH not found in .env file")
    
VAULT_PATH = Path(VAULT_PATH_STR)

# Create an MCP server
mcp = FastMCP("Notes", json_response=True)

def ensure_path():
    if not VAULT_PATH.exists():
        raise RuntimeError(f"The vault at {VAULT_PATH} does not exist")
    return VAULT_PATH

# create resource to access notes
@mcp.resource("obsidian://{note_name}")
def get_note(note_name: str) -> str:
    """
    Gets a note based on a specific file
    Args:
        note_name: The name of the note
    """
    ensure_path()
    if not note_name.endswith(".md"):
        note_name += ".md"
    
    note_path = VAULT_PATH / note_name

    if not note_path.is_relative_to(VAULT_PATH):
        raise ValueError("Access denied: Path outside vault")
        
    if not note_path.exists():
        return "Note not found."
        
    return note_path.read_text(encoding="utf-8")

@mcp.tool()
def create_note(filename: str, content: str) -> str:
    """
    Creates a new markdown note in the vault.
    
    Args:
        filename: The name of the file
        content: The text body to write into the file
    """
    try:
        ensure_path()
        
        if not filename.endswith(".md"):
            filename += ".md"

        note_path = VAULT_PATH / filename

        if note_path.exists():
            return f"Error: A note named '{filename}' already exists."
        
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"Successfully created note: {filename}"

    except Exception as e:
        return f"Error creating note: {str(e)}"

@mcp.prompt()
def organize_notes(filename: str, raw_notes: str) -> str:
    """
    Takes raw, messy text (brain dump) and asks the AI to format it 
    into a clean Markdown note and save it to the vault.
    """
    return f"""
I have some raw notes that I need formatted and saved. 

Please perform the following steps:
1. Analyze the raw text below.
2. Reformat it into clean Markdown. Use headers (##), bullet points, bold text for key terms, use $$ for math equations, and use `` for any code blocks.
3. Summarize the main points at the very top.
4. Call the 'create_note' tool to save this content to my vault with filename: "{filename}" and the content: the formatted markdown.

Here are the raw notes:
{raw_notes}
"""

# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")