"""Shared parameters. Every implementation uses these values, so that the only
difference between frameworks is the framework itself."""

import pathlib

# Embeddings (fastembed, runs locally)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# fastembed looks for the model here. It is vendored in the repo (.models/), so
# the demo runs offline on any OS — no HuggingFace download needed.
CACHE_DIR = pathlib.Path(__file__).resolve().parent.parent / ".models"

# Document chunking (in characters)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Chunks retrieved per query
TOP_K = 5

# Generation (OpenAI)
OPENAI_MODEL = "gpt-4o-mini"

# Validation and retries (part 2)
MIN_SECTIONS_CITED = 3
MAX_ATTEMPTS = 3
