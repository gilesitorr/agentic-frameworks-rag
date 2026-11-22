"""Shared RAG engine: from the PDF to retrievable chunks + the list of sections.

It is identical for every implementation: what differs is how each one orchestrates
retrieval and generation on top of it.
"""

import hashlib
import json
import pathlib
import re
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
    """Semantic index (saved in .chroma/) + the document's sections."""

    collection: object
    embedder: TextEmbedding
    sections: list[str]

    def retrieve(self, query: str, k: int = config.TOP_K) -> list[str]:
        """The k most relevant chunks for the query, each prefixed with its section."""
        vector = next(self.embedder.query_embed(query)).tolist()
        return self.collection.query(query_embeddings=[vector], n_results=k)["documents"][0]


def _fingerprint(pdf_path: str) -> str:
    """Changes whenever the PDF, this chunking code or the index settings change."""
    digest = hashlib.sha256()
    digest.update(pathlib.Path(pdf_path).read_bytes())
    digest.update(pathlib.Path(__file__).read_bytes())
    digest.update(f"{config.EMBEDDING_MODEL}|{config.CHUNK_SIZE}".encode())
    return digest.hexdigest()[:16]


def build_rag(pdf_path: str, rebuild: bool = False) -> Rag:
    """Leave the semantic index ready to query.

    The first run parses, chunks and embeds the PDF and saves the index in .chroma/.
    Later runs load it from disk, unless the fingerprint changed or rebuild=True.
    """
    embedder = TextEmbedding(model_name=config.EMBEDDING_MODEL, cache_dir=str(config.CACHE_DIR))
    client = chromadb.PersistentClient(path=str(config.INDEX_DIR))
    name = f"doc-{_fingerprint(pdf_path)}"

    saved = {c.name for c in client.list_collections()}
    if name in saved and not rebuild:
        collection = client.get_collection(name)
        return Rag(collection, embedder, json.loads(collection.metadata["sections"]))

    for old in saved:  # outdated indexes (or this one, on rebuild)
        client.delete_collection(old)
    chunks, sections = _split(pdf_path)
    vectors = [vec.tolist() for vec in embedder.embed(chunks)]
    collection = client.create_collection(name, metadata={"sections": json.dumps(sections)})
    collection.add(ids=[str(i) for i in range(len(chunks))], documents=chunks, embeddings=vectors)
    return Rag(collection, embedder, sections)
