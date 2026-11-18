"""LangGraph — Parte 2: resumen estructurado + validación + reintentos.

Aquí brilla LangGraph: el reintento es un CICLO explícito en el grafo. Tras
generar, un nodo valida; una arista condicional decide si terminar o volver a
generar (ahora con el feedback de los problemas encontrados).

    START -> recuperar -> generar -> validar -> ¿válido o sin intentos?
                                       ^                    |  sí -> END
                                       |____ no ____________|

Correr desde la raíz del proyecto:
    python -m langgraph_impl.part2_validation
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
    """Nodo 1: recupera el contexto una sola vez e inicializa los contadores."""
    fragmentos = rag.retrieve("problema, método y resultados principales del paper")
    return {"contexto": "\n\n---\n\n".join(fragmentos), "intentos": 0, "problemas": []}


def generar(estado: Estado) -> dict:
    """Nodo 2: genera el resumen estructurado (en JSON), con feedback si lo hay."""
    secciones = "\n".join(f"- {s}" for s in rag.sections)
    feedback = ""
    if estado["problemas"]:
        feedback = "\n\nEl intento anterior falló por:\n" + "\n".join(estado["problemas"]) + "\nCorrígelo."
    prompt = (
        "Resume el paper en varios puntos con base en el contexto.\n"
        'Devuelve un JSON {"puntos": [{"idea": "...", "seccion": "..."}]}.\n'
        "Cada 'seccion' debe ser EXACTAMENTE una de estas etiquetas:\n"
        f"{secciones}\n"
        f"Cita al menos {config.MIN_SECCIONES_CITADAS} secciones distintas.\n\n"
        f"Contexto:\n{estado['contexto']}{feedback}"
    )
    respuesta = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Devuelves JSON válido en español."},
            {"role": "user", "content": prompt},
        ],
    )
    resumen = DocumentSummary.model_validate_json(respuesta.choices[0].message.content)
    return {"resumen": resumen, "intentos": estado["intentos"] + 1}


def validar(estado: Estado) -> dict:
    """Nodo 3: aplica el criterio de validación compartido."""
    return {"problemas": validar_resumen(estado["resumen"], rag.sections)}


def decidir(estado: Estado) -> str:
    """Arista condicional: terminar si es válido o si se acabaron los intentos."""
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
grafo.add_conditional_edges("validar", decidir, {"reintentar": "generar", "fin": END})
app = grafo.compile()


def main() -> None:
    resultado = app.invoke({})
    resumen = resultado["resumen"]
    problemas = resultado["problemas"]
    print(f"\nIntentos: {resultado['intentos']} | ¿válido?: {not problemas}")
    if problemas:
        print("Problemas restantes:", problemas)
    for punto in resumen.puntos:
        print(f"   - [{punto.seccion}] {punto.idea}")


if __name__ == "__main__":
    main()
