import os
import smtplib

from email.message import EmailMessage

from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Team,
    TeamMember,
    JoinRequest,
    User,
    Notification
)
from ..schemas import TeamCreate, TeamResponse, TeamUpdate


# -----------------------------
# ENVIRONMENT
# -----------------------------

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")


# -----------------------------
# EMAIL HELPER
# -----------------------------

def send_team_email(
    receiver_email: str,
    subject: str,
    message_text: str
):
    if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
        raise RuntimeError(
            "SMTP_EMAIL or SMTP_APP_PASSWORD is not configured"
        )

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = SMTP_EMAIL
    message["To"] = receiver_email

    message.set_content(message_text)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()

        server.login(
            SMTP_EMAIL,
            SMTP_APP_PASSWORD
        )

        server.send_message(message)


# -----------------------------
# ROUTER
# -----------------------------

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


# -----------------------------
# HELPERS
# -----------------------------

def split_data(value):
    return [
        x.strip()
        for x in (value or "").split(",")
        if x.strip()
    ]


def convert_team(team):
    return {
        "team_id": team.team_id,
        "team_name": team.team_name,
        "description": team.description or "",
        "team_size": team.team_size or 2,
        "location": team.location or "",
        "required_skills": split_data(
            team.required_skills
        ),
        "required_roles": split_data(
            team.required_roles
        ),
        "interests": split_data(
            team.interests
        ),
        "created_by": team.created_by,
        "created_at": team.created_at,
        "hackathon_date": team.hackathon_date
    }


# -----------------------------
# CREATE TEAM
# -----------------------------

