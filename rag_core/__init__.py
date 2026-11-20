"""rag_core: shared RAG engine + part 2 schema and validation."""

from . import config
from .rag import Rag, build_rag
from .schema import DocumentSummary, SummaryPoint
from .validation import validate_summary

__all__ = ["config", "build_rag", "Rag", "DocumentSummary", "SummaryPoint", "validate_summary"]
