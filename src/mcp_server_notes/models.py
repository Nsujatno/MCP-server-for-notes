from pydantic import BaseModel, Field
from typing import Literal


class NoteUpdate(BaseModel):
    """
    Represents a single file operation (create, append, or overwrite).
    """
    filename: str = Field(..., description="The name of the note (with or without .md extension)")
    content: str = Field(..., description="The text body to write into the file")
    type: Literal["create", "append", "overwrite"] = Field(
        "append", description="The type of write operation"
    )


class BulkUpdate(BaseModel):
    """
    A collection of file updates to be performed in a single tool call.
    """
    updates: list[NoteUpdate] = Field(..., description="A list of file operations to perform")
