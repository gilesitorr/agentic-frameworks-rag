"""Troceado + embeddings (fastembed) + almacenamiento en ChromaDB."""

import chromadb
from fastembed import TextEmbedding

from . import config


def chunk_text(text: str) -> list[str]:
    """Divide el texto en trozos de CHUNK_SIZE caracteres con solape CHUNK_OVERLAP."""
    chunks: list[str] = []
    step = config.CHUNK_SIZE - config.CHUNK_OVERLAP
    for start in range(0, len(text), step):
        chunk = text[start:start + config.CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def build_index(chunks: list[str]):
    """Calcula los embeddings de los trozos y los guarda en una colección de ChromaDB.

    Devuelve (collection, embedder); el embedder se reutiliza para las consultas.
    """
    embedder = TextEmbedding(model_name=config.EMBEDDING_MODEL)
    embeddings = [vector.tolist() for vector in embedder.embed(chunks)]

    client = chromadb.Client()                    # cliente en memoria: se reconstruye cada corrida
    collection = client.create_collection("doc")
    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings,
    )
    return collection, embedder
