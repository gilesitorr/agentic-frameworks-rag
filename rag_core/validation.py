"""Validación del resumen (parte 2): cada punto debe citar una sección real del
documento, y hay que cubrir al menos MIN_SECCIONES_CITADAS secciones distintas."""

from . import config
from .schema import DocumentSummary


def validar_resumen(resumen: DocumentSummary, secciones: list[str]) -> list[str]:
    """Lista de problemas encontrados (vacía = resumen válido)."""
    validas = set(secciones)
    citadas = [punto.seccion for punto in resumen.puntos]

    problemas = [f"La sección '{s}' no existe en el documento." for s in citadas if s not in validas]
    if len(set(citadas)) < config.MIN_SECCIONES_CITADAS:
        problemas.append(
            f"Cita {len(set(citadas))} secciones distintas; se requieren {config.MIN_SECCIONES_CITADAS}."
        )
    return problemas
