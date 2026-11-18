"""Demo 08 — Forzar un reintento en vivo.

Sube el mínimo de secciones para que el primer intento falle y se vea el ciclo
fallar → reintentar → corregir. El cambio es temporal (solo en esta corrida).
    python demo/08_forzar_reintento.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rag_core import config

config.MIN_SECCIONES_CITADAS = 8   # temporal, solo para esta demo

from baseline.summarize_plain import main

main()
