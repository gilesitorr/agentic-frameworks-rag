"""Demo 02 — La regla de validación (no usa OpenAI).

Compara un resumen válido con uno inválido para mostrar qué revisa la parte 2.
    python demo/02_validacion.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rag_core import DocumentSummary, SummaryPoint, build_rag, validar_resumen

rag = build_rag("data/resnet.pdf")

bueno = DocumentSummary(puntos=[
    SummaryPoint(idea="Aprendizaje residual.", seccion="3 Deep Residual Learning"),
    SummaryPoint(idea="Atajos de identidad.", seccion="3.2 Identity Mapping by Shortcuts"),
    SummaryPoint(idea="Resultados en ImageNet.", seccion="4.1 ImageNet Classification"),
])
malo = DocumentSummary(puntos=[
    SummaryPoint(idea="Algo que el modelo se inventó.", seccion="Sección Falsa"),
])

print("Resumen bueno ->", validar_resumen(bueno, rag.sections) or "válido")
print("Resumen malo  ->", validar_resumen(malo, rag.sections))
