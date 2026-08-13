try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from execution.executor import execute_web_search


execute_web_search("Python tutorials")
