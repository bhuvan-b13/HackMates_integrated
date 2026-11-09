from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Notification, User, Connection


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# =========================================================
# GET NOTIFICATIONS
# =========================================================

@router.get("/{user_id}")
def get_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    result = []

    for notification in notifications:

        connection_status = None

        if notification.connection_id:
            connection = db.query(Connection).filter(
                Connection.connection_id == notification.connection_id
            ).first()

            if connection:
                connection_status = connection.status

        result.append({
            "notification_id": notification.notification_id,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "connection_id": notification.connection_id,
            "connection_status": connection_status
        })

    return result


# =========================================================
# CREATE NOTIFICATION
# =========================================== ==============

@router.post("/")
def create_notification(
    user_id: int,
    message: str,
    notification_type: str = "general",
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    notification = Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return {
        "message": "Notification created",
        "notification_id": notification.notification_id
    }


# =========================================================
# MARK NOTIFICATION AS READ
# =========================================================

@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.notification_id == notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()

    return {
        "message": "Notification marked as read"
    }