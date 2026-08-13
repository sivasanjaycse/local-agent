try:
    from tests import bootstrap
except ModuleNotFoundError:
    import tests.bootstrap as bootstrap

from agent.controller import AgentController


controller = AgentController()

user_text = input("Enter your command: ")

result = controller.process_text(user_text)

print("\nFinal result:")
print(result)
