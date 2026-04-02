# Obsidian Brain Dump & Context MCP

A modular MCP (Model Context Protocol) server connecting Claude to your Obsidian vault. 
What started as a simple script to automatically organize messy class notes has evolved into a full **Vault Brain** system. It turns your Obsidian notes into a persistent, provider-agnostic AI context layer.

## Core Features

- **Read & Write Vault Notes**: Give Claude native access to read, append, search, and overwrite any notes in your vault.
- **Bulk & Batch Operations**: Uses optimized `BulkUpdate` tools and batch-reading functions to perform operations efficiently, massively reducing UI latency and API token usage.
- **Seamless Incremental Indexing**: Uses native modification timestamps (`MTime`) inside a lightweight `_index.md` file. Claude syncs changes efficiently without constantly re-reading your entire vault.
- **Synthesis Engine**: Distills chat sessions into atomic knowledge nuggets and generates a portable `AI_CONTEXT.md` file designed to bootstrap cross-AI workflows securely without manual copy-pasting.

## The "Second Brain" Workflow & Prompts
The server provides specialized prompts (accessible via the Claude Desktop attachment menu) to automate your note-taking lifecycle.

1. **`organize_notes`**
   - **Use case**: Cleaning up messy, unstructured text.
   - **What it does**: Takes raw text, reformats it into clean Markdown (with headers, bullet points, and even Mermaid.js diagrams), and saves it directly to a file in your vault.
2. **`distill_session`**
   - **Use case**: Run this at the end of a long brainstorming session. 
   - **What it does**: Harvests atomic "knowledge nuggets" from the conversation, presents you with a dry-run preview, and bulk-saves the approved facts directly into your second brain directory while updating `_index.md`.
3. **`rebuild_index`**
   - **Use case**: Run this after you've manually edited files in your Obsidian vault.
   - **What it does**: Performs a smart increment scan. It compares disk file timestamps against the internal `_index.md`, pulling in and summarizing only the files that changed. 
4. **`generate_context_snapshot`**
   - **Use case**: Run this periodically to synthesize your vault's state.
   - **What it does**: Compiles a concise `AI_CONTEXT.md` file representing Who You Are, Active Projects, Priorities, and Recent Decisions. This artifact can be safely pasted cold into ChatGPT, Gemini, or new Claude sessions so you never have to re-explain yourself.

## Server Architecture
Built using standard Python tooling and `mcp` libraries, the codebase is modularized:
- **`mcp_instance.py`**: Central FastMCP initialization.
- **`resources.py`**: Exposes read-only `note://{name}` URIs.
- **`tools.py`**: Exposes utility functions (`get_note`, `search_notes`) and bulk actions (`get_notes_batch`, `update_notes_bulk`).
- **`prompts.py`**: Exposes the logic for the predefined agent workflows (distill, snapshot, rebuild).
- **`models.py`**: Pydantic schemas validating correct bulk-update parameters.

---

## Setup Instructions

### 1. Clone the Repo
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Install Dependencies (via uv)
Because it relies on the modern Python ecosystem, `uv` is heavily recommended for dependency management.
```bash
uv sync
```
*(This automatically creates a virtual environment and installs `mcp`, `python-dotenv`, and other required packages.)*

### 3. Connect your Obsidian Vault
Create a `.env` file in the root of the cloned repository and set your absolute vault path:
```env
OBSIDIAN_VAULT_PATH="C:\Users\YourName\Documents\ObsidianVault"
```

### 4. Add to Claude Desktop
You must register the MCP server with the Claude app configuration. Open the config file:
- **Windows**: `AppData\Roaming\Claude\claude_desktop_config.json`

Add the following entry under `mcpServers`:
```json
{
  "mcpServers": {
    "Notes": {
      "command": "C:\\Users\\YourName\\.local\\bin\\uv.EXE",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\YourName\\mcp_test",
        "python",
        "-m",
        "mcp_server_notes"
      ]
    }
  }
}
```
**CRITICAL**: You *must* update `YourName` in both the `command` and `--directory` argument to point to your absolute UV path and repository clone path, respectively.

### 5. Restart Claude
Fully restart Claude Desktop and now you should see your mcp server running in (+) -> Connectors.