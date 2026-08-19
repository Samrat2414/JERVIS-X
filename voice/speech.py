import speech_recognition as sr


def normalize_command(text):
    text = text.lower().strip()

    replacements = {
        "jarvis": "jervis",
        "jervish": "jervis",
        "service": "jervis",
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    if text.startswith("hey jervis"):
        text = text.replace("hey jervis", "", 1).strip()

    elif text.startswith("jervis"):
        text = text.replace("jervis", "", 1).strip()

    return text


def listen_once():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("JERVIS: Listening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

            print("JERVIS: Recognizing...")

            text = recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            print(f"YOU SAID: {text}")

            return normalize_command(text)

        except sr.WaitTimeoutError:
            return None

        except sr.UnknownValueError:
            return None

        except sr.RequestError as error:
            print(
                f"Speech recognition service error: {error}"
            )
            return None