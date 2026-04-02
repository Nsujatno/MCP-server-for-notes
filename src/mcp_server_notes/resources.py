from .mcp_instance import mcp
from .config import VAULT_PATH, ensure_path


@mcp.resource("obsidian://{note_name}")
def get_note(note_name: str) -> str:
    """
    Gets a note based on a specific file.
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
