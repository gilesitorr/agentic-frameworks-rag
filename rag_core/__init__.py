"""rag_core: shared RAG engine + the schema and rule for the validation demos."""

from . import config
from .rag import Rag, build_rag
from .schema import DocumentSummary, SummaryPoint
from .validation import validate_summary

__all__ = ["config", "build_rag", "Rag", "DocumentSummary", "SummaryPoint", "validate_summary"]
