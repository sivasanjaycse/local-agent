from agent.controller import AgentController


def main():

    print("================================")
    print("       LOCAL VOICE AGENT")
    print("================================")

    controller = AgentController()

    while True:

        print("\nType a command.")
        print("Type 'exit' to quit.")

        user_text = input("\nCommand: ")

        if user_text.strip().lower() == "exit":
            print("\nGoodbye! 👋")
            break

        if not user_text.strip():
            print("Please enter a command.")
            continue

        try:
            result = controller.process_text(user_text)

            print("\nResult:")
            print(result)

        except Exception as e:
            print("\n❌ Error:")
            print(e)


if __name__ == "__main__":
    main()
