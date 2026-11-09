from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import TeamMessage, TeamMember, Team
from ..database import get_db
from ..models import Connection, Message, User
from .auth import send_chat_message_email


router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


# =========================================================
# SEND MESSAGE
# =========================================================

@router.post("/send")
def send_message(
    sender_id: int,
    receiver_id: int,
    content: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    if sender_id == receiver_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot message yourself"
        )

    if not content.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    sender = (
        db.query(User)
        .filter(User.user_id == sender_id)
        .first()
    )

    receiver = (
        db.query(User)
        .filter(User.user_id == receiver_id)
        .first()
    )

    if not sender or not receiver:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    connection = (
        db.query(Connection)
        .filter(
            (
                (
                    (Connection.sender_id == sender_id)
                    &
                    (Connection.receiver_id == receiver_id)
                )
                |
                (
                    (Connection.sender_id == receiver_id)
                    &
                    (Connection.receiver_id == sender_id)
                )
            ),
            Connection.status == "accepted"
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=403,
            detail="You can only message connected users"
        )

    # Delete messages older than 24 hours
    expiry_time = (
        datetime.utcnow()
        - timedelta(hours=24)
    )

    db.query(Message).filter(
        Message.created_at < expiry_time
    ).delete(
        synchronize_session=False
    )

    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content.strip()
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    # =====================================================
    # SEND EMAIL IN BACKGROUND
    # =====================================================

    background_tasks.add_task(
        send_chat_message_email,
        receiver.email,
        sender.name,
        message.content
    )

    return {
        "message_id": message.message_id,
        "sender_id": message.sender_id,
        "receiver_id": message.receiver_id,
        "content": message.content,
        "created_at": message.created_at
    }


# =========================================================
# GET 1-TO-1 CONVERSATION
# =========================================================

@router.get("/{user_id}/{other_user_id}")
def get_messages(
    user_id: int,
    other_user_id: int,
    db: Session = Depends(get_db)
):

    if user_id == other_user_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation"
        )

    connection = (
        db.query(Connection)
        .filter(
            (
                (
                    (Connection.sender_id == user_id)
                    &
                    (Connection.receiver_id == other_user_id)
                )
                |
                (
                    (Connection.sender_id == other_user_id)
                    &
                    (Connection.receiver_id == user_id)
                )
            ),
            Connection.status == "accepted"
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=403,
            detail="You can only view messages with connected users"
        )

    # Delete messages older than 24 hours
    expiry_time = (
        datetime.utcnow()
        - timedelta(hours=24)
    )

    db.query(Message).filter(
        Message.created_at < expiry_time
    ).delete(
        synchronize_session=False
    )

    db.commit()

    messages = (
        db.query(Message)
        .filter(
            (
                (
                    (Message.sender_id == user_id)
                    &
                    (Message.receiver_id == other_user_id)
                )
                |
                (
                    (Message.sender_id == other_user_id)
                    &
                    (Message.receiver_id == user_id)
                )
            ),
            Message.created_at >= expiry_time
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )

    return [
        {
            "message_id": message.message_id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at
        }
        for message in messages
    ]

# =========================================================
# SEND TEAM MESSAGE
# =========================================================

@router.post("/team/{team_id}/send")
def send_team_message(
    team_id: int,
    sender_id: int,
    content: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if not content.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    team = db.query(Team).filter(
        Team.team_id == team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    sender = db.query(User).filter(
        User.user_id == sender_id
    ).first()

    if not sender:
        raise HTTPException(
            status_code=404,
            detail="Sender not found"
        )

    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == sender_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Only team members can send messages"
        )

    message = TeamMessage(
        team_id=team_id,
        sender_id=sender_id,
        content=content.strip()
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    # Email notification to other team members
    team_members = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id != sender_id
    ).all()

    for member in team_members:
        recipient = db.query(User).filter(
            User.user_id == member.user_id
        ).first()

        if recipient and recipient.email:
            background_tasks.add_task(
                send_chat_message_email,
                recipient.email,
                sender.name,
                f"[{team.team_name}] {message.content}"
            )

    return {
        "message_id": message.message_id,
        "team_id": message.team_id,
        "sender_id": message.sender_id,
        "content": message.content,
        "created_at": message.created_at
    }
# =========================================================
# GET TEAM CONVERSATION
# =========================================================

@router.get("/team/{team_id}/{user_id}")
def get_team_messages(
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

    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Only team members can view messages"
        )

    messages = (
        db.query(TeamMessage)
        .filter(TeamMessage.team_id == team_id)
        .order_by(TeamMessage.created_at.asc())
        .all()
    )

    result = []

    for message in messages:
        sender = db.query(User).filter(
            User.user_id == message.sender_id
        ).first()

        result.append({
            "message_id": message.message_id,
            "team_id": message.team_id,
            "sender_id": message.sender_id,
            "sender_name": sender.name if sender else None,
            "content": message.content,
            "created_at": message.created_at
        })

    return result