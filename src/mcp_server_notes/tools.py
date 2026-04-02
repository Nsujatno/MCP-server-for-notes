from .mcp_instance import mcp
from .config import VAULT_PATH, ensure_path
from .models import BulkUpdate
import json


@mcp.tool()
def get_notes_batch(filenames: list[str]) -> str:
    """
    Reads multiple notes from the vault in a single tool call.
    Returns a JSON mapping of filename to its content.

    Args:
        filenames: A list of note names (with or without .md extension)
    """
    ensure_path()
    results = {}

    for name in filenames:
        original_name = name
        if not name.endswith(".md"):
            name += ".md"

        note_path = VAULT_PATH / name

        if not note_path.is_relative_to(VAULT_PATH):
            results[original_name] = "Error: Access denied — path is outside the vault."
            continue

        if not note_path.exists():
            results[original_name] = f"Error: Note '{name}' not found."
            continue

        try:
            results[original_name] = note_path.read_text(encoding="utf-8")
        except Exception as e:
            results[original_name] = f"Error reading note: {str(e)}"

    return json.dumps(results, indent=2)


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
def overwrite_note(filename: str, content: str) -> str:
    """
    Creates or overwrites a markdown note in the vault.
    Use this when you need to replace an existing file entirely (e.g. regenerating a snapshot).

    Args:
        filename: The name of the file (with or without .md extension)
        content: The full text body to write into the file
    """
    try:
        ensure_path()

        if not filename.endswith(".md"):
            filename += ".md"

        note_path = VAULT_PATH / filename

        if not note_path.is_relative_to(VAULT_PATH):
            return "Error: Access denied — path is outside the vault."

        note_path.parent.mkdir(parents=True, exist_ok=True)

        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)

        action = "Overwrote" if note_path.exists() else "Created"
        return f"{action} note: {filename}"

    except Exception as e:
        return f"Error writing note: {str(e)}"


@mcp.tool()
def update_notes_bulk(bulk_update: BulkUpdate) -> str:
    """
    Performs multiple file operations (create, append, overwrite) in a single tool call.
    Useful for saving multiple nuggets or updating the index together.

    Args:
        bulk_update: A collection of file updates (filename, content, type)
    """
    ensure_path()
    results = []

    for update in bulk_update.updates:
        filename = update.filename
        content = update.content
        update_type = update.type

        if not filename or content is None:
            results.append(f"Skipping update: missing filename or content.")
            continue

        if not filename.endswith(".md"):
            filename += ".md"

        note_path = VAULT_PATH / filename

        if not note_path.is_relative_to(VAULT_PATH):
            results.append(f"Error for '{filename}': Access denied.")
            continue

        try:
            note_path.parent.mkdir(parents=True, exist_ok=True)

            if update_type == "create":
                if note_path.exists():
                    results.append(f"Error for '{filename}': Use 'overwrite' to replace existing file.")
                else:
                    note_path.write_text(content, encoding="utf-8")
                    results.append(f"Created note: {filename}")
            elif update_type == "overwrite":
                action = "Overwrote" if note_path.exists() else "Created"
                note_path.write_text(content, encoding="utf-8")
                results.append(f"{action} note: {filename}")
            elif update_type == "append":
                if not note_path.exists():
                    note_path.write_text(content, encoding="utf-8")
                    results.append(f"Created note (append-mode): {filename}")
                else:
                    with open(note_path, "a", encoding="utf-8") as f:
                        f.write("\n" + content)
                    results.append(f"Appended to note: {filename}")
            else:
                results.append(f"Error for '{filename}': Invalid update_type '{update_type}'.")
        except Exception as e:
            results.append(f"Error for '{filename}': {str(e)}")

    return "\n".join(results)


@mcp.tool()
def search_notes(query: str, folder: str = ".") -> str:
    """
    Searches notes based on a specific query string.

    Args:
        query: The search term to look for
        folder: Optional folder to scope the search (relative to vault root). Defaults to entire vault.
    """
    ensure_path()
    search_dir = VAULT_PATH / folder
    if not search_dir.exists():
        return "Folder not found."
    matches = []
    for path in search_dir.rglob("*.md"):
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
def list_notes_recursive(folder: str = ".") -> str:
    """
    Lists all markdown files under a folder recursively with their modification times.
    Returns a JSON string containing a list of objects with 'path' and 'mtime'.
    Skips the templates/ directory.

    Args:
        folder: The folder to search (relative to vault root). Defaults to entire vault.
    """
    ensure_path()
    target_dir = VAULT_PATH / folder
    if not target_dir.exists():
        return "Folder not found."

    notes = []
    for path in sorted(target_dir.rglob("*.md")):
        # Skip anything inside a templates/ directory
        if "templates" in [p.lower() for p in path.parts]:
            continue
        
        rel_path = str(path.relative_to(VAULT_PATH))
        mtime = path.stat().st_mtime
        notes.append({"path": rel_path, "mtime": mtime})

    return json.dumps(notes, indent=2)


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
