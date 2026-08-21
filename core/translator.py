import requests


TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"


LANGUAGES = {
    "english": "en",
    "bengali": "bn",
    "bangla": "bn",
    "hindi": "hi",
    "japanese": "ja",
    "spanish": "es",
    "french": "fr",
    "german": "de",
}


def get_language_code(language):
    language = language.strip().lower()

    return LANGUAGES.get(
        language,
        language,
    )


def translate_text(
    text,
    target_language,
    source_language="auto",
):
    text = str(text).strip()

    if not text:
        return {
            "success": False,
            "error": "Please provide text to translate.",
        }

    target_code = get_language_code(
        target_language
    )

    source_code = get_language_code(
        source_language
    )

    try:
        response = requests.get(
            TRANSLATE_URL,
            params={
                "client": "gtx",
                "sl": source_code,
                "tl": target_code,
                "dt": "t",
                "q": text,
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        translated_parts = []

        for part in data[0]:
            if part and part[0]:
                translated_parts.append(
                    part[0]
                )

        translated_text = "".join(
            translated_parts
        )

        if not translated_text:
            return {
                "success": False,
                "error": "Translation returned no text.",
            }

        return {
            "success": True,
            "translated_text": translated_text,
            "target_language": target_language,
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": (
                "I could not translate the text. "
                "Please check your internet connection. "
                f"Details: {error}"
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "error": f"Translation error: {error}",
        }


def translate_text_response(
    text,
    target_language,
):
    result = translate_text(
        text,
        target_language,
    )

    if result["success"]:
        return result["translated_text"]

    return result["error"]


if __name__ == "__main__":
    print(
        translate_text_response(
            "Hello Guru",
            "bengali",
        )
    )