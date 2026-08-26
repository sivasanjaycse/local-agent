import os
import subprocess
import webbrowser

import pyautogui


def execute_open_application(application, open_folder=False):

    applications = {
        "Google Chrome": "chrome",
        "Chrome": "chrome",
        "Notepad": "notepad",
        "Calculator": "calc",
        "VS Code": "code"
    }

    if application not in applications:
        raise ValueError(
            f"Application not allowed: {application}"
        )

    command = applications[application]

    if application == "VS Code" and open_folder:
        subprocess.Popen("code .", shell=True)
        print(f"Opened current folder in VS Code ✅")
    elif application == "VS Code":
        subprocess.Popen("code", shell=True)
        print(f"Started application: {application} ✅")
    else:
        subprocess.Popen(command)
        print(f"Started application: {application} ✅")


def execute_open_website(website, url):

    if not url:
        raise ValueError(
            f"No URL provided for website: {website}"
        )

    webbrowser.open(url)

    print(f"Opened {website} ({url}) ✅")


def execute_web_search(query, website=None):

    if not query:
        raise ValueError("Search query cannot be empty")

    if website:
        search_url = (
            "https://www.google.com/search?q="
            + query.replace(" ", "+")
        )
    else:
        search_url = (
            "https://www.google.com/search?q="
            + query.replace(" ", "+")
        )

    webbrowser.open(search_url)

    print(f"Opened web search for: {query} ✅")


def execute_file_operation(operation, name):

    if not name:
        raise ValueError("File/folder name cannot be empty")

    if operation != "create_folder":
        raise ValueError(
            f"Unsupported file operation: {operation}"
        )

    if os.path.basename(name) != name or name in {".", ".."}:
        raise ValueError("Folder name must not include a path")

    folder_path = os.path.join(
        os.getcwd(),
        name
    )

    if os.path.exists(folder_path):
        raise FileExistsError(
            f"Folder already exists: {name}"
        )

    os.makedirs(folder_path)

    print(f"Folder created: {folder_path} ✅")


def execute_system_action(action):

    if action != "screenshot":
        raise ValueError(
            f"Unsupported system action: {action}"
        )

    screenshot = pyautogui.screenshot()

    filename = "screenshot.png"
    screenshot.save(filename)

    print(f"Screenshot saved as: {filename} ✅")


def execute_vibe_coding(workflow):

    steps = workflow.get("steps", [])

    print(f"\n🚀 Starting vibe coding session ({len(steps)} steps)...\n")

    for i, step in enumerate(steps, 1):
        action = step.get("action")

        print(f"  [{i}/{len(steps)}] ", end="")

        if action == "OPEN_WEBSITE":
            execute_open_website(
                step.get("target"),
                step.get("url")
            )

        elif action == "OPEN_APPLICATION":
            execute_open_application(
                step.get("target"),
                step.get("open_folder", False)
            )

        else:
            print(f"Skipping unknown step: {action}")

    print("\n🎧 Vibe coding session ready! Let's go! 🚀")


def execute_workflow(workflow):

    action = workflow.get("action")

    if action == "OPEN_APPLICATION":
        execute_open_application(
            workflow.get("target"),
            workflow.get("open_folder", False)
        )

    elif action == "OPEN_WEBSITE":
        execute_open_website(
            workflow.get("target"),
            workflow.get("url")
        )

    elif action == "WEB_SEARCH":
        execute_web_search(
            workflow.get("query"),
            workflow.get("website")
        )

    elif action == "FILE_OPERATION":
        execute_file_operation(
            workflow.get("operation"),
            workflow.get("name")
        )

    elif action == "SYSTEM_ACTION":
        execute_system_action(
            workflow.get("type")
        )

    elif action == "VIBE_CODING":
        execute_vibe_coding(workflow)

    else:
        raise ValueError(
            f"Unsupported workflow action: {action}"
        )
