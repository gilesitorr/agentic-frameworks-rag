"""Demo 08 — Force a retry live.

Raises the minimum number of sections so the first attempt fails and you can see
the fail → retry → fix cycle. The change is temporary (only this run).
    python demo/08_force_retry.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rag_core import config

config.MIN_SECTIONS_CITED = 8   # temporary, just for this demo

from baseline.summarize_plain import main

main()
