"""Shared RAG engine: from the PDF to retrievable chunks + the list of sections.

It is identical for every implementation: what differs is how each one orchestrates
retrieval and generation on top of it.
"""

import re
import uuid
from dataclasses import dataclass

import chromadb
import pymupdf4llm
from fastembed import TextEmbedding

from . import config

# pymupdf4llm writes PDF headings as Markdown, e.g. "## **3.1. Residual Learning**".
_HEADING = re.compile(r"^#{1,3} \**([A-Z0-9].*?)\**\s*$")
_SKIP = {"References", "Acknowledgments", "Acknowledgements"}  # not worth indexing
# Text pymupdf4llm extracts from inside figures (axis labels, tick values): noise for retrieval.
_PICTURE_TEXT = re.compile(r"<!-- Start of picture text -->.*?<!-- End of picture text -->", re.S)


def _split(pdf_path: str) -> tuple[list[str], list[str]]:
    """Split the PDF into section-labeled chunks: "[3.1. Residual Learning] ...".

    Paragraphs are packed into chunks of up to CHUNK_SIZE characters, and a new
    chunk starts at every heading, so each chunk belongs to exactly one section.
    Only sections with at least one chunk are returned, so every valid citation
    points to text the RAG can retrieve.
    """
    markdown = _PICTURE_TEXT.sub("", pymupdf4llm.to_markdown(pdf_path, use_ocr=False))
    sections, chunks, section, buffer = [], [], "Front matter", ""

    def flush() -> None:
        if buffer.strip() and section not in _SKIP:
            chunks.append(f"[{section}] {buffer.strip()}")
            if section not in sections:
                sections.append(section)

    for paragraph in markdown.split("\n\n"):
        if heading := _HEADING.match(paragraph.strip()):
            flush()
            section, buffer = heading[1], ""
        elif len(buffer) + len(paragraph) > config.CHUNK_SIZE:
            flush()
            buffer = paragraph
        else:
            buffer += "\n\n" + paragraph
    flush()
    return chunks, sections


@dataclass
class Rag:
    """In-memory semantic index + the document's sections."""

    collection: object
    embedder: TextEmbedding
    sections: list[str]

    def retrieve(self, query: str, k: int = config.TOP_K) -> list[str]:
        """The k most relevant chunks for the query, each prefixed with its section."""
        vector = next(self.embedder.query_embed(query)).tolist()
        return self.collection.query(query_embeddings=[vector], n_results=k)["documents"][0]


def build_rag(pdf_path: str) -> Rag:
    """Load the PDF and leave the semantic index ready to query."""
    chunks, sections = _split(pdf_path)

    embedder = TextEmbedding(model_name=config.EMBEDDING_MODEL, cache_dir=str(config.CACHE_DIR))
    vectors = [vec.tolist() for vec in embedder.embed(chunks)]

    # Unique name: rebuilding the index in the same process won't clash with another collection.
    collection = chromadb.Client().create_collection(f"doc-{uuid.uuid4().hex[:8]}")
    collection.add(ids=[str(i) for i in range(len(chunks))], documents=chunks, embeddings=vectors)

    return Rag(collection, embedder, sections)
