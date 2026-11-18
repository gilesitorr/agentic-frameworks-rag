"""Demo 03 — smolagents, parte 1 (básica).
    python demo/03_smolagents_basico.py
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

runpy.run_module("smolagents_impl.part1_basic", run_name="__main__")
