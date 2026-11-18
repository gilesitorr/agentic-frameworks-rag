"""rag_core: el 'motor' RAG compartido, idéntico para todas las implementaciones.

Uso típico desde una implementación:

    from rag_core import build_rag
    rag = build_rag("data/resnet.pdf")
    fragmentos = rag.retrieve("¿qué problema resuelve el paper?")
    secciones = rag.sections   # para validar referencias en la parte 2
"""

from dataclasses import dataclass

from . import config
from .index import build_index, chunk_text
from .loader import extract_sections, load_pdf_text
from .retrieve import retrieve as _retrieve

__all__ = ["build_rag", "Rag", "config"]


@dataclass
class Rag:
    """Índice semántico listo para consultar + lista de secciones del documento."""

    collection: object
    embedder: object
    sections: list[str]

    def retrieve(self, query: str, k: int = config.TOP_K) -> list[str]:
        """Devuelve los fragmentos más relevantes para la consulta."""
        return _retrieve(query, self.collection, self.embedder, k)


def build_rag(pdf_path: str) -> Rag:
    """Carga el PDF y deja listo el índice semántico y la lista de secciones."""
    text = load_pdf_text(pdf_path)
    sections = extract_sections(text)
    collection, embedder = build_index(chunk_text(text))
    return Rag(collection=collection, embedder=embedder, sections=sections)
