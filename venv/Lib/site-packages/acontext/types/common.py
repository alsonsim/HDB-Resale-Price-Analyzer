"""Common type definitions shared across modules."""

from pydantic import BaseModel, Field


class FileContent(BaseModel):
    """Parsed file content model."""

    type: str = Field(..., description="File content type: 'text', 'json', 'csv', or 'code'")
    raw: str = Field(..., description="Raw text content of the file")


class FlagResponse(BaseModel):
    """Response model for flag operations like kill sandbox."""

    status: int = Field(..., description="Status code of the operation")
    errmsg: str = Field(..., description="Error message if any")

