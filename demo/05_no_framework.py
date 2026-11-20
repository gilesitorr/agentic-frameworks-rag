"""Demo 05 — Baseline: the same flow WITHOUT a framework.
    python demo/05_no_framework.py
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

runpy.run_module("baseline.summarize_plain", run_name="__main__")
