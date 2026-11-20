"""Demo 04 — LangGraph, part 1 (basic).
    python demo/04_langgraph_basic.py
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

runpy.run_module("langgraph_impl.part1_basic", run_name="__main__")
