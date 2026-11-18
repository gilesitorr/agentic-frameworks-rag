# Agentic AI en la práctica — RAG con tres frameworks

Demo de la charla *"Agentic AI en la práctica"* (José Arenas y Gil Rodríguez).

Resolvemos **el mismo problema** —un RAG que resume el paper de ResNet— con tres
frameworks, para comparar cómo manejan la ejecución, la validación y los reintentos.
Lo único que cambia entre implementaciones es **el framework**: mismo PDF, mismo RAG y
mismo modelo (ver [`rag_core/config.py`](rag_core/config.py)).

| Framework | Carpeta |
|---|---|
| smolagents | `smolagents_impl/` |
| LangGraph | `langgraph_impl/` |
| Pydantic AI | `pydantic_impl/` (José) |
| Sin framework | `baseline/` |

Cada demo tiene dos partes: **básica** (recuperar y resumir) y **validación +
reintentos** (el resumen cita secciones del documento; si la validación falla, se
reintenta). La comparación a fondo está en [`docs/comparacion.md`](docs/comparacion.md).

## Uso

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env    # pon tu OPENAI_API_KEY
```

Descarga el paper en `data/resnet.pdf` (ver [`data/README.md`](data/README.md)) y corre,
desde la raíz del proyecto:

```powershell
python -m smolagents_impl.part1_basic
python -m langgraph_impl.part2_validation
python -m baseline.summarize_plain
```

## Stack

fastembed (embeddings) · ChromaDB (base vectorial) · OpenAI `gpt-4o-mini` (generación)
