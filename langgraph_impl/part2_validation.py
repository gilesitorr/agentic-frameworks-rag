"""LangGraph — Parte 2: resumen estructurado + validación + reintentos.

El reintento es un ciclo explícito en el grafo: generar → validar → si no es
válido, volver a generar con el feedback.

Ejecutar:  python -m langgraph_impl.part2_validation
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from openai import OpenAI

from rag_core import build_rag, config
from rag_core.schema import DocumentSummary
from rag_core.validation import validar_resumen

load_dotenv()
rag = build_rag("data/resnet.pdf")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


class Estado(TypedDict):
    contexto: str
    resumen: DocumentSummary
    problemas: list[str]
    intentos: int


def recuperar(estado: Estado) -> dict:
    fragmentos = rag.retrieve("problema, método y resultados del paper")
    return {"contexto": "\n\n".join(fragmentos), "intentos": 0, "problemas": []}


def generar(estado: Estado) -> dict:
    feedback = f"\n\nCorrige esto del intento anterior: {estado['problemas']}" if estado["problemas"] else ""
    prompt = (
        "Resume el paper en puntos. Devuelve JSON "
        '{"puntos": [{"idea": "...", "seccion": "..."}]}.\n'
        f"Cada 'seccion' debe ser una de: {', '.join(rag.sections)}.\n"
        f"Cita al menos {config.MIN_SECCIONES_CITADAS} secciones distintas. Responde en español.\n\n"
        f"Contexto:\n{estado['contexto']}{feedback}"
    )
    respuesta = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    resumen = DocumentSummary.model_validate_json(respuesta.choices[0].message.content)
    return {"resumen": resumen, "intentos": estado["intentos"] + 1}


def validar(estado: Estado) -> dict:
    return {"problemas": validar_resumen(estado["resumen"], rag.sections)}


def seguir(estado: Estado) -> str:
    if not estado["problemas"] or estado["intentos"] >= config.MAX_INTENTOS:
        return "fin"
    return "reintentar"


grafo = StateGraph(Estado)
grafo.add_node("recuperar", recuperar)
grafo.add_node("generar", generar)
grafo.add_node("validar", validar)
grafo.add_edge(START, "recuperar")
grafo.add_edge("recuperar", "generar")
grafo.add_edge("generar", "validar")
grafo.add_conditional_edges("validar", seguir, {"reintentar": "generar", "fin": END})
app = grafo.compile()

if __name__ == "__main__":
    estado = app.invoke({})
    print(f"Intentos: {estado['intentos']} · válido: {not estado['problemas']}")
    for punto in estado["resumen"].puntos:
        print(f"- [{punto.seccion}] {punto.idea}")
