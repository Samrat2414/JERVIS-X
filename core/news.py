import xml.etree.ElementTree as ET
from urllib.parse import quote

import requests


GOOGLE_NEWS_URL = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)


def get_news(topic="India", limit=5):
    topic = topic.strip() or "India"

    try:
        limit = max(1, min(int(limit), 10))
    except (TypeError, ValueError):
        limit = 5

    url = GOOGLE_NEWS_URL.format(
        query=quote(topic)
    )

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)

        items = root.findall(
            "./channel/item"
        )

        if not items:
            return (
                f"I could not find news for {topic}."
            )

        headlines = []

        for number, item in enumerate(
            items[:limit],
            start=1,
        ):
            title = item.findtext(
                "title",
                default="Untitled",
            )

            pub_date = item.findtext(
                "pubDate",
                default="",
            )

            headlines.append(
                f"{number}. {title}\n"
                f"   {pub_date}"
            )

        return (
            f"Latest news about {topic}:\n\n"
            + "\n\n".join(headlines)
        )

    except requests.RequestException as error:
        return (
            "I could not get live news. "
            "Please check your internet connection. "
            f"Details: {error}"
        )

    except ET.ParseError:
        return "I received invalid news data."

    except Exception as error:
        return f"News error: {error}"


if __name__ == "__main__":
    print(get_news("technology"))