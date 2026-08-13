try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from execution.executor import execute_workflow


workflow = {
    "action": "OPEN_APPLICATION",
    "target": "Notepad"
}

execute_workflow(workflow)
