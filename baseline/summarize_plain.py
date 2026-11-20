"""Baseline — the same flow WITHOUT a framework.

We do by hand what smolagents / Pydantic AI / LangGraph organize for you:
retrieve, generate structured output, validate and retry in a loop.

Run:  python -m baseline.summarize_plain
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from rag_core import build_rag, config
from rag_core.schema import DocumentSummary
from rag_core.validation import validate_summary

load_dotenv()
rag = build_rag("data/resnet.pdf")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def prompt(context: str, problems: list[str]) -> str:
    feedback = f"\n\nFix this from the previous attempt: {problems}" if problems else ""
    return (
        "Summarize the paper as points. Return JSON "
        '{"points": [{"idea": "...", "section": "..."}]}.\n'
        f"Each 'section' must be one of: {', '.join(rag.sections)}.\n"
        f"Cite at least {config.MIN_SECTIONS_CITED} distinct sections.\n\n"
        f"Context:\n{context}{feedback}"
    )


def main() -> None:
    context = "\n\n".join(rag.retrieve("the paper's problem, method and results"))
    problems: list[str] = []

    for attempt in range(1, config.MAX_ATTEMPTS + 1):
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt(context, problems)}],
        )
        summary = DocumentSummary.model_validate_json(response.choices[0].message.content)
        problems = validate_summary(summary, rag.sections)
        print(f"Attempt {attempt}: {'valid' if not problems else problems}")
        if not problems:
            break

    for point in summary.points:
        print(f"- [{point.section}] {point.idea}")


if __name__ == "__main__":
    main()
