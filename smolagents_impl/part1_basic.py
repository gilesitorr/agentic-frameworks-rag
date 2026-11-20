"""smolagents — Part 1: basic summary.

The agent has one tool (search the document) and one task (summarize).
smolagents handles the reason ↔ use tool ↔ answer loop.

Run:  python -m smolagents_impl.part1_basic
"""

import os

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

from rag_core import build_rag, config

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

if __name__ == "__main__":
    print(agent.run("Summarize the paper: problem, method and results."))
