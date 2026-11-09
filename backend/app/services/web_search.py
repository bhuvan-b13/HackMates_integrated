from ddgs import DDGS


def search_web(query: str, max_results: int = 10):
    results = []

    with DDGS(timeout=15) as ddgs:
        search_results = ddgs.text(
            query,
            max_results=max_results
        )

        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
                "source": ""
            })

    return results


def find_article_url(title: str, source: str) -> str:
    query = f"{title} {source}"

    results = search_web(query, max_results=10)

    if not results:
        return ""

    return results[0]["url"]