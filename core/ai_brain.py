import ollama

MODEL_NAME = "qwen3:0.6b"


def ask_ai(user_message):
    user_message = user_message.strip()

    if not user_message:
        return "Please ask me something."

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are JERVIS, a helpful personal AI assistant. "
                        "Answer clearly and concisely. "
                        "Your name is JERVIS."
                    ),
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            think=False,
        )

        return response["message"]["content"].strip()

    except Exception as error:
        return f"Local AI error: {error}"


if __name__ == "__main__":
    print(
        ask_ai("Hello. Introduce yourself in one sentence.")
    )