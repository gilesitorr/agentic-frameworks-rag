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

# smolagents, part 1 (basic)
smolagents-1:
    uv run python -m smolagents_impl.part1_basic

# LangGraph, part 1 (basic)
langgraph-1:
    uv run python -m langgraph_impl.part1_basic

# Pydantic AI, part 1 (basic)
pydantic-basic:
    uv run python -m pydantic_impl.part1_basic

# smolagents, part 2 (validation + retries)
smolagents-2:
    uv run python -m smolagents_impl.part2_validation

# LangGraph, part 2 (validation + retries)
langgraph-2:
    uv run python -m langgraph_impl.part2_validation

# Pydantic AI, part 2 (validation + retries)
pydantic-validation:
    uv run python -m pydantic_impl.part2_validation

# Force a retry live (temporary high threshold): baseline, smolagents, langgraph or pydantic
force-retry framework="baseline":
    uv run python demo/force_retry.py {{framework}}
