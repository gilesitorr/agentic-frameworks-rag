"""LangGraph — Part 1: basic summary as an explicit graph.

We define the flow as nodes + edges: retrieve → generate. The control is
explicit, unlike smolagents, which hides the loop inside the agent.

Run:  python -m langgraph_impl.part1_basic
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from openai import OpenAI

from rag_core import build_rag, config

load_dotenv()
rag = build_rag("data/resnet.pdf")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class State(TypedDict):
    context: str
    summary: str


def retrieve(state: State) -> dict:
    return {"context": "\n\n".join(rag.retrieve("the paper's problem, method and results"))}


def generate(state: State) -> dict:
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[{"role": "user", "content": f"Summarize the paper:\n\n{state['context']}"}],
    )
    return {"summary": response.choices[0].message.content}


graph = StateGraph(State)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)
app = graph.compile()

if __name__ == "__main__":
    print(app.invoke({})["summary"])
