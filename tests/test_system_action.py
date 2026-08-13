try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from execution.executor import execute_system_action


execute_system_action("screenshot")
