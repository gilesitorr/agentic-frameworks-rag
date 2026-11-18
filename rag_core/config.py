"""Parámetros compartidos del RAG.

Todas las implementaciones (smolagents, LangGraph y, idealmente, Pydantic AI)
usan ESTOS valores. Así la única diferencia entre frameworks es el framework
mismo, no el RAG. Si José ajusta algo aquí, lo copiamos tal cual.
"""

# --- Embeddings (fastembed) ---
# Modelo por defecto de fastembed: pequeño, rápido y corre local (sin API).
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# --- Troceado del documento ---
# En caracteres, para que sea fácil de explicar en la charla.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# --- Recuperación ---
# Cuántos fragmentos devolvemos por cada búsqueda.
TOP_K = 5

# --- Generación (OpenAI) ---
# Mismo modelo en las tres implementaciones.
OPENAI_MODEL = "gpt-4o-mini"

# --- Validación y reintentos (parte 2) ---
# Mínimo de secciones distintas que debe citar un resumen para considerarse válido.
MIN_SECCIONES_CITADAS = 3
# Máximo de reintentos cuando la validación falla.
MAX_INTENTOS = 3
