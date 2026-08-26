"""
Intent Validator

Validates the structured output from the Intent Recognition Module
(Module 3) before it is passed to the Workflow Recommendation Module
(Module 4).

Ensures the LLM response conforms to the expected schema with
high-level goal intents and properly structured entities.
"""


ALLOWED_INTENTS = {
    "CODING",
    "MEETING",
    "RESEARCH",
    "ENTERTAINMENT",
    "COMMUNICATION",
    "PRODUCTIVITY",
    "SYSTEM",
}

EXPECTED_ENTITY_FIELDS = {
    "applications",
    "websites",
    "query",
    "topic",
    "action",
    "file_target",
    "file_path",
}


def validate_intent(result):
    """
    Validate the intent classification result.

    Args:
        result: dict returned by GeminiIntentClassifier.classify()

    Raises:
        ValueError: If the result does not conform to the schema.

    Returns:
        True if validation passes.
    """

    if not isinstance(result, dict):
        raise ValueError("Intent result must be a dictionary")

    if "intent" not in result:
        raise ValueError("Missing 'intent' field")

    if "entities" not in result:
        raise ValueError("Missing 'entities' field")

    if "reasoning" not in result:
        raise ValueError("Missing 'reasoning' field")

    if result["intent"] not in ALLOWED_INTENTS:
        raise ValueError(
            f"Unknown intent: {result['intent']}. "
            f"Allowed: {', '.join(sorted(ALLOWED_INTENTS))}"
        )

    entities = result["entities"]

    if not isinstance(entities, dict):
        raise ValueError("'entities' must be a dictionary")

    # Validate applications list
    apps = entities.get("applications", [])
    if not isinstance(apps, list):
        raise ValueError("'entities.applications' must be a list")

    # Validate websites list
    websites = entities.get("websites", [])
    if not isinstance(websites, list):
        raise ValueError("'entities.websites' must be a list")

    for i, site in enumerate(websites):
        if not isinstance(site, dict):
            raise ValueError(
                f"'entities.websites[{i}]' must be a dictionary"
            )
        if "name" not in site:
            raise ValueError(
                f"'entities.websites[{i}]' missing 'name' field"
            )
        if "url" not in site:
            raise ValueError(
                f"'entities.websites[{i}]' missing 'url' field"
            )

    return True