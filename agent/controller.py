"""
Agent Controller — Pipeline Orchestrator

Orchestrates the full 7-phase lifecycle:
  Listen → Understand → Reason → Recommend → Confirm → Execute → Learn

Connects all modules:
  Module 2 (NLU) → Module 3 (Intent) → Module 4 (Workflow) →
  Module 5 (Confirm) → Module 6 (Execute) → Module 7 (Learn)

Module 8 (Knowledge Base) underpins Modules 4 and 7.
"""

import time

from nlu.preprocessor import NLUPreprocessor
from llm.gemini_client import GeminiIntentClassifier
from validation.intent_validator import validate_intent
from workflows.workflow_builder import build_workflow
from confirmation.confirm import request_confirmation
from execution.executor import execute_workflow
from knowledge.database import KnowledgeBase
from learning.preference_engine import PreferenceLearningEngine


class AgentController:

    def __init__(self):
        self.nlu = NLUPreprocessor()
        self.classifier = GeminiIntentClassifier()
        self.kb = KnowledgeBase()
        self.learner = PreferenceLearningEngine(self.kb)

    def process_text(self, user_text):

        pipeline_start = time.time()

        # ----------------------------------------------------------
        # Step 1 — NLU Preprocessing (Module 2)
        # ----------------------------------------------------------
        print("\n[1] NLU preprocessing...")
        nlu_result = self.nlu.process(user_text)

        print(f"    Original : \"{nlu_result['original_text']}\"")
        print(f"    Cleaned  : \"{nlu_result['cleaned_text']}\"")
        print(f"    Normalized: \"{nlu_result['normalized_text']}\"")

        if nlu_result["transformations"]:
            print(f"    Steps    : {', '.join(nlu_result['transformations'])}")

        if not nlu_result["is_valid"]:
            print("\n❌ NLU: no actionable content after preprocessing.")
            return {
                "status": "empty_input",
                "nlu": nlu_result,
            }

        processed_text = nlu_result["normalized_text"]

        # ----------------------------------------------------------
        # Step 2 — Intent Classification (Module 3)
        # ----------------------------------------------------------
        print("\n[2] Classifying intent...")
        intent_result = self.classifier.classify(processed_text)

        print(f"    Intent   : {intent_result['intent']}")
        print(f"    Reasoning: {intent_result.get('reasoning', '')}")

        # ----------------------------------------------------------
        # Step 3 — Validation
        # ----------------------------------------------------------
        print("\n[3] Validating...")
        validate_intent(intent_result)
        print("    Validation successful! ✅")

        # ----------------------------------------------------------
        # Step 4 — Workflow Recommendation (Module 4)
        #          Now KB-driven via the learner
        # ----------------------------------------------------------
        print("\n[4] Building workflow...")

        # Check for temporal suggestion
        temporal_hint = self.learner.get_temporal_suggestion()
        if temporal_hint and temporal_hint != intent_result["intent"]:
            print(f"    💡 Temporal hint: you usually do {temporal_hint} at this time")

        workflow = build_workflow(intent_result, learner=self.learner)

        print(f"    Description: {workflow['description']}")
        print(f"    Steps ({len(workflow['steps'])}):")
        for i, step in enumerate(workflow["steps"], 1):
            target = step.get("target", step.get("type", step.get("query", step.get("name", ""))))
            print(f"      {i}. {step['action']}: {target}")

        # ----------------------------------------------------------
        # E2E Latency measurement (voice-end → workflow displayed)
        # ----------------------------------------------------------
        e2e_latency_ms = (time.time() - pipeline_start) * 1000
        print(f"\n    ⏱️  E2E Latency: {e2e_latency_ms:.0f}ms")

        # ----------------------------------------------------------
        # Step 5 — User Confirmation (Module 5)
        # ----------------------------------------------------------
        print("\n[5] Requesting confirmation...")
        confirmation = request_confirmation(workflow)

        if not confirmation["confirmed"]:
            print("\n❌ User rejected the workflow.")

            # Module 7: Record rejected interaction
            self.learner.record_interaction(
                nlu_result, intent_result, workflow,
                confirmed=False, executed=False,
            )

            return {
                "status": "cancelled",
                "nlu": nlu_result,
                "workflow": workflow,
                "e2e_latency_ms": e2e_latency_ms,
            }

        print("\n✅ User confirmed the workflow.")

        # ----------------------------------------------------------
        # Step 6 — Execution (Module 6)
        # ----------------------------------------------------------
        print("\n[6] Executing workflow...")

        execution_error = None
        try:
            execute_workflow(workflow)
            executed = True
            print("\n✅ Workflow completed.")
        except Exception as e:
            executed = True  # attempted
            execution_error = str(e)
            print(f"\n❌ Execution error: {e}")

        # ----------------------------------------------------------
        # Step 7 — Preference Learning (Module 7)
        # ----------------------------------------------------------
        print("\n[7] Recording interaction for learning...")
        self.learner.record_interaction(
            nlu_result, intent_result, workflow,
            confirmed=True,
            executed=executed,
            error=execution_error,
        )

        # Show acceptance trend
        trend = self.learner.get_acceptance_trend()
        print(f"    Acceptance rate: {trend['rate']:.0%} "
              f"({trend['accepted']}/{trend['total']}) — {trend['trend']}")

        return {
            "status": "completed" if execution_error is None else "error",
            "nlu": nlu_result,
            "workflow": workflow,
            "e2e_latency_ms": e2e_latency_ms,
            "execution_error": execution_error,
        }
