"""Demo 04 — LangGraph, parte 1 (básica).
    python demo/04_langgraph_basico.py
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

runpy.run_module("langgraph_impl.part1_basic", run_name="__main__")
