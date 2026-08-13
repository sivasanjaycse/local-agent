def request_confirmation(workflow):

    print("\n==============================")
    print("        ACTION REQUEST")
    print("==============================")

    description = workflow.get(
        "description",
        "Unknown action"
    )

    print("\nI want to:")
    print(f"  {description}")

    print("\n==============================")

    response = input(
        "Do you want to proceed? (y/n): "
    )

    confirmed = response.strip().lower() == "y"

    return {
        "confirmed": confirmed,
        "workflow_id": workflow.get("workflow_id")
    }