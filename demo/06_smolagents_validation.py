"""Demo 06 — smolagents, part 2 (validation + retries).
    python demo/06_smolagents_validation.py
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

runpy.run_module("smolagents_impl.part2_validation", run_name="__main__")
