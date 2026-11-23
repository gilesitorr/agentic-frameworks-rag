"""Baseline — basic: the same summary with no framework.

Retrieve once, then a single LLM call. The workflow pattern, by hand — compare it
with langgraph_impl/part1_basic.py, which is the same flow as an explicit graph.
Only the OpenAI SDK talks to the model; no agent framework is involved.

Run:  python -m baseline.summarize_basic
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from rag_core import build_rag, config

load_dotenv()
rag = build_rag("data/resnet.pdf")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def main() -> None:
    context = "\n\n".join(rag.retrieve("the paper's problem, method and results"))
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[{"role": "user", "content": f"Summarize the paper:\n\n{context}"}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
