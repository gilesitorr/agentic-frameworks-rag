"""Schema for the structured summary (part 2)."""

from pydantic import BaseModel


class SummaryPoint(BaseModel):
    idea: str       # one idea from the paper
    section: str    # the section that backs it (exact label)


class DocumentSummary(BaseModel):
    points: list[SummaryPoint]
