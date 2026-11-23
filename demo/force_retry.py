"""Force a retry live (deterministic): the first attempt always fails, so the
fail -> retry -> fix cycle shows the same way across all four frameworks.
    python demo/force_retry.py [baseline|smolagents|langgraph|pydantic]
"""

import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rag_core.validation as validation

_real_validate = validation.validate_summary
_state = {"first": True}


def _forced_first_failure(summary, sections):
    if _state["first"]:  # fail the first attempt on purpose
        _state["first"] = False
        return ["(demo) forced first-attempt failure to show the retry loop"]
    return _real_validate(summary, sections)  # from the 2nd attempt on, the real rule


validation.validate_summary = _forced_first_failure

VALIDATION = {
    "baseline": "baseline.summarize_plain",
    "smolagents": "smolagents_impl.part2_validation",
    "langgraph": "langgraph_impl.part2_validation",
    "pydantic": "pydantic_impl.part2_validation",
}

runpy.run_module(VALIDATION[sys.argv[1] if len(sys.argv) > 1 else "baseline"], run_name="__main__")
