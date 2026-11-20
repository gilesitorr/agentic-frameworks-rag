# Agentic AI in practice — RAG with three frameworks

Demo for the talk *"Agentic AI in practice"* (José Arenas and Gil Rodríguez).

We solve **the same problem** —a RAG that summarizes the ResNet paper— with three
frameworks, to compare how they handle execution, validation and retries.
The only thing that changes between implementations is **the framework**: same PDF, same
RAG and same model (see [`rag_core/config.py`](rag_core/config.py)).

| Framework | Folder |
|---|---|
| smolagents | `smolagents_impl/` |
| LangGraph | `langgraph_impl/` |
| Pydantic AI | `pydantic_impl/` (José) |
| No framework | `baseline/` |

Each demo has two parts: **basic** (retrieve and summarize) and **validation +
retries** (the summary cites sections of the document; if validation fails, it retries).
The in-depth comparison is in [`docs/comparison.md`](docs/comparison.md), and the flow
diagrams are in [`docs/diagrams.md`](docs/diagrams.md).

## Usage

We use [uv](https://docs.astral.sh/uv/) for the environment and
[just](https://just.systems/) for the demo recipes.

```powershell
uv sync                   # creates the environment and installs everything (reads pyproject.toml)
cp .env.example .env      # add your OPENAI_API_KEY   (Windows: copy .env.example .env)
```

The paper (`data/resnet.pdf`) and the embedding model (`.models/`) are vendored in the repo,
so the demo runs offline on any OS — no HuggingFace download needed. Run any demo with a
recipe (list them all with `just`):

```powershell
just rag-internals     # offline: PDF sections + semantic search
just smolagents-2      # smolagents, part 2 (validation + retries)
just langgraph-2       # LangGraph, part 2 (validation + retries)
just force-retry       # force a retry live
```

Each recipe just wraps `uv run ...`, so you can always run the module directly instead,
e.g. `uv run python -m smolagents_impl.part1_basic`.

## Stack

fastembed (embeddings) · ChromaDB (vector store) · OpenAI `gpt-4o-mini` (generation)
