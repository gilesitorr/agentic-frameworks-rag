"""Demo 03 — smolagents, part 1 (basic).
    python demo/03_smolagents_basic.py
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

runpy.run_module("smolagents_impl.part1_basic", run_name="__main__")
