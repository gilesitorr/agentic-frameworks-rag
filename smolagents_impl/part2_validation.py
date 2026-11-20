"""smolagents — Part 2: structured summary + validation + retries.

smolagents gives us the tool loop, but we orchestrate validation and retries
ourselves: a loop around agent.run (compare it with LangGraph, where the retry
is part of the graph).

Also, smolagents does not guarantee structured output: it returns a dict or JSON
text, so we normalize it before validating.

Run:  python -m smolagents_impl.part2_validation
"""

import json
import os

from dotenv import load_dotenv
from pydantic import ValidationError
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

from rag_core import build_rag, config
from rag_core.schema import DocumentSummary
from rag_core.validation import validate_summary

load_dotenv()
rag = build_rag("data/resnet.pdf")


@tool
def search_document(query: str) -> str:
    """Return the document chunks most relevant to the query.

    Args:
        query: What to search for in the document.
    """
    return "\n\n".join(rag.retrieve(query))


agent = ToolCallingAgent(
    tools=[search_document],
    model=OpenAIServerModel(model_id=config.OPENAI_MODEL, api_key=os.environ["OPENAI_API_KEY"]),
)


def task(problems: list[str]) -> str:
    feedback = f"\n\nFix this from the previous attempt: {problems}" if problems else ""
    return (
        "Summarize the paper using search_document. Return JSON "
        '{"points": [{"idea": "...", "section": "..."}]}.\n'
        f"Each 'section' must be one of: {', '.join(rag.sections)}.\n"
        f"Cite at least {config.MIN_SECTIONS_CITED} distinct sections.{feedback}"
    )


def main() -> None:
    problems: list[str] = []
    summary = None
    for attempt in range(1, config.MAX_ATTEMPTS + 1):
        output = agent.run(task(problems))
        try:
            # smolagents returns the output as a dict or as JSON text.
            data = output if isinstance(output, dict) else json.loads(str(output))
            summary = DocumentSummary.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as error:
            problems = [f"The output does not match the schema: {error}"]
            print(f"Attempt {attempt}: invalid output")
            continue

        problems = validate_summary(summary, rag.sections)
        print(f"Attempt {attempt}: {'valid' if not problems else problems}")
        if not problems:
            break

    if summary:
        for point in summary.points:
            print(f"- [{point.section}] {point.idea}")


if __name__ == "__main__":
    main()
