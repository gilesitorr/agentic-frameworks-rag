"""The RAG internals (no OpenAI, instant).

Shows the sections detected in the PDF and a semantic search.
    python demo/rag_internals.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rag_core import build_rag

rag = build_rag("data/resnet.pdf")

print("Detected sections:")
for section in rag.sections:
    print(" -", section)

print("\nSemantic search: 'what is residual learning?'\n")
for chunk in rag.retrieve("what is residual learning?"):
    print("•", chunk[:200].replace("\n", " "), "...\n")
