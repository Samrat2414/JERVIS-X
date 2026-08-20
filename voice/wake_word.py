import speech_recognition as sr


WAKE_WORDS = [
    "hey jervis",
    "jervis",
    "hey jarvis",
    "jarvis",
]


def wait_for_wake_word():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    print("JERVIS: Wake word mode active...")
    print('JERVIS: Say "Hey Jervis"')

    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=4
                )

            text = recognizer.recognize_google(
                audio,
                language="en-IN"
            ).lower().strip()

            print(f"HEARD: {text}")

            for wake_word in WAKE_WORDS:
                if wake_word in text:
                    print("JERVIS: Wake word detected!")
                    return True

        except sr.WaitTimeoutError:
            continue

        except sr.UnknownValueError:
            continue

        except sr.RequestError as error:
            print(
                f"JERVIS: Speech service error: {error}"
            )
            return False

        except OSError as error:
            print(
                f"JERVIS: Microphone error: {error}"
            )
            return False


if __name__ == "__main__":
    wait_for_wake_word()