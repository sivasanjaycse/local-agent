from nlu.preprocessor import NLUPreprocessor
from llm.gemini_client import GeminiIntentClassifier
from validation.intent_validator import validate_intent
from workflows.workflow_builder import build_workflow
from confirmation.confirm import request_confirmation
from execution.executor import execute_workflow


class AgentController:

    def __init__(self):
        self.nlu = NLUPreprocessor()
        self.classifier = GeminiIntentClassifier()

    def process_text(self, user_text):

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

        print("\n[3] Gemini result:")
        print(intent_result)

        # ----------------------------------------------------------
        # Step 3 — Validation
        # ----------------------------------------------------------
        print("\n[4] Validating...")
        validate_intent(intent_result)

        print("Validation successful! ✅")

        # ----------------------------------------------------------
        # Step 4 — Workflow Building (Module 4)
        # ----------------------------------------------------------
        print("\n[5] Building workflow...")
        workflow = build_workflow(intent_result)

        print("Workflow:")
        print(workflow)

        # ----------------------------------------------------------
        # Step 5 — User Confirmation (Module 5)
        # ----------------------------------------------------------
        print("\n[6] Requesting confirmation...")
        confirmation = request_confirmation(workflow)

        if not confirmation["confirmed"]:
            print("\n❌ User rejected the workflow.")
            print("Execution cancelled.")
            return {
                "status": "cancelled",
                "nlu": nlu_result,
                "workflow": workflow,
            }

        print("\n✅ User confirmed the workflow.")

        # ----------------------------------------------------------
        # Step 6 — Execution (Module 6)
        # ----------------------------------------------------------
        print("\n[7] Executing workflow...")
        execute_workflow(workflow)

        print("\n✅ Workflow completed.")

        return {
            "status": "completed",
            "nlu": nlu_result,
            "workflow": workflow,
        }
