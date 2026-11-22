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

# Sanity check: build the index (downloads the embedding model into .models/ on first run)
warmup:
    uv run python -c "from rag_core import build_rag; build_rag('data/resnet.pdf'); print('ready')"

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
    uv run python -m smolagents_impl.basic

# LangGraph, basic
langgraph-basic:
    uv run python -m langgraph_impl.basic

# Pydantic AI, basic
pydantic-basic:
    uv run python -m pydantic_impl.basic

# smolagents, validation (structured output + retries)
smolagents-validation:
    uv run python -m smolagents_impl.validation

# LangGraph, validation (structured output + retries)
langgraph-validation:
    uv run python -m langgraph_impl.validation

# Pydantic AI, validation (structured output + retries)
pydantic-validation:
    uv run python -m pydantic_impl.validation

# Force a retry live (temporary high threshold): baseline, smolagents, langgraph or pydantic
force-retry framework="baseline":
    uv run python demo/force_retry.py {{framework}}
