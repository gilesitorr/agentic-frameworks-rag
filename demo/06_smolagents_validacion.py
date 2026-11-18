"""Demo 06 — smolagents, parte 2 (validación + reintentos).
    python demo/06_smolagents_validacion.py
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

runpy.run_module("smolagents_impl.part2_validation", run_name="__main__")
