import threading
from pathlib import Path

import pyttsx3


AUDIO_DIR = Path("generated_audio")

_engine = None
_engine_lock = threading.Lock()


def _get_engine():
    global _engine

    if _engine is None:
        _engine = pyttsx3.init()

    return _engine


def speak_text(text, rate=180):
    text = str(text).strip()

    if not text:
        return "Please provide some text to speak."

    try:
        rate = int(rate)
    except (TypeError, ValueError):
        rate = 180

    rate = max(80, min(rate, 300))

    try:
        with _engine_lock:
            engine = _get_engine()
            engine.setProperty("rate", rate)
            engine.say(text)
            engine.runAndWait()

        return "Speech completed."

    except Exception as error:
        return f"TTS error: {error}"


def stop_speaking():
    try:
        with _engine_lock:
            engine = _get_engine()
            engine.stop()

        return "Speech stopped."

    except Exception as error:
        return f"I could not stop speech: {error}"


def get_voices():
    try:
        engine = _get_engine()
        voices = engine.getProperty("voices")

        result = []

        for index, voice in enumerate(voices):
            result.append(
                {
                    "index": index,
                    "name": getattr(
                        voice,
                        "name",
                        f"Voice {index + 1}",
                    ),
                    "id": voice.id,
                }
            )

        return result

    except Exception:
        return []


def set_voice(voice_index):
    try:
        voice_index = int(voice_index)
    except (TypeError, ValueError):
        return "Invalid voice number."

    try:
        with _engine_lock:
            engine = _get_engine()
            voices = engine.getProperty("voices")

            if (
                voice_index < 0
                or voice_index >= len(voices)
            ):
                return "Voice number not found."

            engine.setProperty(
                "voice",
                voices[voice_index].id,
            )

        return (
            f"Voice changed to "
            f"{voices[voice_index].name}."
        )

    except Exception as error:
        return f"I could not change voice: {error}"


def save_speech_to_file(
    text,
    file_name="jervis_speech.wav",
    rate=180,
):
    text = str(text).strip()

    if not text:
        return {
            "success": False,
            "error": "Please provide text to save.",
        }

    try:
        rate = int(rate)
    except (TypeError, ValueError):
        rate = 180

    rate = max(80, min(rate, 300))

    if not file_name.lower().endswith(".wav"):
        file_name += ".wav"

    AUDIO_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = AUDIO_DIR / file_name

    try:
        with _engine_lock:
            engine = _get_engine()
            engine.setProperty("rate", rate)

            engine.save_to_file(
                text,
                str(file_path),
            )
            engine.runAndWait()

        return {
            "success": True,
            "path": str(file_path),
            "message": (
                f"Audio saved as {file_path}."
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "error": f"I could not save audio: {error}",
        }


if __name__ == "__main__":
    print(
        speak_text(
            "Hello, I am JERVIS.",
            rate=180,
        )
    )