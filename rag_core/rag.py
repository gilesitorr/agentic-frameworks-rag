"""Shared RAG engine: from the PDF to retrievable chunks + the list of sections.

It is identical for every implementation, so that the only thing that changes
between frameworks is the framework itself.
"""

import re
import unicodedata
import uuid
from dataclasses import dataclass

import chromadb
from fastembed import TextEmbedding
from pypdf import PdfReader

from . import config

# A heading like "3" or "3.1" followed by a short title in title case.
_SECTION = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+([A-Z][A-Za-z][^\n]{1,60})\s*$")


def _read_pdf(path: str) -> str:
    text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return unicodedata.normalize("NFKC", text)  # normalize ligatures: "ﬁ" -> "fi"


def _sections(text: str) -> list[str]:
    titles = []
    for line in text.splitlines():
        m = _SECTION.match(line)
        # A real heading is short and has no commas or colons (skips figure captions).
        if m and ":" not in m.group(2) and "," not in m.group(2):
            titles.append(f"{m.group(1)} {m.group(2).strip()}")
    return list(dict.fromkeys(titles))  # de-duplicated, in order


def _chunks(text: str) -> list[str]:
    step = config.CHUNK_SIZE - config.CHUNK_OVERLAP
    pieces = (text[i:i + config.CHUNK_SIZE].strip() for i in range(0, len(text), step))
    return [p for p in pieces if p]


@dataclass
class Rag:
    """In-memory semantic index + the document's sections."""

    collection: object
    embedder: TextEmbedding
    sections: list[str]

    def retrieve(self, query: str, k: int = config.TOP_K) -> list[str]:
        """The k most relevant chunks for the query."""
        vector = next(self.embedder.embed([query])).tolist()
        return self.collection.query(query_embeddings=[vector], n_results=k)["documents"][0]


def build_rag(pdf_path: str) -> Rag:
    """Load the PDF and leave the semantic index ready to query."""
    text = _read_pdf(pdf_path)
    chunks = _chunks(text)

    embedder = TextEmbedding(model_name=config.EMBEDDING_MODEL)
    vectors = [vec.tolist() for vec in embedder.embed(chunks)]

    # Unique name: rebuilding the index in the same process won't clash with another collection.
    collection = chromadb.Client().create_collection(f"doc-{uuid.uuid4().hex[:8]}")
    collection.add(ids=[str(i) for i in range(len(chunks))], documents=chunks, embeddings=vectors)

    return Rag(collection, embedder, _sections(text))
