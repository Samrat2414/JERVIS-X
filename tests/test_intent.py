from core.intent import detect_intent


def test_detect_intent_recognizes_greeting():
    assert detect_intent("Hello") == ("greeting", None)


def test_detect_intent_normalizes_open_youtube_command():
    assert detect_intent(" JERVIS, please open YouTube ") == (
        "open_youtube",
        None,
    )


def test_detect_intent_extracts_google_search_query():
    assert detect_intent("search Google for Python tutorials") == (
        "search_google",
        "python tutorials",
    )


def test_detect_intent_extracts_youtube_search_query():
    assert detect_intent("search YouTube for Python tutorials") == (
        "search_youtube",
        "python tutorials",
    )


def test_detect_intent_treats_empty_google_search_as_unknown():
    assert detect_intent("search Google for ") == (
        None,
        "search google for",
    )


def test_detect_intent_treats_empty_youtube_search_as_unknown():
    assert detect_intent("search YouTube for ") == (
        None,
        "search youtube for",
    )


def test_detect_intent_preserves_unknown_command():
    assert detect_intent("something completely unknown") == (
        None,
        "something completely unknown",
    )
