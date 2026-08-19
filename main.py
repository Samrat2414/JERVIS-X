from core.router import route_command


def start_jervis():
    print("=" * 45)
    print("JERVIS X")
    print("Advanced Personal AI Virtual Assistant")
    print("System Status: ONLINE")
    print("=" * 45)

    print("\nJERVIS: Hello! I am JERVIS.")
    print("Type 'exit' to close JERVIS.\n")

    while True:
        command = input("YOU: ").strip()

        if command.lower() in ["exit", "quit", "bye"]:
            print("JERVIS: Goodbye!")
            break

        response = route_command(command)
        print(f"JERVIS: {response}")


if __name__ == "__main__":
    start_jervis()