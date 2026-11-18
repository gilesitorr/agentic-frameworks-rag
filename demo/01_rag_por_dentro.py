"""Demo 01 — El RAG por dentro (no usa OpenAI, es instantáneo).

Muestra las secciones detectadas en el PDF y una búsqueda semántica.
    python demo/01_rag_por_dentro.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rag_core import build_rag

rag = build_rag("data/resnet.pdf")

print("Secciones detectadas:")
for seccion in rag.sections:
    print(" -", seccion)

print("\nBúsqueda semántica: '¿qué es el aprendizaje residual?'\n")
for fragmento in rag.retrieve("¿qué es el aprendizaje residual?"):
    print("•", fragmento[:200].replace("\n", " "), "...\n")
