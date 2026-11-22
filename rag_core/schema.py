"""Schema for the structured summary (part 2)."""

from pydantic import BaseModel, Field


class SummaryPoint(BaseModel):
    idea: str = Field(description="One idea from the paper.")
    section: str = Field(
        description="The section that backs the idea, copied exactly from the [label] of a passage."
    )


class DocumentSummary(BaseModel):
    points: list[SummaryPoint]
