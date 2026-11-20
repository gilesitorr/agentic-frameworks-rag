"""LangGraph — Part 2: structured summary + validation + retries.

The retry is an explicit cycle in the graph: generate → validate → if it is
not valid, go back to generate with the feedback.

Run:  python -m langgraph_impl.part2_validation
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from openai import OpenAI

from rag_core import build_rag, config
from rag_core.schema import DocumentSummary
from rag_core.validation import validate_summary

load_dotenv()
rag = build_rag("data/resnet.pdf")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class State(TypedDict):
    context: str
    summary: DocumentSummary
    problems: list[str]
    attempts: int


def retrieve(state: State) -> dict:
    chunks = rag.retrieve("the paper's problem, method and results")
    return {"context": "\n\n".join(chunks), "attempts": 0, "problems": []}


def generate(state: State) -> dict:
    feedback = f"\n\nFix this from the previous attempt: {state['problems']}" if state["problems"] else ""
    prompt = (
        "Summarize the paper as points. Return JSON "
        '{"points": [{"idea": "...", "section": "..."}]}.\n'
        f"Each 'section' must be one of: {', '.join(rag.sections)}.\n"
        f"Cite at least {config.MIN_SECTIONS_CITED} distinct sections.\n\n"
        f"Context:\n{state['context']}{feedback}"
    )
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    summary = DocumentSummary.model_validate_json(response.choices[0].message.content)
    return {"summary": summary, "attempts": state["attempts"] + 1}


def validate(state: State) -> dict:
    return {"problems": validate_summary(state["summary"], rag.sections)}


def route(state: State) -> str:
    if not state["problems"] or state["attempts"] >= config.MAX_ATTEMPTS:
        return "end"
    return "retry"


graph = StateGraph(State)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.add_node("validate", validate)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", "validate")
graph.add_conditional_edges("validate", route, {"retry": "generate", "end": END})
app = graph.compile()

if __name__ == "__main__":
    state = app.invoke({})
    print(f"Attempts: {state['attempts']} · valid: {not state['problems']}")
    for point in state["summary"].points:
        print(f"- [{point.section}] {point.idea}")
