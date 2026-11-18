"""smolagents — Parte 1: resumen básico.

El agente tiene una herramienta (buscar en el documento) y una tarea (resumir).
smolagents maneja el ciclo razonar ↔ usar herramienta ↔ responder.

Ejecutar:  python -m smolagents_impl.part1_basic
"""

import os

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

from rag_core import build_rag, config

load_dotenv()
rag = build_rag("data/resnet.pdf")


@tool
def search_document(query: str) -> str:
    """Devuelve los fragmentos del documento más relevantes para la consulta.

    Args:
        query: Lo que se busca en el documento.
    """
    return "\n\n".join(rag.retrieve(query))


agent = ToolCallingAgent(
    tools=[search_document],
    model=OpenAIServerModel(model_id=config.OPENAI_MODEL, api_key=os.environ["OPENAI_API_KEY"]),
)

if __name__ == "__main__":
    print(agent.run("Resume el paper: problema, método y resultados. Responde en español."))
