# Agentic AI en la práctica — RAG con tres frameworks

Demo de la charla **"Agentic AI en la práctica: Explorando Frameworks y sus Capacidades"**
(Demystifying AI Series — José Arenas y Gil Rodríguez).

Resolvemos **el mismo problema** —un RAG que resume el paper de ResNet a partir de
fragmentos recuperados por búsqueda semántica— con tres frameworks, para comparar
cómo cada uno maneja la ejecución, las validaciones y los reintentos.

| Framework | Carpeta | Responsable |
|---|---|---|
| Hugging Face smolagents | `smolagents_impl/` | Gil |
| LangGraph | `langgraph_impl/` | Gil |
| Pydantic AI | `pydantic_impl/` | José |
| Sin framework (baseline) | `baseline/` | referencia |

La comparación es justa porque **lo único que cambia es el framework**: todas usan el
mismo PDF, el mismo stack de RAG y el mismo modelo de generación, definidos en
[`rag_core/config.py`](rag_core/config.py).

## Estructura

```
rag_core/              # motor RAG compartido (igual para todas las implementaciones)
  config.py            # parámetros comunes (chunking, k, modelos)
  loader.py            # PDF -> texto + lista de secciones
  index.py             # troceado -> fastembed -> ChromaDB
  retrieve.py          # búsqueda semántica
smolagents_impl/       # parte 1 (básica) y parte 2 (validación + reintentos)
langgraph_impl/
baseline/
data/                  # aquí va resnet.pdf (ver data/README.md)
```

## La demo tiene dos partes

1. **Básica** — recuperar fragmentos y generar el resumen. Se ve la estructura del
   código de cada framework y qué tendríamos que hacer a mano sin uno (eso lo muestra
   `baseline/`).
2. **Validación + reintentos** — el resumen pasa a ser estructurado: cada punto cita una
   sección. Validamos que cada sección citada **(a)** exista en el documento y **(b)** haya
   estado entre las recuperadas; si no, se reintenta (regenerar o recuperar más).

## Puesta en marcha

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env    # y pon tu OPENAI_API_KEY
```

Descarga el PDF de ResNet en `data/resnet.pdf` (ver [`data/README.md`](data/README.md)).

Corre una implementación **desde la raíz del proyecto**:

```powershell
python -m smolagents_impl.part1_basic
```

## Stack

- **Embeddings:** fastembed (`BAAI/bge-small-en-v1.5`, local)
- **Base vectorial:** ChromaDB (en memoria)
- **Generación:** OpenAI (`gpt-4o-mini`)
