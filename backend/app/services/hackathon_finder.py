def find_completed_hackathons(search_results):
    candidates = []

    blocked_domains = [
        "instagram.com",
        "facebook.com",
        "linkedin.com",
        "twitter.com",
        "x.com",
        "youtube.com",
        "github.com",
        "scribd.com",
    ]

    blocked_keywords = [
        "problem statements",
        "problem statement",
        "registration",
        "register now",
        "upcoming",
        "archive",
        "listing",
    ]

    winner_keywords = [
        "winner",
        "winners",
        "results",
        "result",
        "awards",
        "award",
        "concluded",
        "completed",
        "finale",
    ]

    seen_urls = set()

    for result in search_results:
        title = result.get("title", "").strip()
        url = result.get("url", "").strip()
        snippet = result.get("snippet", "").strip()

        if not url:
            continue

        url_lower = url.lower()
        text = f"{title} {snippet}".lower()

        # Reject social/generic websites
        if any(domain in url_lower for domain in blocked_domains):
            continue

        # Reject obvious non-completed-event pages
        if any(keyword in text for keyword in blocked_keywords):
            continue

        # Keep pages showing completion/results
        if not any(keyword in text for keyword in winner_keywords):
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        candidates.append({
            "title": title,
            "source_url": url,
            "related_source_url": ""
        })

    return {
        "completed_hackathons": candidates
    }