"""Baseline — el MISMO sistema pero SIN framework.

Hace a mano lo que luego delegamos a smolagents / Pydantic AI / LangGraph:
recuperar contexto, pedir un resumen estructurado, validarlo y reintentar en un
bucle. Sirve para mostrar en vivo qué responsabilidades asume cada framework.

Correr desde la raíz del proyecto:
    python -m baseline.summarize_plain
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


def construir_prompt(contexto: str, problemas: list[str]) -> str:
    secciones = "\n".join(f"- {s}" for s in rag.sections)
    feedback = ""
    if problemas:
        feedback = "\n\nEl intento anterior falló por:\n" + "\n".join(problemas) + "\nCorrígelo."
    return (
        "Resume el paper en varios puntos con base en el contexto.\n"
        'Devuelve un JSON {"puntos": [{"idea": "...", "seccion": "..."}]}.\n'
        "Cada 'seccion' debe ser EXACTAMENTE una de estas etiquetas:\n"
        f"{secciones}\n"
        f"Cita al menos {config.MIN_SECCIONES_CITADAS} secciones distintas.\n\n"
        f"Contexto:\n{contexto}{feedback}"
    )


def main() -> None:
    # 1) Recuperar contexto (a mano).
    contexto = "\n\n---\n\n".join(rag.retrieve("problema, método y resultados principales del paper"))

    # 2) Generar -> validar -> reintentar (bucle a mano, sin framework).
    problemas: list[str] = []
    for intento in range(1, config.MAX_INTENTOS + 1):
        print(f"\n--- Intento {intento} ---")
        respuesta = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Devuelves JSON válido en español."},
                {"role": "user", "content": construir_prompt(contexto, problemas)},
            ],
        )
        try:
            resumen = DocumentSummary.model_validate_json(respuesta.choices[0].message.content)
        except Exception as error:
            problemas = [f"La salida no es un JSON válido del esquema: {error}"]
            print("  JSON inválido:", error)
            continue

        problemas = validar_resumen(resumen, rag.sections)
        if not problemas:
            print("  OK - resumen válido:")
            for punto in resumen.puntos:
                print(f"   - [{punto.seccion}] {punto.idea}")
            return
        print("  Problemas:", problemas)

    print("\nSe agotaron los intentos sin un resumen válido.")


if __name__ == "__main__":
    main()
