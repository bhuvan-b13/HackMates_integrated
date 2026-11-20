
import json
from datetime import datetime

from .hackathon_finder import find_completed_hackathons
from .web_search import search_web
from .page_readers import read_page
from .hackathon_extractor import extract_hackathon
from .hackathon_validator import validate_hackathon
from .pdf_reader import read_pdf

from ..models import CompletedHackathon


def update_completed_hackathons(db, source_urls=None):

    # --------------------------------------------------
    # 1. Collect existing and newly discovered sources
    # --------------------------------------------------

    if source_urls:
        # Update only explicitly selected sources.
        candidates = [
            {"source_url": url.strip()}
            for url in source_urls
            if isinstance(url, str) and url.strip()
        ]

    else:
        # Retrieve all existing hackathon records from SQLite.
        existing_records = (
            db.query(CompletedHackathon).all()
        )

        existing_candidates = [
            {"source_url": record.source_url.strip()}
            for record in existing_records
            if record.source_url
            and record.source_url.strip()
        ]

        # Discover new completed hackathons for the current year.
        current_year = datetime.now().year

        search_results = search_web(
            f'"hackathon" "winners" "{current_year}" India results',
            max_results=15
        )

        result = find_completed_hackathons(search_results)

        discovered_candidates = result.get(
            "completed_hackathons", []
        )

        # Combine existing and newly discovered sources.
        # Avoid processing the same source URL twice.
        candidates = []
        seen_urls = set()

        for candidate in (
            existing_candidates + discovered_candidates
        ):
            if not isinstance(candidate, dict):
                continue

            url = candidate.get("source_url", "")

            if not isinstance(url, str):
                continue

            url = url.strip()

            if url and url not in seen_urls:
                candidate = candidate.copy()
                candidate["source_url"] = url

                candidates.append(candidate)
                seen_urls.add(url)

    # --------------------------------------------------
    # 2. Track inserted and refreshed records
    # --------------------------------------------------

    added = 0
    updated = 0

    text_fields = [
        "title",
        "organizer",
        "college",
        "date",
        "location",
        "problem_statement",
        "first_place",
        "first_project_name",
        "first_project_description",
        "second_place",
        "second_project_name",
        "second_project_description",
        "third_place",
        "third_project_name",
        "third_project_description",
    ]

    # Only these fields may be explicitly cleared
    # under the existing GitLab correction condition.
    clearable_fields = {
        "first_place",
        "second_place",
        "third_place",
    }

    # --------------------------------------------------
    # 3. Read source webpages and extract information
    # --------------------------------------------------

    for candidate in candidates:

        source_url = candidate.get("source_url", "")
        related_source_url = candidate.get(
            "related_source_url", ""
        )

        if not source_url:
            continue

        try:
            # Read the main source webpage or PDF.
            if source_url.lower().endswith(".pdf"):
                page_text = read_pdf(source_url)
            else:
                page_text = read_page(source_url)

            if not page_text or not page_text.strip():
                print(f"Skipped empty source: {source_url}")
                continue

            # Read additional related source when available.
            if related_source_url:
                try:
                    if related_source_url.lower().endswith(".pdf"):
                        related_text = read_pdf(related_source_url)
                    else:
                        related_text = read_page(related_source_url)

                    if related_text:
                        page_text += "\n\n" + related_text

                except Exception as error:
                    print(
                        f"Could not read related source: "
                        f"{related_source_url}"
                    )
                    print(f"Reason: {error}")

            # Extract structured information using Ollama.
            data = extract_hackathon(page_text, source_url)

            # Do not save invalid or unsupported extraction results.
            if not validate_hackathon(data):
                print(f"Skipped invalid hackathon: {source_url}")
                continue

            # --------------------------------------------------
            # 4. Find existing record or create a new record
            # --------------------------------------------------

            hackathon = (
                db.query(CompletedHackathon)
                .filter(
                    CompletedHackathon.source_url == source_url
                )
                .first()
            )

            is_new = hackathon is None

            if is_new:
                hackathon = CompletedHackathon(
                    title=data.get("title", "")
                )

            # Preserve the existing GitLab correction behavior.
            allow_empty_placements = (
                not is_new
                and source_urls is not None
                and source_url in source_urls
                and "gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners"
                in source_url
            )

            # --------------------------------------------------
            # 5. Update extracted text fields
            # --------------------------------------------------

            for field in text_fields:

                new_value = data.get(field, "")

                if isinstance(new_value, str):
                    new_value = new_value.strip()

                # Update only when the extracted value is non-empty.
                if new_value:
                    setattr(hackathon, field, new_value)

                # Explicitly clear selected placement fields
                # only under the existing GitLab correction rule.
                elif (
                    allow_empty_placements
                    and field in clearable_fields
                ):
                    setattr(hackathon, field, "")

            # --------------------------------------------------
            # 6. Update project ideas without losing old data
            # --------------------------------------------------

            new_ideas = data.get("project_ideas", [])

            if isinstance(new_ideas, list) and new_ideas:

                clean_ideas = [
                    idea.strip()
                    for idea in new_ideas
                    if isinstance(idea, str) and idea.strip()
                ]

                if clean_ideas:
                    hackathon.project_ideas = json.dumps(
                        clean_ideas
                    )

            elif is_new:
                hackathon.project_ideas = "[]"

            # --------------------------------------------------
            # 7. Save the record in SQLite
            # --------------------------------------------------

            hackathon.source_url = source_url

            db.add(hackathon)
            db.commit()

            if is_new:
                added += 1

                print(
                    f"Added completed hackathon: "
                    f"{hackathon.title}"
                )

            else:
                updated += 1

                print(
                    f"Refreshed completed hackathon: "
                    f"{hackathon.title}"
                )

        except Exception as error:

            db.rollback()

            print(f"Skipped source: {source_url}")
            print(f"Reason: {error}")

    # --------------------------------------------------
    # 8. Return update summary
    # --------------------------------------------------

    return {
        "added": added,
        "updated": updated,
        "total_processed": added + updated
    }
