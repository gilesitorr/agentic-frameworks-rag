"""rag_core: motor RAG compartido + esquema y validación de la parte 2."""

from . import config
from .rag import Rag, build_rag
from .schema import DocumentSummary, SummaryPoint
from .validation import validar_resumen

__all__ = ["config", "build_rag", "Rag", "DocumentSummary", "SummaryPoint", "validar_resumen"]
