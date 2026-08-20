import ollama

MODEL_NAME = "qwen3:0.6b"
MAX_HISTORY_MESSAGES = 10

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are JERVIS, a helpful personal AI assistant. "
        "Answer clearly and concisely. "
        "Use recent conversation context for follow-up questions. "
        "Your name is JERVIS."
    ),
}

conversation_history = []


def ask_ai(user_message):
    user_message = user_message.strip()

    if not user_message:
        return "Please ask me something."

    try:
        messages = [
            SYSTEM_MESSAGE,
            *conversation_history,
            {
                "role": "user",
                "content": user_message,
            },
        ]

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            think=False,
        )

        answer = response["message"]["content"].strip()

        if not answer:
            return "I could not generate an answer."

        conversation_history.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        conversation_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        if len(conversation_history) > MAX_HISTORY_MESSAGES:
            del conversation_history[:-MAX_HISTORY_MESSAGES]

        return answer

    except Exception as error:
        return f"Local AI error: {error}"


def clear_conversation():
    conversation_history.clear()
    return "Conversation memory cleared."


if __name__ == "__main__":
    print(
        ask_ai("Hello. Introduce yourself in one sentence.")
    )