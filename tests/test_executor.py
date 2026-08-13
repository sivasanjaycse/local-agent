try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from execution.executor import execute_open_application


execute_open_application("Notepad")
