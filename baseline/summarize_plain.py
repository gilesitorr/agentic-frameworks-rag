"""Baseline — el mismo flujo SIN framework.

Hacemos a mano lo que smolagents / Pydantic AI / LangGraph organizan por ti:
recuperar, generar estructurado, validar y reintentar en un bucle.

Ejecutar:  python -m baseline.summarize_plain
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from rag_core import build_rag, config
from rag_core.schema import DocumentSummary
from rag_core.validation import validar_resumen

load_dotenv()
rag = build_rag("data/resnet.pdf")
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def prompt(contexto: str, problemas: list[str]) -> str:
    feedback = f"\n\nCorrige esto del intento anterior: {problemas}" if problemas else ""
    return (
        "Resume el paper en puntos. Devuelve JSON "
        '{"puntos": [{"idea": "...", "seccion": "..."}]}.\n'
        f"Cada 'seccion' debe ser una de: {', '.join(rag.sections)}.\n"
        f"Cita al menos {config.MIN_SECCIONES_CITADAS} secciones distintas. Responde en español.\n\n"
        f"Contexto:\n{contexto}{feedback}"
    )


def main() -> None:
    contexto = "\n\n".join(rag.retrieve("problema, método y resultados del paper"))
    problemas: list[str] = []

    for intento in range(1, config.MAX_INTENTOS + 1):
        respuesta = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt(contexto, problemas)}],
        )
        resumen = DocumentSummary.model_validate_json(respuesta.choices[0].message.content)
        problemas = validar_resumen(resumen, rag.sections)
        print(f"Intento {intento}: {'válido' if not problemas else problemas}")
        if not problemas:
            break

    for punto in resumen.puntos:
        print(f"- [{punto.seccion}] {punto.idea}")


if __name__ == "__main__":
    main()
