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
Call `list_notes_recursive` with folder="second brain" to see what files currently exist.
If "_index.md" appears in the list, call `get_note("second brain/_index")` to understand how the vault is organized.

## Step 2 — Extract nuggets from this conversation
Scan the conversation and extract only what's worth persisting long-term. Be ruthless.

**Extract:**
- Decisions made (with brief rationale)
- Project status changes, blockers resolved, next actions clarified
- New ideas or concepts worth revisiting later
- Shifts in priorities
- Persistent facts about me (background, constraints, goals)

**Do NOT extract:**
- Exploratory back-and-forth that didn't land anywhere
- Things I already knew before this conversation started
- Code snippets (those live in repos, not the second brain)
- Anything prefixed with "I'm thinking about maybe..."
- **CRITICAL:** Never write to or edit `second brain/AI_CONTEXT.md`. That file is strictly managed by the `generate_context_snapshot` process and should not receive atomic updates from sessions.

## Step 3 — Plan where each nugget goes
For each nugget, decide which file it belongs in. You have full freedom over file structure under `second brain/`. Good conventions:
- `second brain/decisions.md` — running log of decisions
- `second brain/projects/<project-name>.md` — one file per project
- `second brain/about.md` — persistent background facts about me
- `second brain/ideas.md` — ideas worth revisiting
- Or any other structure that fits the content

Check if the target file already exists (from Step 1). Pick the right tool:
- File exists → `append_to_note`
- File doesn't exist → `create_note`

Each nugget format:
```
**[{today}]** [1-2 sentence atomic fact. Specific names, numbers, context. No vague summaries.]
```

## Step 4 — Show dry-run preview (DO NOT WRITE YET)
Present this table and stop — do not write anything until I respond:

```
Here's what I'd save from this session:

| # | Target file | Action | Content |
|---|---|---|---|
| 1 | second brain/decisions.md | append | **[{today}]** ... |
| 2 | second brain/projects/vault-brain.md | create | **[{today}]** ... |

Reply "looks good" to save all, give me numbers to skip (e.g. "skip 2"),
or tell me to reword anything. You can also say "add [content] to [file]"
to include something I missed.
```

## Step 5 — After I respond, write approved items
Apply any changes I requested, then write only the approved nuggets using `append_to_note` or `create_note`.

## Step 6 — Update _index.md
After all writes are complete:
1. Read current index: `get_note("second brain/_index")` if it exists, otherwise start fresh
2. Add or update one entry for every file you just wrote to:

```markdown
### second brain/[filename].md
- Topics: [comma-separated keywords]
- Last updated: {today}
- Summary: [one sentence — what kind of info lives in this file]
```

3. Call `overwrite_note("second brain/_index", ...)` with the full updated index

Confirm how many nuggets were saved and list the files that changed.
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
Call `list_notes_recursive("second brain")`.

Ignore these files entirely (don't read them, don't index them):
- `second brain/_index.md`
- `second brain/AI_CONTEXT.md`
- Anything in a `templates/` directory (already excluded by the tool)

## Step 2 — Read each note
For every file in the list, call `get_note(filename)` to read its full content.

## Step 3 — Build the index
Produce a new `_index.md` with this structure:

```markdown
# Second Brain Index
_Last rebuilt: {today}_

## Files

### second brain/[filename].md
- Topics: [comma-separated keywords extracted from content]
- Last updated: [most recent **[YYYY-MM-DD]** datestamp found in the file, or "{today}" if none]
- Summary: [one sentence — what kind of information lives in this file]
```

Order entries by last updated date, most recent first.

## Step 4 — Save
Call `overwrite_note("second brain/_index", ...)` with the full index markdown.

Report how many files were indexed.
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

Call `get_note(...)` for only the selected files — do not read everything.

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