@router.post(
    "/",
    response_model=TeamResponse
)
def create_team(
    data: TeamCreate,
    db: Session = Depends(get_db)
):
    creator = db.query(User).filter(
        User.user_id == data.created_by
    ).first()

    if not creator:
        raise HTTPException(
            status_code=404,
            detail="Creator user not found"
        )

    team = Team(
        team_name=data.team_name,
        description=data.description,
        team_size=data.team_size,
        location=data.location,
        required_skills=",".join(
            data.required_skills
        ),
        required_roles=",".join(
            data.required_roles
        ),
        interests=",".join(
            data.interests
        ),
        hackathon_date=data.hackathon_date,
        created_by=data.created_by
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    # Team creator automatically becomes first member
    db.add(
        TeamMember(
            team_id=team.team_id,
            user_id=data.created_by
        )
    )

    db.commit()

    return convert_team(team)


# -----------------------------
# GET ALL TEAMS
# -----------------------------

@router.get(
    "/",
    response_model=list[TeamResponse]
)
def get_teams(
    db: Session = Depends(get_db)
):
    teams = db.query(Team).all()

    return [
        convert_team(team)
        for team in teams
    ]


# -----------------------------
# GET SINGLE TEAM
# -----------------------------

@router.get(
    "/{team_id}",
    response_model=TeamResponse
)
def get_team(
    team_id: int,
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(
        Team.team_id == team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    return convert_team(team)


# -----------------------------
# UPDATE TEAM
# -----------------------------

@router.put(
    "/{team_id}",
    response_model=TeamResponse
)
def update_team(
    team_id: int,
    data: TeamUpdate,
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(
        Team.team_id == team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    if data.team_name is not None:
        team.team_name = data.team_name

    if data.description is not None:
        team.description = data.description

    if data.required_skills is not None:
        team.required_skills = ",".join(
            data.required_skills
        )

    if data.required_roles is not None:
        team.required_roles = ",".join(
            data.required_roles
        )

    if data.interests is not None:
        team.interests = ",".join(
            data.interests
        )

    db.commit()
    db.refresh(team)

    return convert_team(team)


# -----------------------------
# GET TEAM MEMBERS
# -----------------------------

@router.get("/{team_id}/members")
def get_team_members(
    team_id: int,
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(
        Team.team_id == team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    members = db.query(
        TeamMember
    ).filter(
        TeamMember.team_id == team_id
    ).all()

    result = []

    for member in members:

        user = db.query(User).filter(
            User.user_id == member.user_id
        ).first()

        if user:
            result.append({
                "user_id": user.user_id,
                "name": user.name,
                "skills": split_data(user.skills),
                "roles": split_data(user.roles),
                "interests": split_data(user.interests),
                "rating": user.rating or 0
            })

    return {
        "team_id": team_id,
        "members": result
    }


# -----------------------------
# REQUEST TO JOIN TEAM
# -----------------------------
@router.get("/{team_id}/join-status")
def get_join_status(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(
        Team.team_id == team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    request = db.query(JoinRequest).filter(
        JoinRequest.team_id == team_id,
        JoinRequest.user_id == user_id,
        JoinRequest.status == "pending"
    ).first()

    if request:
        return {"status": "pending"}

    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()

    if member:
        return {"status": "joined"}

    return {"status": "none"}
@router.post("/{team_id}/join")
def join_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(
        Team.team_id == team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    already_member = db.query(
        TeamMember
    ).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()

    if already_member:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to this team"
        )

    member_count = db.query(
        TeamMember
    ).filter(
        TeamMember.team_id == team_id
    ).count()

    team_size = team.team_size or 2

    if member_count >= team_size:
        raise HTTPException(
            status_code=400,
            detail="This team is already full"
        )

    existing_request = db.query(
        JoinRequest
    ).filter(
        JoinRequest.team_id == team_id,
        JoinRequest.user_id == user_id,
        JoinRequest.status == "pending"
    ).first()

    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Join request already pending"
        )

    join_request = JoinRequest(
        team_id=team_id,
        user_id=user_id,
        status="pending"
    )

    db.add(join_request)

    # In-app notification for leader
    notification = Notification(
        user_id=team.created_by,
        message=(
            f"{user.name} requested to join "
            f"your team '{team.team_name}'."
        ),
        notification_type="join_request"
    )

    db.add(notification)

    db.commit()
    db.refresh(join_request)

    # Email notification for leader
    leader = db.query(User).filter(
        User.user_id == team.created_by
    ).first()

    if leader and leader.email:
        try:
            send_team_email(
                receiver_email=leader.email,
                subject="New HackMates Team Join Request",
                message_text=f"""
Hello {leader.name},

You have a new team join request on HackMates.

{user.name} has requested to join your team
"{team.team_name}".

Please open HackMates to accept or reject the request.

Regards,
HackMates Team
"""
            )

        except Exception as error:
            print(
                "Join request email error:",
                error
            )

    return {
        "message": "Join request sent successfully",
        "request_id": join_request.request_id
    }


# -----------------------------
# GET JOIN REQUESTS
# -----------------------------

@router.get("/{team_id}/join-requests")
def get_join_requests(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    team = db.query(Team).filter(
        Team.team_id == team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    if team.created_by != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the team leader can view join requests"
        )

    requests = db.query(
        JoinRequest
    ).filter(
        JoinRequest.team_id == team_id,
        JoinRequest.status == "pending"
    ).all()

    result = []

    for request in requests:

        user = db.query(User).filter(
            User.user_id == request.user_id
        ).first()

        if user:
            result.append({
                "request_id": request.request_id,
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "skills": split_data(user.skills),
                "roles": split_data(user.roles),
                "interests": split_data(user.interests),
                "status": request.status,
                "created_at": request.created_at
            })

    return {
        "team_id": team_id,
        "requests": result
    }


# -----------------------------
# ACCEPT / REJECT JOIN REQUEST
# -----------------------------

@router.put(
    "/join-requests/{request_id}"
)
def respond_to_join_request(
    request_id: int,
    leader_id: int,
    action: str,
    db: Session = Depends(get_db)
):
    join_request = db.query(
        JoinRequest
    ).filter(
        JoinRequest.request_id == request_id
    ).first()

    if not join_request:
        raise HTTPException(
            status_code=404,
            detail="Join request not found"
        )

    team = db.query(Team).filter(
        Team.team_id == join_request.team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    if team.created_by != leader_id:
        raise HTTPException(
            status_code=403,
            detail="Only the team leader can respond"
        )

    if join_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Join request already processed"
        )

    if action not in ["accept", "reject"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be accept or reject"
        )

    # Find requester
    requester = db.query(User).filter(
        User.user_id == join_request.user_id
    ).first()

    if not requester:
        raise HTTPException(
            status_code=404,
            detail="Requesting user not found"
        )

    # -----------------------------
    # REJECT
    # -----------------------------

    if action == "reject":

        join_request.status = "rejected"

        notification = Notification(
            user_id=join_request.user_id,
            message=(
                f"Your request to join team "
                f"'{team.team_name}' was rejected."
            ),
            notification_type="join_rejected"
        )

        db.add(notification)
        db.commit()

        if requester.email:
            try:
                send_team_email(
                    receiver_email=requester.email,
                    subject="HackMates Join Request Rejected",
                    message_text=f"""
Hello {requester.name},

Your request to join the HackMates team
"{team.team_name}" has been rejected.

You can explore other teams on HackMates.

Regards,
HackMates Team
"""
                )

            except Exception as error:
                print(
                    "Join rejection email error:",
                    error
                )

        return {
            "message": "Join request rejected"
        }

    # -----------------------------
    # ACCEPT
    # -----------------------------

    member_count = db.query(
        TeamMember
    ).filter(
        TeamMember.team_id == team.team_id
    ).count()

    if member_count >= (
        team.team_size or 2
    ):
        raise HTTPException(
            status_code=400,
            detail="This team is already full"
        )

    already_member = db.query(
        TeamMember
    ).filter(
        TeamMember.team_id == team.team_id,
        TeamMember.user_id == join_request.user_id
    ).first()

    if not already_member:

        db.add(
            TeamMember(
                team_id=team.team_id,
                user_id=join_request.user_id
            )
        )

    join_request.status = "accepted"

    notification = Notification(
        user_id=join_request.user_id,
        message=(
            f"Your request to join team "
            f"'{team.team_name}' was accepted."
        ),
        notification_type="join_accepted"
    )

    db.add(notification)

    db.commit()

    if requester.email:
        try:
            send_team_email(
                receiver_email=requester.email,
                subject="HackMates Join Request Accepted",
                message_text=f"""
Hello {requester.name},

Your request to join the HackMates team
"{team.team_name}" has been accepted.

You are now a member of the team.

Regards,
HackMates Team
"""
            )

        except Exception as error:
            print(
                "Join acceptance email error:",
                error
            )

    return {
        "message": "Join request accepted"
    }