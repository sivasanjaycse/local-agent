def build_workflow(intent_result):

    intent = intent_result["intent"]
    parameters = intent_result["parameters"]

    if intent == "OPEN_APPLICATION":
        application = parameters.get("application")
        open_folder = parameters.get("open_folder", False)

        description = f"Open {application}"
        if open_folder:
            description = f"Open current folder in {application}"

        return {
            "workflow_id": "open_application",
            "action": "OPEN_APPLICATION",
            "target": application,
            "open_folder": open_folder,
            "description": description
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

    elif intent == "OPEN_WEBSITE":
        website = parameters.get("website")
        url = parameters.get("url")

        return {
            "workflow_id": "open_website",
            "action": "OPEN_WEBSITE",
            "target": website,
            "url": url,
            "description": f"Open {website} ({url})"
        }

    elif intent == "VIBE_CODING":
        websites = parameters.get("websites", [])

        steps = []
        site_names = []

        for site in websites:
            steps.append({
                "action": "OPEN_WEBSITE",
                "target": site.get("website"),
                "url": site.get("url")
            })
            site_names.append(site.get("website"))

        # Always include VS Code as the final step
        steps.append({
            "action": "OPEN_APPLICATION",
            "target": "VS Code"
        })

        description = (
            "Start vibe coding session — open "
            + ", ".join(site_names)
            + " & VS Code"
        )

        return {
            "workflow_id": "vibe_coding",
            "action": "VIBE_CODING",
            "steps": steps,
            "description": description
        }

    else:
        raise ValueError(f"Unsupported intent: {intent}")