import os
import subprocess
import webbrowser

import pyautogui


# ------------------------------------------------------------------ #
#  Common user folder shortcuts                                      #
# ------------------------------------------------------------------ #
COMMON_FOLDERS = {
    "desktop":   os.path.join(os.path.expanduser("~"), "Desktop"),
    "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
    "documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "pictures":  os.path.join(os.path.expanduser("~"), "Pictures"),
    "music":     os.path.join(os.path.expanduser("~"), "Music"),
    "videos":    os.path.join(os.path.expanduser("~"), "Videos"),
}


def execute_open_application(application, open_folder=False):

    applications = {
        "Microsoft Edge": "msedge",
        "Edge": "msedge",
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


def execute_file_operation(operation, name, file_path=None):
    """
    Handle file operations: create_folder and open_file.

    For open_file:
      - file_path can be a folder shortcut ("desktop", "downloads")
        or a relative path like "desktop/report.pdf".
      - If only a folder is specified, open it in File Explorer.
      - If a file within the folder is specified, open it directly.
    """

    if operation == "open_file":
        return _execute_open_file(name, file_path)

    if operation != "create_folder":
        raise ValueError(
            f"Unsupported file operation: {operation}"
        )

    if not name:
        raise ValueError("File/folder name cannot be empty")

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


def _execute_open_file(name, file_path):
    """
    Open a file or folder from common user directories.

    Examples:
      name="downloads", file_path=None      → opens Downloads folder
      name="report.pdf", file_path="desktop" → opens Desktop/report.pdf
      name="desktop", file_path=None         → opens Desktop folder
    """

    # If name is itself a known folder shortcut, open that folder
    folder_key = (file_path or name or "").lower().strip()

    if folder_key in COMMON_FOLDERS:
        base_folder = COMMON_FOLDERS[folder_key]

        if file_path and name and name.lower() != folder_key:
            # A specific file within the folder
            target = os.path.join(base_folder, name)
        else:
            # Just open the folder
            target = base_folder

        if not os.path.exists(target):
            raise FileNotFoundError(
                f"Path not found: {target}"
            )

        os.startfile(target)
        print(f"Opened: {target} ✅")
        return

    raise ValueError(
        f"Unknown folder or file target: '{name}'. "
        f"Supported folders: {', '.join(COMMON_FOLDERS.keys())}"
    )


def execute_system_action(action):

    if action == "screenshot":
        screenshot = pyautogui.screenshot()
        filename = "screenshot.png"
        screenshot.save(filename)
        print(f"Screenshot saved as: {filename} ✅")

    elif action == "shutdown":
        print("⚠️  Shutting down in 30 seconds...")
        print("   Run 'shutdown /a' in a terminal to cancel.")
        subprocess.Popen(["shutdown", "/s", "/t", "30"])
        print(f"Shutdown scheduled ✅")

    else:
        raise ValueError(
            f"Unsupported system action: {action}"
        )


def execute_workflow(workflow):
    """
    Execute a multi-step workflow.

    Each workflow produced by the Workflow Builder (Module 4) now
    contains a list of steps.  This function iterates through them,
    dispatching each step to the appropriate action handler.
    """

    steps = workflow.get("steps", [])
    intent = workflow.get("intent", "UNKNOWN")

    if not steps:
        print("No steps to execute.")
        return

    total = len(steps)
    label = intent.replace("_", " ").title()

    print(f"\n  Starting {label} workflow ({total} step{'s' if total != 1 else ''})...\n")

    for i, step in enumerate(steps, 1):
        action = step.get("action")
        print(f"  [{i}/{total}] ", end="")

        if action == "OPEN_APPLICATION":
            execute_open_application(
                step.get("target"),
                step.get("open_folder", False),
            )

        elif action == "OPEN_WEBSITE":
            execute_open_website(
                step.get("target"),
                step.get("url"),
            )

        elif action == "WEB_SEARCH":
            execute_web_search(
                step.get("query"),
                step.get("website"),
            )

        elif action == "FILE_OPERATION":
            execute_file_operation(
                step.get("operation"),
                step.get("name"),
                step.get("file_path"),
            )

        elif action == "SYSTEM_ACTION":
            execute_system_action(
                step.get("type"),
            )

        else:
            print(f"Skipping unknown action: {action}")

    print(f"\n  {label} workflow complete!")


