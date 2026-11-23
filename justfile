# Demo recipes for the talk. Run `just` to list them.
# Everything runs through uv, so no venv activation is needed.
# just is a project dependency: after `uv sync`, run recipes with `uv run just <recipe>`.

# Run recipes in PowerShell on Windows, and force UTF-8 so smolagents'
# rich output never trips the legacy cp1252 console.
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
export PYTHONUTF8 := "1"

# List available recipes
default:
    @just --list

# Create the environment and install dependencies
setup:
    uv sync

# Ingest the PDF: build and save the index if it's missing or outdated, otherwise just load it
ingest:
    uv run python -c "from rag_core import build_rag; r = build_rag('data/resnet.pdf'); print(f'index ready: {r.collection.count()} chunks, {len(r.sections)} sections')"

alias warmup := ingest

# Rebuild the saved index from scratch (it also rebuilds by itself when the PDF or chunking changes)
reindex:
    uv run python -c "from rag_core import build_rag; build_rag('data/resnet.pdf', rebuild=True); print('rebuilt')"

# RAG internals: sections + semantic search (offline, no OpenAI)
rag-internals:
    uv run python demo/rag_internals.py

# The validation rule: good vs. bad summary (offline, no OpenAI)
validation:
    uv run python demo/validation_rule.py

# Baseline: the same flow with no framework
baseline:
    uv run python -m baseline.summarize_plain

# smolagents, basic
smolagents-basic:
    uv run python -m smolagents_impl.part1_basic

# LangGraph, basic
langgraph-basic:
    uv run python -m langgraph_impl.part1_basic

# Pydantic AI, basic
pydantic-basic:
    uv run python -m pydantic_impl.part1_basic

# smolagents, validation (structured output + retries)
smolagents-validation:
    uv run python -m smolagents_impl.part2_validation

# LangGraph, validation (structured output + retries)
langgraph-validation:
    uv run python -m langgraph_impl.part2_validation

# Pydantic AI, validation (structured output + retries)
pydantic-validation:
    uv run python -m pydantic_impl.part2_validation

# Force a retry live (temporary high threshold): baseline, smolagents, langgraph or pydantic
force-retry framework="baseline":
    uv run python demo/force_retry.py {{framework}}
