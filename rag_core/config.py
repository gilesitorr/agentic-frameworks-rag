"""Shared parameters. Every implementation uses these values, so the PDF, the RAG
and the model are the same everywhere."""

import pathlib

# Embeddings (fastembed, runs locally)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# fastembed downloads the model here on the first run (git-ignored); after that
# the RAG runs offline.
CACHE_DIR = pathlib.Path(__file__).resolve().parent.parent / ".models"

# The vector index is saved here (git-ignored) so later runs skip parsing and embedding.
# It is rebuilt automatically when the PDF, the chunking code or these settings change.
INDEX_DIR = pathlib.Path(__file__).resolve().parent.parent / ".chroma"

# Document chunking (in characters)
CHUNK_SIZE = 1000  # max per chunk; chunks never cross a section boundary

# Chunks retrieved per query
TOP_K = 5

# Generation (OpenAI)
OPENAI_MODEL = "gpt-4o-mini"

# Validation and retries (validation demos)
MIN_SECTIONS_CITED = 3
MAX_ATTEMPTS = 3
