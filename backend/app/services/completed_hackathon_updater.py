import json

from .hackathon_finder import find_completed_hackathons
from .web_search import search_web
from .page_readers import read_page
from .hackathon_extractor import extract_hackathon
from .hackathon_validator import validate_hackathon
from .pdf_reader import read_pdf

from ..models import CompletedHackathon


def update_completed_hackathons(db, source_urls=None):
    if source_urls:
        # Update only the explicitly selected sources.
        candidates = [
            {"source_url": url}
            for url in source_urls
        ]
    else:
        # Preserve the existing automatic discovery behavior.
        search_results = search_web(
            '"hackathon" "winners" "2026" India results',
            max_results=15
        )

        result = find_completed_hackathons(search_results)
        candidates = result.get("completed_hackathons", [])

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

    for candidate in candidates:
        source_url = candidate.get("source_url", "")
        related_source_url = candidate.get("related_source_url", "")

        if not source_url:
            continue

        try:
            # Read the main source.
            if source_url.lower().endswith(".pdf"):
                page_text = read_pdf(source_url)
            else:
                page_text = read_page(source_url)

            # Append related source text when available.
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

            # Extract information from the source.
            data = extract_hackathon(page_text, source_url)

            if not validate_hackathon(data):
                print(f"Skipped invalid hackathon: {source_url}")
                continue

            # Find an existing record.
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
            
                        # Update extracted fields.
            # For selected existing records, allow explicitly corrected
            # empty placement fields to clear incorrect stored rankings.
            clearable_fields = {
                "first_place",
                "second_place",
                "third_place",
            }
            
            allow_empty_placements = (
                not is_new
                and source_url in (source_urls or [])
                and "gitlab.com/blog/gitlab-ai-hackathon-2026-meet-the-winners"
                in source_url
            )
            
            for field in text_fields:
                new_value = data.get(field, "")
            
                if isinstance(new_value, str):
                    new_value = new_value.strip()
            
                if new_value:
                    setattr(hackathon, field, new_value)
                elif allow_empty_placements and field in clearable_fields:
                    setattr(hackathon, field, "")
            # Preserve existing project ideas when extraction returns
            # an empty list. Otherwise, save the extracted list.
            new_ideas = data.get("project_ideas", [])

            if isinstance(new_ideas, list) and new_ideas:
                clean_ideas = [
                    idea.strip()
                    for idea in new_ideas
                    if isinstance(idea, str) and idea.strip()
                ]

                if clean_ideas:
                    hackathon.project_ideas = json.dumps(clean_ideas)
            elif is_new:
                hackathon.project_ideas = "[]"

            # Preserve the source URL.
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
                    f"Updated completed hackathon: "
                    f"{hackathon.title}"
                )

        except Exception as error:
            db.rollback()
            print(f"Skipped source: {source_url}")
            print(f"Reason: {error}")

    return added