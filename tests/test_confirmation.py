try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from confirmation.confirm import request_confirmation


workflow = {
    "workflow_id": "open_application",
    "action": "OPEN_APPLICATION",
    "target": "Notepad",
    "description": "Open Notepad"
}

result = request_confirmation(workflow)

print("\nConfirmation result:")
print(result)

if result["confirmed"]:
    print("User confirmed! ✅")
else:
    print("User rejected the action. ❌")
