import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CompletedHackathon
from ..schemas import (
    CompletedHackathonCreate,
    CompletedHackathonResponse,
)

router = APIRouter(
    prefix="/completed-hackathons",
    tags=["Completed Hackathons"],
)


def format_hackathon(hackathon):
    """Convert a database record into a JSON-friendly dictionary."""

    try:
        project_ideas = json.loads(
            hackathon.project_ideas or "[]"
        )
    except (json.JSONDecodeError, TypeError):
        project_ideas = []

    if not isinstance(project_ideas, list):
        project_ideas = []

    return {
        "hackathon_id": hackathon.hackathon_id,
        "title": hackathon.title or "",
        "organizer": hackathon.organizer or "",
        "college": hackathon.college or "",
        "date": hackathon.date or "",
        "location": hackathon.location or "",
        "problem_statement": hackathon.problem_statement or "",
        "project_ideas": project_ideas,

        # First-place winner
        "first_place": hackathon.first_place or "",
        "first_project_name": hackathon.first_project_name or "",
        "first_project_description": (
            hackathon.first_project_description or ""
        ),

        # Second-place winner
        "second_place": hackathon.second_place or "",
        "second_project_name": hackathon.second_project_name or "",
        "second_project_description": (
            hackathon.second_project_description or ""
        ),

        # Third-place winner
        "third_place": hackathon.third_place or "",
        "third_project_name": hackathon.third_project_name or "",
        "third_project_description": (
            hackathon.third_project_description or ""
        ),

        "source_url": hackathon.source_url or "",
    }


@router.get("/")
def get_completed_hackathons(
    db: Session = Depends(get_db),
):
    """Return all completed hackathons."""

    hackathons = (
        db.query(CompletedHackathon)
        .order_by(CompletedHackathon.hackathon_id.desc())
        .all()
    )

    return [
        format_hackathon(hackathon)
        for hackathon in hackathons
    ]


@router.get("/{hackathon_id}")
def get_completed_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
):
    """Return one completed hackathon by its ID."""

    hackathon = (
        db.query(CompletedHackathon)
        .filter(
            CompletedHackathon.hackathon_id == hackathon_id
        )
        .first()
    )

    if not hackathon:
        raise HTTPException(
            status_code=404,
            detail="Completed hackathon not found",
        )

    return format_hackathon(hackathon)


@router.post("/")
def create_completed_hackathon(
    data: CompletedHackathonCreate,
    db: Session = Depends(get_db),
):
    """Create a completed hackathon record."""

    hackathon = CompletedHackathon(
        title=data.title,
        organizer=data.organizer,
        college=data.college,
        date=data.date,
        location=data.location,
        problem_statement=data.problem_statement,
        project_ideas=json.dumps(data.project_ideas),

        # First-place winner
        first_place=data.first_place,
        first_project_name=data.first_project_name,
        first_project_description=data.first_project_description,

        # Second-place winner
        second_place=data.second_place,
        second_project_name=data.second_project_name,
        second_project_description=data.second_project_description,

        # Third-place winner
        third_place=data.third_place,
        third_project_name=data.third_project_name,
        third_project_description=data.third_project_description,

        source_url=data.source_url,
    )

    try:
        db.add(hackathon)
        db.commit()
        db.refresh(hackathon)

        return format_hackathon(hackathon)

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save completed hackathon",
        ) from error


@router.post("/update")
def update_completed_hackathons_route(
    db: Session = Depends(get_db),
):
    """Search for and add new completed hackathons."""

    from ..services.completed_hackathon_updater import (
        update_completed_hackathons,
    )

    try:
        added = update_completed_hackathons(db)

        return {
            "message": "Completed hackathons update finished",
            "added": added,
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not update completed hackathons",
        ) from error