"""Parámetros compartidos. Todas las implementaciones usan estos valores, para
que la única diferencia entre frameworks sea el framework."""

# Embeddings (fastembed, corre local)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Troceado del documento (en caracteres)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Fragmentos a recuperar por consulta
TOP_K = 5

# Generación (OpenAI)
OPENAI_MODEL = "gpt-4o-mini"

# Validación y reintentos (parte 2)
MIN_SECCIONES_CITADAS = 3
MAX_INTENTOS = 3
