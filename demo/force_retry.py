"""Force a retry live.

Raises the minimum number of sections so the first attempt fails and you can see
the fail → retry → fix cycle. The change is temporary (only this run).
    python demo/force_retry.py [baseline|smolagents|langgraph|pydantic]
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rag_core import config

VALIDATION = {
    "baseline": "baseline.summarize_plain",
    "smolagents": "smolagents_impl.part2_validation",
    "langgraph": "langgraph_impl.part2_validation",
    "pydantic": "pydantic_impl.part2_validation",
}

config.MIN_SECTIONS_CITED = 8   # temporary, just for this run

runpy.run_module(VALIDATION[sys.argv[1] if len(sys.argv) > 1 else "baseline"], run_name="__main__")
