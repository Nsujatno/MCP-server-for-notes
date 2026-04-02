from .mcp_instance import mcp
from .config import VAULT_PATH, ensure_path


@mcp.tool()
def get_note(note_name: str) -> str:
    """
    Reads and returns the contents of a note from the vault.

    Args:
        note_name: The name of the note (with or without .md extension)
    """
    ensure_path()
    if not note_name.endswith(".md"):
        note_name += ".md"

    note_path = VAULT_PATH / note_name

    if not note_path.is_relative_to(VAULT_PATH):
        return "Error: Access denied — path is outside the vault."

    if not note_path.exists():
        return f"Error: Note '{note_name}' not found."

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

        note_path.parent.mkdir(parents=True, exist_ok=True)

        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully created note: {filename}"

    except Exception as e:
        return f"Error creating note: {str(e)}"


@mcp.tool()
def search_notes(query: str) -> str:
    """
    Searches notes based on a specific query string.
    """
    ensure_path()
    matches = []
    for path in VAULT_PATH.rglob("*.md"):
        try:
            if query.lower() in path.read_text(encoding="utf-8").lower():
                matches.append(str(path.relative_to(VAULT_PATH)))
        except Exception:
            continue
    return "\n".join(matches) if matches else "No matches found."


@mcp.tool()
def list_notes(folder: str = ".") -> str:
    """
    Lists all note files in a folder.
    """
    ensure_path()
    target_dir = VAULT_PATH / folder
    if not target_dir.exists():
        return "Folder not found."

    files = []
    for p in target_dir.iterdir():
        if p.is_dir():
            files.append(f"[DIR] {p.name}")
        elif p.suffix == ".md":
            files.append(p.name)

    return "\n".join(sorted(files))


@mcp.tool()
def append_to_note(filename: str, content: str) -> str:
    """
    Adds text to the end of an existing note.
    """
    ensure_path()
    if not filename.endswith(".md"):
        filename += ".md"
    note_path = VAULT_PATH / filename

    if not note_path.exists():
        return "Note doesn't exist"

    with open(note_path, "a", encoding="utf-8") as f:
        f.write("\n" + content)
    return f"Appended to {filename}"
