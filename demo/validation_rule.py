"""The validation rule (no OpenAI).

Compares a valid summary with an invalid one to show what part 2 checks.
    python demo/validation_rule.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rag_core import DocumentSummary, SummaryPoint, build_rag, validate_summary

rag = build_rag("data/resnet.pdf")

good = DocumentSummary(points=[
    SummaryPoint(idea="Residual learning.", section="3. Deep Residual Learning"),
    SummaryPoint(idea="Identity shortcuts.", section="3.2. Identity Mapping by Shortcuts"),
    SummaryPoint(idea="ImageNet results.", section="4.1. ImageNet Classification"),
])
bad = DocumentSummary(points=[
    SummaryPoint(idea="Something the model made up.", section="Fake Section"),
])

print("Good summary ->", validate_summary(good, rag.sections) or "valid")
print("Bad summary  ->", validate_summary(bad, rag.sections))
