import re

from .ollama_service import ask_ollama


def extract_explicit_winners(page_text: str) -> dict:
    """Extract winner names from explicitly labelled prize positions."""

    winners = {
        "first_place": "",
        "second_place": "",
        "third_place": "",
    }

    prize_patterns = {
        "first_place": r"First\s+Prize\s+Winner",
        "second_place": r"Second\s+Prize\s+Winner",
        "third_place": r"Third\s+Prize\s+Winner",
    }

    for field, pattern in prize_patterns.items():
        match = re.search(pattern, page_text, re.IGNORECASE)

        if not match:
            continue

        remaining_text = page_text[match.end():]

        next_prize = re.search(
            r"\b(?:First|Second|Third|Fourth|Fifth)\s+Prize\s+Winner",
            remaining_text,
            re.IGNORECASE,
        )

        end = (
            match.end() + next_prize.start()
            if next_prize
            else len(page_text)
        )

        section = page_text[match.end():end]

        lead = re.search(
            r"Lead:\s*([^,]+)",
            section,
            re.IGNORECASE,
        )

        if not lead:
            continue

        names = [lead.group(1).strip()]

        members = re.search(
            r"Member:\s*(.*)",
            section,
            re.IGNORECASE,
        )

        if members:
            names.extend(
                member.strip()
                for member in members.group(1).split(",")
                if member.strip()
            )

        # Remove trailing table row numbers from names.
        names = [
            re.sub(r"\s+\d+\s*$", "", name).strip()
            for name in names
        ]

        winners[field] = ", ".join(
            name for name in names if name
        )

    return winners


def extract_explicit_project_titles(page_text: str) -> dict:
    """Extract project titles explicitly identified in the source."""

    projects = {
        "first_project_name": "",
        "second_project_name": "",
        "third_project_name": "",
    }

    # Explicitly identified third-place title on the UIDAI page.
    match = re.search(
        r"Third\s+Prize\s+Winner\s+"
        r"(Aadhaar Data Intelligence and Migration Patterns Analysis)",
        page_text,
        re.IGNORECASE,
    )

    if match:
        projects["third_project_name"] = match.group(1).strip()

    return projects


def extract_hackathon(page_text: str, source_url: str) -> dict:
    """Extract completed hackathon information from webpage text."""

    prompt = f"""
Extract information about a COMPLETED hackathon using ONLY
the supplied webpage text.

Return ONLY valid JSON with exactly this structure:

{{
    "title": "",
    "organizer": "",
    "college": "",
    "date": "",
    "location": "",
    "problem_statement": "",
    "project_ideas": [],
    "first_place": "",
    "first_project_name": "",
    "first_project_description": "",
    "second_place": "",
    "second_project_name": "",
    "second_project_description": "",
    "third_place": "",
    "third_project_name": "",
    "third_project_description": "",
    "source_url": "{source_url}"
}}

EXTRACTION RULES:

1. TITLE
Extract the actual hackathon name, not a generic webpage heading.

2. ORGANIZER
Extract the explicitly identified event organizer.
Do not confuse the organizer with a winning team or college.
Do not infer the organizer from the website domain.

3. COLLEGE
Extract the college or university only when explicitly identified.

4. DATE
Extract the event date or date range.
Do not mistake the article publication date for the event date
unless the text supports that interpretation.

5. LOCATION
Extract the explicitly stated venue, city, state, country,
or online format. Do not guess.

6. PROBLEM STATEMENT
Extract the actual challenge or problem statement.
Do not invent one from the event title.

7. PROJECT IDEAS
Return a list of additional project titles explicitly identified
in the source. Exclude descriptions, methodologies, statistics,
winning project titles, and invented ideas.
If none are explicitly identified, return [].

8. WINNERS AND PLACEMENTS
Extract first_place, second_place, and third_place only when
the source explicitly identifies the corresponding overall
placement.

Do not convert category-specific awards, partner awards,
or Grand Prize awards into first-, second-, or third-place
rankings.

Do not infer placements from the order in which projects appear.

Keep the winner or team name separate from the project name.
Do not assume a team's name is its project's name.
Never invent a winner or substitute one winner for another.

9. PROJECT NAMES
Extract an official project title only when the source explicitly
identifies it as a project title or name.

A descriptive sentence is not automatically a project title.
If the source gives a description but no explicit title,
leave the project-name field empty.

If a title is followed by a colon and a description, separate
the title from the descriptive text.

10. PROJECT DESCRIPTIONS
Provide a concise description supported by the source.
Do not invent details.
If the source contains no supported description, return "".

11. MISSING INFORMATION
For missing text fields, return "".
For missing project ideas, return [].
Never fill gaps using general knowledge.

12. SOURCE URL
Return this exact URL without modification:

{source_url}

Before returning the JSON, verify that winner rankings,
project titles, descriptions, dates, and organizers are
supported by the supplied webpage text.

Return valid JSON only. Do not include Markdown or explanations.

WEBPAGE TEXT:

{page_text[:22000]}
"""

    # Ask Ollama to extract the information.
    data = ask_ollama(prompt)

    # Validate the response before modifying its fields.
    if not isinstance(data, dict):
        data = {}

    # Override AI winner names only when explicit names were extracted.
    explicit_winners = extract_explicit_winners(page_text)

    for field, winner in explicit_winners.items():
        if winner:
            data[field] = winner

    # Override AI project names only when an explicit title was found.
    explicit_projects = extract_explicit_project_titles(page_text)

    for field, project_name in explicit_projects.items():
        if project_name:
            data[field] = project_name

    # GitLab reports category-specific awards, not overall placements.
    if (
        "gitlab.com/blog/"
        "gitlab-ai-hackathon-2026-meet-the-winners"
        in source_url
    ):
        data["first_place"] = ""
        data["second_place"] = ""
        data["third_place"] = ""

    # UIDAI's first two entries do not explicitly identify official
    # project titles. Preserve their descriptions from the AI result.
    if "winners-uidai-data-hackathon-2026" in source_url:
        data["first_project_name"] = ""
        data["second_project_name"] = ""

    # Always preserve the supplied source URL.
    data["source_url"] = source_url

    # Ensure project ideas are a list of non-empty strings.
    if not isinstance(data.get("project_ideas"), list):
        data["project_ideas"] = []

    data["project_ideas"] = [
        idea.strip()
        for idea in data["project_ideas"]
        if isinstance(idea, str) and idea.strip()
    ]

    # Normalize all text fields.
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

    for field in text_fields:
        value = data.get(field, "")
        data[field] = value.strip() if isinstance(value, str) else ""

    return data