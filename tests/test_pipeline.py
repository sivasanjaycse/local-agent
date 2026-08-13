try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from llm.gemini_client import GeminiIntentClassifier
from validation.intent_validator import validate_intent
from workflows.workflow_builder import build_workflow
from confirmation.confirm import request_confirmation
from execution.executor import execute_open_application


classifier = GeminiIntentClassifier()

user_text = input("Enter your command: ")

print("\n[1] Sending to Gemini...")
intent_result = classifier.classify(user_text)

print("[2] Gemini result:")
print(intent_result)

print("\n[3] Validating...")
validate_intent(intent_result)
print("Validation successful! ✅")

print("\n[4] Building workflow...")
workflow = build_workflow(intent_result)

print("Workflow:")
print(workflow)

print("\n[5] Requesting confirmation...")
confirmed = request_confirmation(workflow)

if not confirmed:
    print("\n❌ User rejected the workflow.")
    print("Execution cancelled.")
    exit()

print("\n✅ User confirmed the workflow.")

if workflow["action"] == "OPEN_APPLICATION":

    execute_open_application(
        workflow["target"]
    )

else:
    print(
        f"Execution for {workflow['action']} "
        "is not implemented yet."
    )
