"""Búsqueda semántica: dada una consulta, los TOP_K trozos más relevantes."""

from . import config


def retrieve(query: str, collection, embedder, k: int = config.TOP_K) -> list[str]:
    """Embebe la consulta y pide a ChromaDB los k trozos más cercanos."""
    query_embedding = next(iter(embedder.embed([query]))).tolist()
    result = collection.query(query_embeddings=[query_embedding], n_results=k)
    return result["documents"][0]
