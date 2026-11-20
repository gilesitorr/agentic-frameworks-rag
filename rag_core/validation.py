"""Summary validation (part 2): every point must cite a real section of the
document, and at least MIN_SECTIONS_CITED distinct sections must be covered."""

from . import config
from .schema import DocumentSummary


def validate_summary(summary: DocumentSummary, sections: list[str]) -> list[str]:
    """List of problems found (empty = valid summary)."""
    valid = set(sections)
    cited = [point.section for point in summary.points]

    problems = [f"Section '{s}' is not in the document." for s in cited if s not in valid]
    if len(set(cited)) < config.MIN_SECTIONS_CITED:
        problems.append(
            f"Cites {len(set(cited))} distinct sections; {config.MIN_SECTIONS_CITED} are required."
        )
    return problems
