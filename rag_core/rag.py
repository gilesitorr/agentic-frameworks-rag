"""Motor RAG compartido: del PDF a fragmentos recuperables + lista de secciones.

Es idéntico para todas las implementaciones, para que lo único que cambie entre
frameworks sea el framework.
"""

import re
import unicodedata
import uuid
from dataclasses import dataclass

import chromadb
from fastembed import TextEmbedding
from pypdf import PdfReader

from . import config

# Encabezado tipo "3" o "3.1" seguido de un título corto en mayúscula.
_SECCION = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+([A-Z][A-Za-z][^\n]{1,60})\s*$")


def _leer_pdf(path: str) -> str:
    texto = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return unicodedata.normalize("NFKC", texto)  # normaliza ligaduras: "ﬁ" -> "fi"


def _secciones(texto: str) -> list[str]:
    titulos = []
    for linea in texto.splitlines():
        m = _SECCION.match(linea)
        # Un encabezado real es corto y sin comas ni dos puntos (descarta pies de figura).
        if m and ":" not in m.group(2) and "," not in m.group(2):
            titulos.append(f"{m.group(1)} {m.group(2).strip()}")
    return list(dict.fromkeys(titulos))  # sin duplicados, en orden


def _trozos(texto: str) -> list[str]:
    paso = config.CHUNK_SIZE - config.CHUNK_OVERLAP
    trozos = (texto[i:i + config.CHUNK_SIZE].strip() for i in range(0, len(texto), paso))
    return [t for t in trozos if t]


@dataclass
class Rag:
    """Índice semántico en memoria + secciones del documento."""

    collection: object
    embedder: TextEmbedding
    sections: list[str]

    def retrieve(self, query: str, k: int = config.TOP_K) -> list[str]:
        """Los k fragmentos más relevantes para la consulta."""
        vector = next(self.embedder.embed([query])).tolist()
        return self.collection.query(query_embeddings=[vector], n_results=k)["documents"][0]


def build_rag(pdf_path: str) -> Rag:
    """Carga el PDF y deja el índice semántico listo para consultar."""
    texto = _leer_pdf(pdf_path)
    trozos = _trozos(texto)

    embedder = TextEmbedding(model_name=config.EMBEDDING_MODEL)
    vectores = [vec.tolist() for vec in embedder.embed(trozos)]

    # Nombre único: reconstruir el índice en el mismo proceso no choca con otra colección.
    collection = chromadb.Client().create_collection(f"doc-{uuid.uuid4().hex[:8]}")
    collection.add(ids=[str(i) for i in range(len(trozos))], documents=trozos, embeddings=vectores)

    return Rag(collection, embedder, _secciones(texto))
