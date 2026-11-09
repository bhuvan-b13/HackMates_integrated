import requests
from bs4 import BeautifulSoup


def read_page(url: str) -> str:
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    # Extract all visible webpage text instead of relying
    # on an article element that may contain only a placeholder.
    return soup.get_text(" ", strip=True)