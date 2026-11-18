"""smolagents — Parte 2: resumen estructurado + validación + reintentos.

smolagents nos da el ciclo de herramientas, pero la validación y el reintento los
orquestamos nosotros: un bucle alrededor de agent.run (compáralo con LangGraph,
donde el reintento es parte del grafo).

Además, smolagents no garantiza salida estructurada: devuelve un dict o texto JSON,
así que lo normalizamos antes de validar.

Ejecutar:  python -m smolagents_impl.part2_validation
"""

import json
import os

from dotenv import load_dotenv
from pydantic import ValidationError
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

from rag_core import build_rag, config
from rag_core.schema import DocumentSummary
from rag_core.validation import validar_resumen

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


def tarea(problemas: list[str]) -> str:
    feedback = f"\n\nCorrige esto del intento anterior: {problemas}" if problemas else ""
    return (
        "Resume el paper usando search_document. Devuelve JSON "
        '{"puntos": [{"idea": "...", "seccion": "..."}]}.\n'
        f"Cada 'seccion' debe ser una de: {', '.join(rag.sections)}.\n"
        f"Cita al menos {config.MIN_SECCIONES_CITADAS} secciones distintas. Responde en español.{feedback}"
    )


def main() -> None:
    problemas: list[str] = []
    resumen = None
    for intento in range(1, config.MAX_INTENTOS + 1):
        salida = agent.run(tarea(problemas))
        try:
            # smolagents devuelve la salida como dict o como texto JSON.
            datos = salida if isinstance(salida, dict) else json.loads(str(salida))
            resumen = DocumentSummary.model_validate(datos)
        except (json.JSONDecodeError, ValidationError) as error:
            problemas = [f"La salida no respeta el esquema: {error}"]
            print(f"Intento {intento}: salida inválida")
            continue

        problemas = validar_resumen(resumen, rag.sections)
        print(f"Intento {intento}: {'válido' if not problemas else problemas}")
        if not problemas:
            break

    if resumen:
        for punto in resumen.puntos:
            print(f"- [{punto.seccion}] {punto.idea}")


if __name__ == "__main__":
    main()
