"""Schema for the structured summary (validation demos)."""

from pydantic import BaseModel, Field


class SummaryPoint(BaseModel):
    idea: str = Field(description="One idea from the paper.")
    section: str = Field(
        description="Name of the paper section that backs the idea: the text between square "
        "brackets at the start of a passage, e.g. '3.1. Residual Learning'."
    )


class DocumentSummary(BaseModel):
    points: list[SummaryPoint]
