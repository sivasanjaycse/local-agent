try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from workflows.workflow_builder import build_workflow


intent_result = {
    "intent": "OPEN_APPLICATION",
    "parameters": {
        "application": "Google Chrome"
    }
}

workflow = build_workflow(intent_result)

print("Workflow:")
print(workflow)
