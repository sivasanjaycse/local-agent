"""
Quick smoke test for the refactored Module 3 pipeline.

Sends a few text commands through the full pipeline
(NLU → Intent → Validate → Workflow) WITHOUT execution,
to verify the new high-level intent taxonomy works end-to-end.
"""

import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nlu.preprocessor import NLUPreprocessor
from llm.gemini_client import GeminiIntentClassifier
from validation.intent_validator import validate_intent
from workflows.workflow_builder import build_workflow

import json


nlu = NLUPreprocessor()
classifier = GeminiIntentClassifier()

TEST_COMMANDS = [
    "Open VS Code",
    "Let's do vibe coding",
    "Search YouTube for Python tutorials",
    "Take a screenshot",
    "Create a folder called TestProject",
    "Open Spotify",
    "Open Notepad",
    "I have a meeting to join",
]


print("=" * 60)
print("  Module 3 Smoke Test — High-Level Intents")
print("=" * 60)

for cmd in TEST_COMMANDS:

    print(f"\n{'—' * 60}")
    print(f"  Command: \"{cmd}\"")
    print(f"{'—' * 60}")

    # NLU
    nlu_result = nlu.process(cmd)
    processed = nlu_result["normalized_text"]
    print(f"  NLU output: \"{processed}\"")

    # Intent Classification
    try:
        intent_result = classifier.classify(processed)
    except Exception as e:
        print(f"  ❌ Classification error: {e}")
        continue

    print(f"  Intent    : {intent_result['intent']}")
    print(f"  Reasoning : {intent_result['reasoning']}")
    print(f"  Entities  : {json.dumps(intent_result['entities'], indent=2)}")

    # Validation
    try:
        validate_intent(intent_result)
        print(f"  Validation: ✅")
    except ValueError as e:
        print(f"  Validation: ❌ {e}")
        continue

    # Workflow Building
    workflow = build_workflow(intent_result)
    print(f"  Workflow  : {workflow['description']}")
    print(f"  Steps ({len(workflow['steps'])}):")
    for i, step in enumerate(workflow["steps"], 1):
        print(f"    {i}. {step['action']}: {step.get('target', step.get('type', step.get('query', step.get('name', ''))))}")


print(f"\n{'=' * 60}")
print(f"  Smoke test complete!")
print(f"{'=' * 60}")
