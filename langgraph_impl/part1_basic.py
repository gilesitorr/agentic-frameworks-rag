"""LangGraph — Parte 1: RAG básico como un grafo explícito.

LangGraph modela el flujo como un grafo de estados: nosotros definimos los nodos
(recuperar, generar) y las aristas. El control es EXPLÍCITO, lo contrario a
smolagents, que esconde el ciclo dentro del agente.

Correr desde la raíz del proyecto:
    python -m langgraph_impl.part1_basic
"""

from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from openai import OpenAI

from rag_core import build_rag, config

load_dotenv()

rag = build_rag("data/resnet.pdf")
client = OpenAI()


class Estado(TypedDict):
    tema: str        # qué queremos buscar/resumir
    contexto: str    # fragmentos recuperados
    resumen: str     # resultado final


def recuperar(estado: Estado) -> dict:
    """Nodo 1: busca fragmentos relevantes y los deja en el estado."""
    fragmentos = rag.retrieve(estado["tema"])
    return {"contexto": "\n\n---\n\n".join(fragmentos)}


def generar(estado: Estado) -> dict:
    """Nodo 2: pide al modelo un resumen a partir del contexto recuperado."""
    respuesta = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Resumes papers técnicos de forma clara, en español."},
            {"role": "user", "content": f"Resume el paper con base en este contexto:\n\n{estado['contexto']}"},
        ],
    )
    return {"resumen": respuesta.choices[0].message.content}


# Armamos el grafo: START -> recuperar -> generar -> END
grafo = StateGraph(Estado)
grafo.add_node("recuperar", recuperar)
grafo.add_node("generar", generar)
grafo.add_edge(START, "recuperar")
grafo.add_edge("recuperar", "generar")
grafo.add_edge("generar", END)
app = grafo.compile()


def main() -> None:
    resultado = app.invoke({"tema": "problema que resuelve, método propuesto y resultados principales"})
    print("\n===== RESUMEN =====\n")
    print(resultado["resumen"])


if __name__ == "__main__":
    main()
