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

# Pre-download the embedding model (run once before the talk)
warmup:
    uv run python -c "from rag_core import build_rag; build_rag('data/resnet.pdf'); print('ready')"

# 01 — RAG internals: sections + semantic search (offline, no OpenAI)
rag-internals:
    uv run python demo/01_rag_internals.py

# 02 — The validation rule: good vs. bad summary (offline, no OpenAI)
validation:
    uv run python demo/02_validation.py

# 03 — smolagents, part 1 (basic)
smolagents-1:
    uv run python -m smolagents_impl.part1_basic

# 04 — LangGraph, part 1 (basic)
langgraph-1:
    uv run python -m langgraph_impl.part1_basic

# 05 — Baseline: the same flow with no framework
baseline:
    uv run python -m baseline.summarize_plain

# 06 — smolagents, part 2 (validation + retries)
smolagents-2:
    uv run python -m smolagents_impl.part2_validation

# 07 — LangGraph, part 2 (validation + retries)
langgraph-2:
    uv run python -m langgraph_impl.part2_validation

# 08 — Force a retry live (temporary high threshold)
force-retry:
    uv run python demo/08_force_retry.py
