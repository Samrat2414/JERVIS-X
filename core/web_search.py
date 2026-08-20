import webbrowser
from urllib.parse import quote_plus


def search_web(query):
    query = query.strip()

    if not query:
        return "Please tell me what you want to search."

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )

    try:
        webbrowser.open(url)
        return f"Searching the web for: {query}"

    except Exception as error:
        return f"I could not open web search: {error}"


def search_google_direct(query):
    return search_web(query)


def search_youtube_direct(query):
    query = query.strip()

    if not query:
        return "Please tell me what you want to search on YouTube."

    url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query)
    )

    try:
        webbrowser.open(url)
        return f"Searching YouTube for: {query}"

    except Exception as error:
        return f"I could not open YouTube search: {error}"


if __name__ == "__main__":
    print(search_web("Python tutorials"))