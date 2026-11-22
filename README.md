# Agentic AI in practice — RAG with three frameworks

Demo for the talk *"Agentic AI in practice"* (José Arenas and Gil Rodríguez).

We solve **the same problem** —a RAG that summarizes the ResNet paper— with three
frameworks, to compare how they handle execution, validation and retries.
Every implementation uses the same PDF, RAG and model (see
[`rag_core/config.py`](rag_core/config.py)). Besides the framework, they also differ in
**pattern**, each following the way its framework is typically used:

- **Workflow:** your code runs one fixed query, then a single LLM call writes the summary.
- **Agent:** the LLM gets a `search_document` tool and decides what to search, and how often,
  before writing the summary.

| Implementation | Folder | Pattern |
|---|---|---|
| No framework | `baseline/` | workflow |
| smolagents | `smolagents_impl/` | agent |
| Pydantic AI | `pydantic_impl/` | agent |
| LangGraph | `langgraph_impl/` | workflow |

Each demo has two parts: **basic** (retrieve and summarize) and **validation +
retries** (the summary cites sections of the document; if validation fails, it retries).
The in-depth comparison is in [`docs/comparison.md`](docs/comparison.md), and the flow
diagrams are in [`docs/diagrams.md`](docs/diagrams.md).

## Usage

We use [uv](https://docs.astral.sh/uv/) for the environment and
[just](https://just.systems/) for the demo recipes. `just` is a project dependency, so
`uv sync` installs it into the environment: no separate install needed.

```powershell
uv sync                   # creates the environment and installs everything (reads pyproject.toml)
cp .env.example .env      # add your OPENAI_API_KEY   (Windows: copy .env.example .env)
```

The paper (`data/resnet.pdf`) is in the repo. The embedding model is downloaded from
HuggingFace into `.models/` on the first run (`uv run just warmup` does it ahead of time); after
that the RAG runs offline. Run any demo with a recipe (list them all with `uv run just`):

```powershell
uv run just rag-internals         # offline: PDF sections + semantic search
uv run just smolagents-2          # smolagents, part 2 (validation + retries)
uv run just langgraph-2           # LangGraph, part 2 (validation + retries)
uv run just pydantic-validation   # Pydantic AI, part 2 (validation + retries)
uv run just force-retry pydantic  # force a retry live (baseline, smolagents, langgraph or pydantic)
```

If you have `just` installed globally, you can drop the `uv run` prefix. Each recipe just
wraps `uv run ...`, so you can always run the module directly instead,
e.g. `uv run python -m smolagents_impl.part1_basic`.

## Stack

pymupdf4llm (PDF parsing) · fastembed (embeddings) · ChromaDB (vector store) ·
OpenAI `gpt-4o-mini` (generation)

## The shared RAG (`rag_core`)

`build_rag()` converts the PDF to Markdown with pymupdf4llm, splits it at its headings,
and packs each section's paragraphs into chunks of up to 1000 characters. Every chunk is
labeled with its section (`[3.1. Residual Learning] ...`), so the model sees where each
passage comes from and can cite it. References are not indexed.
