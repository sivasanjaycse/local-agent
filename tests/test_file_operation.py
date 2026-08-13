try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from execution.executor import execute_file_operation


execute_file_operation(
    "create_folder",
    "AgentTestFolder"
)
