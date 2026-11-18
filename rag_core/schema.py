"""Esquema del resumen estructurado (parte 2), compartido por las implementaciones.

En la parte 2 el resumen deja de ser texto libre: cada punto cita la sección del
documento que lo respalda. Eso es lo que luego validamos.
"""

from pydantic import BaseModel, Field


class SummaryPoint(BaseModel):
    """Una idea del resumen y la sección del documento que la respalda."""

    idea: str = Field(description="Una idea clave del paper, en una o dos frases.")
    seccion: str = Field(description="Etiqueta EXACTA de la sección que respalda la idea.")


class DocumentSummary(BaseModel):
    """Resumen del documento como una lista de puntos con su sección."""

    puntos: list[SummaryPoint]
