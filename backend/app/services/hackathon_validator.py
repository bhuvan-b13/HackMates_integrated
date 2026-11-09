from typing import Any


REQUIRED_FIELDS = [
    "title",
    "organizer",
    "college",
    "date",
    "location",
    "problem_statement",
    "project_ideas",
    "first_place",
    "first_project_name",
    "first_project_description",
    "second_place",
    "second_project_name",
    "second_project_description",
    "third_place",
    "third_project_name",
    "third_project_description",
    "source_url",
]


def validate_hackathon(data: dict[str, Any]) -> bool:
    # All fields must exist
    for field in REQUIRED_FIELDS:
        if field not in data:
            return False

    # Check data types
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
        "source_url",
    ]

    for field in text_fields:
        if not isinstance(data[field], str):
            return False

    # Project ideas must be a list of strings
    if not isinstance(data["project_ideas"], list):
        return False

    if not all(
        isinstance(idea, str)
        for idea in data["project_ideas"]
    ):
        return False

    # Minimum information required
    if not data["title"].strip():
        return False

    if not data["source_url"].strip():
        return False

    # At least one winner must be present
    winners = [
        data["first_place"],
        data["second_place"],
        data["third_place"],
    ]

    if not any(winner.strip() for winner in winners):
        return False

    return True