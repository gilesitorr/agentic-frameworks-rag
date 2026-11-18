"""LangGraph — Parte 1: resumen básico como grafo explícito.

Definimos el flujo como nodos + aristas: recuperar → generar. El control es
explícito, a diferencia de smolagents, que esconde el ciclo dentro del agente.

Ejecutar:  python -m langgraph_impl.part1_basic
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


class Estado(TypedDict):
    contexto: str
    resumen: str


def recuperar(estado: Estado) -> dict:
    return {"contexto": "\n\n".join(rag.retrieve("problema, método y resultados del paper"))}


def generar(estado: Estado) -> dict:
    respuesta = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[{"role": "user", "content": f"Resume el paper en español:\n\n{estado['contexto']}"}],
    )
    return {"resumen": respuesta.choices[0].message.content}


grafo = StateGraph(Estado)
grafo.add_node("recuperar", recuperar)
grafo.add_node("generar", generar)
grafo.add_edge(START, "recuperar")
grafo.add_edge("recuperar", "generar")
grafo.add_edge("generar", END)
app = grafo.compile()

if __name__ == "__main__":
    print(app.invoke({})["resumen"])
