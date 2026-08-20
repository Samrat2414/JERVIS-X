import speech_recognition as sr


DEFAULT_LANGUAGE = "en-IN"
DEFAULT_TIMEOUT = 6
DEFAULT_PHRASE_LIMIT = 10


def normalize_command(text):
    text = text.lower().strip()

    replacements = {
        "jarvis": "jervis",
        "jervish": "jervis",
        "service": "jervis",
        "jervis x": "jervis",
        "hey jarvis": "hey jervis",
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    wake_words = [
        "hey jervis",
        "hello jervis",
        "jervis",
    ]

    for wake_word in wake_words:
        if text.startswith(wake_word):
            text = text[len(wake_word):].strip()
            break

    return text


def create_recognizer():
    recognizer = sr.Recognizer()

    recognizer.energy_threshold = 280
    recognizer.dynamic_energy_threshold = True
    recognizer.dynamic_energy_adjustment_damping = 0.15
    recognizer.dynamic_energy_ratio = 1.5
    recognizer.pause_threshold = 0.8
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.5

    return recognizer


def listen_once(
    language=DEFAULT_LANGUAGE,
    timeout=DEFAULT_TIMEOUT,
    phrase_time_limit=DEFAULT_PHRASE_LIMIT,
):
    recognizer = create_recognizer()

    try:
        with sr.Microphone() as source:
            print("JERVIS: Listening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.8,
            )

            try:
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                )

            except sr.WaitTimeoutError:
                print("JERVIS: I did not hear anything.")
                return None

        print("JERVIS: Recognizing...")

        try:
            text = recognizer.recognize_google(
                audio,
                language=language,
            )

            print(f"YOU SAID: {text}")

            command = normalize_command(text)

            if not command:
                print("JERVIS: I heard only the wake word.")
                return None

            return command

        except sr.UnknownValueError:
            print("JERVIS: I could not understand you.")
            return None

        except sr.RequestError as error:
            print(
                "JERVIS: Speech recognition service is unavailable. "
                f"Details: {error}"
            )
            return None

    except OSError as error:
        print(
            "JERVIS: Microphone is not available. "
            f"Details: {error}"
        )
        return None


def listen_continuously(callback, stop_words=None):
    """
    Experimental helper for future continuous voice mode.

    callback(command) is called each time a command is recognized.
    Say 'stop listening' or 'exit voice mode' to stop by default.
    """
    if stop_words is None:
        stop_words = {
            "stop listening",
            "exit voice mode",
            "stop voice mode",
        }

    print("JERVIS: Continuous listening mode started.")

    while True:
        command = listen_once()

        if not command:
            continue

        if command in stop_words:
            print("JERVIS: Continuous listening mode stopped.")
            break

        callback(command)


if __name__ == "__main__":
    result = listen_once()

    if result:
        print(f"NORMALIZED COMMAND: {result}")