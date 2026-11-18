"""Esquema del resumen estructurado (parte 2)."""

from pydantic import BaseModel


class SummaryPoint(BaseModel):
    idea: str      # una idea del paper
    seccion: str   # la sección que la respalda (etiqueta exacta)


class DocumentSummary(BaseModel):
    puntos: list[SummaryPoint]
