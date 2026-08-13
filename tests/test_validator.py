try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from validation.intent_validator import validate_intent


test_result = {
    "intent": "DELETE_EVERYTHING",
    "parameters": {}
}

try:
    validate_intent(test_result)
    print("Validation successful! ✅")

except ValueError as e:
    print("Validation failed:", e)
