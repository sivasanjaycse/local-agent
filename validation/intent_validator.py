ALLOWED_INTENTS = {
    "OPEN_APPLICATION",
    "WEB_SEARCH",
    "FILE_OPERATION",
    "SYSTEM_ACTION"
}


def validate_intent(result):

    if not isinstance(result, dict):
        raise ValueError("Intent result must be a dictionary")

    if "intent" not in result:
        raise ValueError("Missing 'intent' field")

    if "parameters" not in result:
        raise ValueError("Missing 'parameters' field")

    if result["intent"] not in ALLOWED_INTENTS:
        raise ValueError(
            f"Unknown intent: {result['intent']}"
        )

    if not isinstance(result["parameters"], dict):
        raise ValueError("'parameters' must be a dictionary")

    return True