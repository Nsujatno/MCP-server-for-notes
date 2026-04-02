from .mcp_instance import mcp
from .tools import get_note


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
