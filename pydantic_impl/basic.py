"""Pydantic AI — basic: summarize the paper with a search tool.

The agent has one tool (search the document) and returns a typed DocumentSummary.
Pydantic AI runs the reason ↔ use tool ↔ answer loop, builds the tool schema from
the type hints and docstring, and validates the answer against the Pydantic model
(asking the model to fix it if it doesn't match).

Run:  python -m pydantic_impl.basic
"""

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from rag_core import Rag, build_rag, config
from rag_core.schema import DocumentSummary

load_dotenv()

agent = Agent(
    f"openai:{config.OPENAI_MODEL}",
    deps_type=Rag,  # what the tools receive through RunContext
    output_type=DocumentSummary,  # the answer is a validated DocumentSummary, not text
    instructions="Summarize the paper: problem, method and results. Use search_document.",
)


@agent.tool
def search_document(ctx: RunContext[Rag], query: str) -> str:
    """Return the document chunks most relevant to the query.

    Args:
        query: What to search for in the document.
    """
    return "\n\n".join(ctx.deps.retrieve(query))


if __name__ == "__main__":
    result = agent.run_sync("Summarize the paper.", deps=build_rag("data/resnet.pdf"))
    for point in result.output.points:
        print(f"- [{point.section}] {point.idea}")
    print(result.usage)
