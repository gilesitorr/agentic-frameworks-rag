"""smolagents — Parte 2: resumen estructurado + validación + reintentos.

A diferencia de la parte 1, el resumen debe ser ESTRUCTURADO: cada punto cita
una sección del documento. Validamos que las secciones citadas existan y, si no,
reintentamos pasándole al agente el feedback.

Para la charla: smolagents nos da el ciclo de herramientas, pero la validación
estructural y el reintento los orquestamos NOSOTROS (compáralo con Pydantic AI,
que trae validadores, y con LangGraph, que modela el ciclo dentro del grafo).

Correr desde la raíz del proyecto:
    python -m smolagents_impl.part2_validation
"""

import os

from dotenv import load_dotenv
from smolagents import OpenAIServerModel, ToolCallingAgent, tool

from rag_core import build_rag, config
from rag_core.schema import DocumentSummary
from rag_core.validation import validar_resumen

load_dotenv()

rag = build_rag("data/resnet.pdf")


@tool
def search_document(query: str) -> str:
    """Busca en el documento y devuelve los fragmentos más relevantes.

    Args:
        query: Lo que se quiere encontrar en el documento.
    """
    return "\n\n---\n\n".join(rag.retrieve(query))


model = OpenAIServerModel(model_id=config.OPENAI_MODEL, api_key=os.environ["OPENAI_API_KEY"])
agent = ToolCallingAgent(tools=[search_document], model=model)


def _extraer_json(texto: str) -> str:
    """Toma el objeto JSON de la respuesta (el agente puede añadir texto alrededor)."""
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fin == -1:
        raise ValueError("La respuesta no contiene un objeto JSON.")
    return texto[inicio:fin + 1]


def construir_tarea(feedback: str = "") -> str:
    secciones = "\n".join(f"- {s}" for s in rag.sections)
    tarea = (
        "Resume el paper en varios puntos usando la herramienta search_document.\n"
        'Responde SOLO con un JSON de la forma: '
        '{"puntos": [{"idea": "...", "seccion": "..."}]}\n'
        "Cada 'seccion' debe ser EXACTAMENTE una de estas etiquetas del documento:\n"
        f"{secciones}\n"
        f"Cita al menos {config.MIN_SECCIONES_CITADAS} secciones distintas. Responde en español."
    )
    if feedback:
        tarea += f"\n\nEl intento anterior falló por:\n{feedback}\nCorrígelo."
    return tarea


def main() -> None:
    feedback = ""
    for intento in range(1, config.MAX_INTENTOS + 1):
        print(f"\n--- Intento {intento} ---")
        salida = agent.run(construir_tarea(feedback))
        try:
            resumen = DocumentSummary.model_validate_json(_extraer_json(str(salida)))
        except Exception as error:
            feedback = f"La salida no es un JSON válido del esquema: {error}"
            print("  JSON inválido:", error)
            continue

        problemas = validar_resumen(resumen, rag.sections)
        if not problemas:
            print("  OK - resumen válido:")
            for punto in resumen.puntos:
                print(f"   - [{punto.seccion}] {punto.idea}")
            return

        feedback = "\n".join(problemas)
        print("  Problemas:", feedback)

    print("\nSe agotaron los intentos sin un resumen válido.")


if __name__ == "__main__":
    main()
