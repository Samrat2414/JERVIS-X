import pyttsx3


engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)


def speak(text):
    if not text:
        return

    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    speak("Hello. I am JERVIS.")