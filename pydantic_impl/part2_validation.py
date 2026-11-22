"""Pydantic AI — validation: structured summary + validation + retries.

Same agent as the basic version, plus two decorators: the valid sections go into the
instructions, and an output validator runs the shared rule. When it fails we raise
ModelRetry: Pydantic AI sends the problems back to the model and asks again, up to
`retries` times. There is no loop of ours (compare it with smolagents and LangGraph).

Run:  python -m pydantic_impl.part2_validation
"""

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.exceptions import UnexpectedModelBehavior

from rag_core import Rag, build_rag, config
from rag_core.schema import DocumentSummary
from rag_core.validation import validate_summary

load_dotenv()

agent = Agent(
    f"openai:{config.OPENAI_MODEL}",
    deps_type=Rag,
    output_type=DocumentSummary,
    instructions="Summarize the paper as points. Use search_document.",
    retries=config.MAX_ATTEMPTS - 1,  # the first attempt + retries = MAX_ATTEMPTS
)


@agent.instructions
def valid_sections(ctx: RunContext[Rag]) -> str:
    return (
        f"Each 'section' must be one of: {', '.join(ctx.deps.sections)}.\n"
        f"Cite at least {config.MIN_SECTIONS_CITED} distinct sections."
    )


@agent.tool
def search_document(ctx: RunContext[Rag], query: str) -> str:
    """Return the document chunks most relevant to the query.

    Args:
        query: What to search for in the document.
    """
    return "\n\n".join(ctx.deps.retrieve(query))


@agent.output_validator
def check_sections(ctx: RunContext[Rag], summary: DocumentSummary) -> DocumentSummary:
    problems = validate_summary(summary, ctx.deps.sections)
    print(f"Attempt {ctx.retry + 1}: {'valid' if not problems else problems}")
    if problems:
        raise ModelRetry(f"Fix this: {problems}")
    return summary


def main() -> None:
    try:
        result = agent.run_sync("Summarize the paper.", deps=build_rag("data/resnet.pdf"))
    except UnexpectedModelBehavior as error:  # still invalid after MAX_ATTEMPTS
        print(error)
        return
    for point in result.output.points:
        print(f"- [{point.section}] {point.idea}")
    print(result.usage)


if __name__ == "__main__":
    main()
