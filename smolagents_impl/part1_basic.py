"""smolagents — Parte 1: RAG básico para resumir el paper.

Idea: le damos al agente UNA herramienta (buscar en el documento) y una tarea
(resumir). smolagents se encarga del ciclo razonar <-> llamar herramienta <->
responder. Nosotros no escribimos ese loop.

Correr desde la raíz del proyecto:
    python -m smolagents_impl.part1_basic
"""

import os

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

from rag_core import build_rag, config

load_dotenv()

# 1) Motor RAG compartido (idéntico en las tres implementaciones).
rag = build_rag("data/resnet.pdf")


# 2) Exponemos la búsqueda semántica como una herramienta del agente.
@tool
def search_document(query: str) -> str:
    """Busca en el documento y devuelve los fragmentos más relevantes.

    Args:
        query: Lo que se quiere encontrar en el documento.
    """
    return "\n\n---\n\n".join(rag.retrieve(query))


# 3) Modelo de lenguaje (OpenAI) — el mismo para todos.
model = OpenAIServerModel(model_id=config.OPENAI_MODEL, api_key=os.environ["OPENAI_API_KEY"])

# 4) El agente: herramientas + modelo. smolagents maneja el ciclo por nosotros.
agent = ToolCallingAgent(tools=[search_document], model=model)

TASK = (
    "Escribe un resumen claro del paper. Usa la herramienta search_document para "
    "recuperar información sobre el problema que aborda, el método propuesto y los "
    "resultados principales. Responde en español."
)


if __name__ == "__main__":
    summary = agent.run(TASK)
    print("\n===== RESUMEN =====\n")
    print(summary)
