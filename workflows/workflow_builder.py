def build_workflow(intent_result):

    intent = intent_result["intent"]
    parameters = intent_result["parameters"]

    if intent == "OPEN_APPLICATION":
        application = parameters.get("application")

        return {
            "workflow_id": "open_application",
            "action": "OPEN_APPLICATION",
            "target": application,
            "description": f"Open {application}"
        }

    elif intent == "WEB_SEARCH":
        query = parameters.get("query")
        website = parameters.get("website")

        return {
            "workflow_id": "web_search",
            "action": "WEB_SEARCH",
            "query": query,
            "website": website,
            "description": f"Search the web for '{query}'"
        }

    elif intent == "FILE_OPERATION":
        operation = parameters.get("operation")
        name = parameters.get("name")

        return {
            "workflow_id": "file_operation",
            "action": "FILE_OPERATION",
            "operation": operation,
            "name": name,
            "description": f"{operation.replace('_', ' ').capitalize()} '{name}'"
        }

    elif intent == "SYSTEM_ACTION":
        action = parameters.get("action")

        return {
            "workflow_id": "system_action",
            "action": "SYSTEM_ACTION",
            "type": action,
            "description": f"Perform system action: {action}"
        }

    else:
        raise ValueError(f"Unsupported intent: {intent}")