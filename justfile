# Demo recipes for the talk. Run `just` to list them.
# Everything runs through uv, so no venv activation is needed.
# Install just: https://just.systems/  (e.g. `winget install Casey.Just`)

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

# Sanity check: load the vendored embedding model (it lives in .models/)
warmup:
    uv run python -c "from rag_core import build_rag; build_rag('data/resnet.pdf'); print('ready')"

# RAG internals: sections + semantic search (offline, no OpenAI)
rag-internals:
    uv run python demo/rag_internals.py

# The validation rule: good vs. bad summary (offline, no OpenAI)
validation:
    uv run python demo/validation_rule.py

# smolagents, part 1 (basic)
smolagents-1:
    uv run python -m smolagents_impl.part1_basic

# LangGraph, part 1 (basic)
langgraph-1:
    uv run python -m langgraph_impl.part1_basic

# Baseline: the same flow with no framework
baseline:
    uv run python -m baseline.summarize_plain

# smolagents, part 2 (validation + retries)
smolagents-2:
    uv run python -m smolagents_impl.part2_validation

# LangGraph, part 2 (validation + retries)
langgraph-2:
    uv run python -m langgraph_impl.part2_validation

# Force a retry live (temporary high threshold)
force-retry:
    uv run python demo/force_retry.py
