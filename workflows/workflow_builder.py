"""
Workflow Recommendation Module — Module 4

Correlates the high-level intent from Module 3 with extracted entities
to synthesize a multi-step workflow of concrete desktop actions.

Currently uses static default templates per intent. When the Knowledge
Base (Module 8) is implemented, this module will query it for temporal
context and historical usage to produce personalized recommendations.
"""


# ------------------------------------------------------------------
# Default workflow templates per intent
#
# These provide fallback actions when the LLM's entity extraction
# does not include enough information to build a complete workflow.
# Once the Knowledge Base is available, these will be augmented
# with personalized, context-aware recommendations.
# ------------------------------------------------------------------

DEFAULT_WORKFLOWS = {
    "CODING": {
        "applications": ["VS Code"],
        "websites": [
            {"name": "GitHub", "url": "https://github.com"},
        ],
    },
    "MEETING": {
        "applications": [],
        "websites": [
            {"name": "Google Meet", "url": "https://meet.google.com"},
        ],
    },
    "RESEARCH": {
        "applications": ["Chrome"],
        "websites": [],
    },
    "ENTERTAINMENT": {
        "applications": [],
        "websites": [
            {"name": "YouTube", "url": "https://www.youtube.com"},
            {"name": "Spotify", "url": "https://open.spotify.com"},
        ],
    },
    "COMMUNICATION": {
        "applications": ["Chrome"],
        "websites": [
            {"name": "Gmail", "url": "https://mail.google.com"},
        ],
    },
    "PRODUCTIVITY": {
        "applications": ["Notepad"],
        "websites": [],
    },
    "SYSTEM": {
        "applications": [],
        "websites": [],
    },
}

INTENT_LABELS = {
    "CODING":        "coding session",
    "MEETING":       "meeting setup",
    "RESEARCH":      "research session",
    "ENTERTAINMENT": "entertainment session",
    "COMMUNICATION": "communication setup",
    "PRODUCTIVITY":  "productivity task",
    "SYSTEM":        "system operation",
}


def build_workflow(intent_result, learner=None):
    """
    Build a multi-step workflow from a high-level intent + entities.

    Args:
        intent_result: dict from GeminiIntentClassifier with keys
                       intent, entities, reasoning.
        learner:       Optional PreferenceLearningEngine instance.
                       When provided, learned user preferences are
                       used before falling back to static defaults.

    Returns:
        dict with workflow_id, intent, steps, description, reasoning.
    """
    intent = intent_result["intent"]
    entities = intent_result.get("entities", {})
    reasoning = intent_result.get("reasoning", "")

    steps = []

    # ---- Build steps from extracted entities ----

    action = entities.get("action", "open")

    # 1. System-level actions (screenshot, create_folder)
    if action == "screenshot":
        steps.append({
            "action": "SYSTEM_ACTION",
            "type": "screenshot",
        })

    elif action == "create_folder":
        file_target = entities.get("file_target", "")
        if file_target:
            steps.append({
                "action": "FILE_OPERATION",
                "operation": "create_folder",
                "name": file_target,
            })

    else:
        # 2. Applications
        for app in entities.get("applications", []):
            step = {
                "action": "OPEN_APPLICATION",
                "target": app,
            }
            if action == "open_folder":
                step["open_folder"] = True
            steps.append(step)

        # 3. Websites
        for site in entities.get("websites", []):
            steps.append({
                "action": "OPEN_WEBSITE",
                "target": site.get("name", ""),
                "url": site.get("url", ""),
            })

        # 4. Search query
        query = entities.get("query", "")
        if query:
            steps.append({
                "action": "WEB_SEARCH",
                "query": query,
            })

    # ---- Learned preferences (from Knowledge Base) ----
    #
    # If the entity-based steps are empty and a learner is
    # available, query historical usage before falling back
    # to static defaults.

    if not steps and learner is not None:
        learned_apps = learner.get_recommended_apps(intent)
        learned_sites = learner.get_recommended_websites(intent)

        for app in learned_apps:
            steps.append({
                "action": "OPEN_APPLICATION",
                "target": app,
            })

        for site in learned_sites:
            steps.append({
                "action": "OPEN_WEBSITE",
                "target": site["name"],
                "url": site["url"],
            })

    # ---- Static defaults (last resort) ----
    if not steps:
        defaults = DEFAULT_WORKFLOWS.get(intent, {})

        for app in defaults.get("applications", []):
            steps.append({
                "action": "OPEN_APPLICATION",
                "target": app,
            })

        for site in defaults.get("websites", []):
            steps.append({
                "action": "OPEN_WEBSITE",
                "target": site["name"],
                "url": site["url"],
            })

    # ---- Build human-readable description ----
    description = _build_description(intent, steps)

    return {
        "workflow_id": intent.lower(),
        "intent": intent,
        "steps": steps,
        "description": description,
        "reasoning": reasoning,
    }


def _build_description(intent, steps):
    """Generate a readable summary of the workflow."""
    label = INTENT_LABELS.get(intent, "task")

    parts = []
    for step in steps:
        action = step.get("action")

        if action == "OPEN_APPLICATION":
            target = step.get("target", "app")
            if step.get("open_folder"):
                parts.append(f"{target} (folder)")
            else:
                parts.append(target)

        elif action == "OPEN_WEBSITE":
            parts.append(step.get("target", "website"))

        elif action == "WEB_SEARCH":
            parts.append(f"search '{step.get('query', '')}'")

        elif action == "FILE_OPERATION":
            op = step.get("operation", "")
            name = step.get("name", "")
            parts.append(
                f"{op.replace('_', ' ')} '{name}'"
            )

        elif action == "SYSTEM_ACTION":
            parts.append(step.get("type", "action"))

    if parts:
        return f"Start {label} \u2014 {', '.join(parts)}"

    return f"Start {label}"