from .mcp_instance import mcp
from .tools import get_note
from datetime import date


@mcp.prompt()
def organize_notes(raw_filename: str, output_filename: str) -> str:
    """
    Takes a filename for raw notes, reads them, and asks the AI to format
    into a clean Markdown note and save it to the output filename.
    """
    raw_notes = get_note(raw_filename)

    return f"""
I have some raw notes from "{raw_filename}" that I need formatted and saved. 

Please perform the following steps:
1. Analyze the raw text below.
2. Reformat it into clean Markdown. Use headers (##), bullet points, bold text for key terms, use $$ for math equations, and use `` for any code blocks.
3. Identify any processes, workflows, hierarchies, or complex relationships in the text. Visualise these using valid Mermaid.js diagrams (e.g., flowcharts, sequence diagrams) enclosed in ```mermaid code blocks.
4. For any links: eg: anything between ![[content]]. it is a link. keep this do not modify it
5. Summarize the main points at the very top.
6. For any parts that say "claude help me", or "claude expand on this", explain more about the information.
7. Call the 'create_note' tool to save this content to my vault with filename: "{output_filename}" and the content: the formatted markdown.

Here are the raw notes from "{raw_filename}":
{raw_notes}
"""


@mcp.prompt()
def distill_session() -> str:
    """
    Harvests curated knowledge nuggets from the current session and writes them
    to the second brain. Shows a dry-run preview before writing anything.
    Scoped strictly to second brain/. Maintains _index.md for efficient future reads.
    """
    today = date.today().isoformat()

    return f"""
Today is {today}. Extract and save the most valuable knowledge from this conversation into my second brain.

## Step 1 — Survey the vault
Call `list_notes_recursive` with folder="second brain" to get the list of files and their modification times (`mtime`).
If "_index.md" exists, call `get_note("second brain/_index")` to understand the current state.

## Step 2 — Extract nuggets from this conversation
Scan the conversation for extractive facts. Do not write to `second brain/AI_CONTEXT.md`.

## Step 3 — Plan writes
For each nugget, decide if you need to `create` (new) or `append` (exists).
Important: For any file you write to, capture the **current disk mtime** from Step 1 (or assume it will update).

## Step 4 — Show dry-run preview
Stop and show the table of intended changes.

## Step 5 — Write approved items
Execute all writes in a SINGLE `update_notes_bulk` call.

## Step 6 — Update _index.md
Include the `_index.md` update in the SAME `update_notes_bulk` call:
1. Read current index.
2. Add or update entries for the files you just modified:
```markdown
### second brain/[filename].md
- Topics: [keywords]
- Last updated: {today}
- MTime: [mtime from list_notes_recursive]
- Summary: [sentence]
```
3. Overwrite `second brain/_index.md` with the new content.
"""


@mcp.prompt()
def rebuild_index() -> str:
    """
    Scans the entire second brain folder and rebuilds _index.md from scratch.
    Run this when you've added or edited notes manually in Obsidian.
    This is intentionally expensive — it reads every file once.
    """
    today = date.today().isoformat()

    return f"""
Today is {today}. Rebuild the second brain index from scratch.

## Step 1 — Discover all notes
Call `list_notes_recursive("second brain")`. You will receive a JSON list of `{path, mtime}`.

Ignore: `_index.md`, `AI_CONTEXT.md`.

## Step 2 — Compare with existing Index
1. Call `get_note("second brain/_index")`.
2. For each file in the vault, check if its **current `mtime`** is greater than the **`MTime`** recorded in your current index.
3. Identify "Stale" files: any file that is new OR has a newer disk `mtime`.

## Step 3 — Batch Read Stale Notes
Call `get_notes_batch([list of stale files])`. Do NOT read files that are up-to-date.

## Step 4 — Save the Index
Rebuild the full `_index.md` by merging your existing index with the new info.
Ensure every file entry has its current `MTime` recorded.

Report how many files were updated/synced.
"""


@mcp.prompt()
def generate_context_snapshot() -> str:
    """
    Reads the second brain index, selectively reads only relevant notes,
    and synthesizes a structured AI_CONTEXT.md snapshot.
    Scoped strictly to second brain/. Never reads class notes or other folders.
    """
    today = date.today().isoformat()

    return f"""
Today's date is {today}. Regenerate my AI context snapshot.

## Step 1 — Read the index
Call `get_note("second brain/_index")`.

If the index doesn't exist yet, call `list_notes_recursive("second brain")` instead
and use the filenames as a rough guide for Step 2.

## Step 2 — Select which files to read
From the index, identify which files are relevant to each section of AI_CONTEXT.md:

- **Who I Am** → look for: about, background, identity, persistent facts
- **Active Projects** → look for: projects/, anything project-named — prioritize recently updated
- **This Week's Priorities** → look for: priorities, goals, todos
- **Recent Decisions** → look for: decisions
- **Persistent Background** → look for: about, background, constraints, long-term goals

Skip any file that:
- Is named `AI_CONTEXT.md` or `_index.md`
- Was last updated more than 60 days ago AND is about transient things (projects, priorities)
- Is in the `templates/` directory

Call `get_notes_batch(filenames)` for only the selected files — do not read them individually.

## Step 3 — Synthesize
Produce a single, concise document using EXACTLY this structure:

```markdown
# AI Context Snapshot
_Last updated: {today}_

## Who I Am
[Name, role, school, career goals — 2-3 sentences max]

## Active Projects
### [Project Name]
- Status:
- Current blocker:
- Next action:

## This Week's Priorities
[3-5 bullets max]

## Recent Decisions (don't re-litigate)
- [Decision + brief reason]

## Persistent Background
[Scholarship, honors college, constraints, long-term goals — anything that stays true across weeks]
```

Rules:
- Be concise — this gets pasted cold into other AIs. Every sentence earns its place.
- Distill, don't dump raw note content.
- If a section has no data, write "None noted." — never omit a section.
- Preserve specifics: names, project names, numbers, deadlines — vague summaries are useless.

## Step 4 — Save
Call `overwrite_note("second brain/AI_CONTEXT", ...)` with the full markdown.

Report how many files you read and flag any sections that were sparse.
"""
