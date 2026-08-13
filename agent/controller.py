from llm.gemini_client import GeminiIntentClassifier
from validation.intent_validator import validate_intent
from workflows.workflow_builder import build_workflow
from confirmation.confirm import request_confirmation
from execution.executor import execute_workflow


class AgentController:

    def __init__(self):
        self.classifier = GeminiIntentClassifier()

    def process_text(self, user_text):

        print("\n[1] Understanding command...")
        intent_result = self.classifier.classify(user_text)

        print("\n[2] Gemini result:")
        print(intent_result)

        print("\n[3] Validating...")
        validate_intent(intent_result)

        print("Validation successful! ✅")

        print("\n[4] Building workflow...")
        workflow = build_workflow(intent_result)

        print("Workflow:")
        print(workflow)

        print("\n[5] Requesting confirmation...")
        confirmation = request_confirmation(workflow)

        if not confirmation["confirmed"]:
            print("\n❌ User rejected the workflow.")
            print("Execution cancelled.")
            return {
                "status": "cancelled",
                "workflow": workflow
            }

        print("\n✅ User confirmed the workflow.")

        print("\n[6] Executing workflow...")
        execute_workflow(workflow)

        print("\n✅ Workflow completed.")

        return {
            "status": "completed",
            "workflow": workflow
        }
