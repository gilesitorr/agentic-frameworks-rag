"""Criterio de validación del resumen (parte 2), idéntico para las implementaciones.

Regla (simple y determinista, fácil de justificar en vivo):
  1. cada punto debe citar una sección que EXISTA en el documento, y
  2. el resumen debe cubrir al menos MIN_SECCIONES_CITADAS secciones distintas.

Nota: una validación más estricta ("grounding": que el texto citado aparezca en
los fragmentos recuperados) es una extensión natural, pero la dejamos fuera para
mantener la demo simple y reproducible.
"""

from . import config
from .schema import DocumentSummary


def validar_resumen(resumen: DocumentSummary, secciones_validas: list[str]) -> list[str]:
    """Devuelve una lista de problemas; vacía significa que el resumen es válido."""
    problemas: list[str] = []
    validas = set(secciones_validas)
    citadas = [punto.seccion for punto in resumen.puntos]

    for seccion in citadas:
        if seccion not in validas:
            problemas.append(f"La sección citada '{seccion}' no existe en el documento.")

    distintas = len(set(citadas))
    if distintas < config.MIN_SECCIONES_CITADAS:
        problemas.append(
            f"El resumen cita {distintas} secciones distintas; "
            f"se requieren al menos {config.MIN_SECCIONES_CITADAS}."
        )
    return problemas
