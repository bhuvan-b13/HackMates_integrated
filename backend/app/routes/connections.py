from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Connection, User, Notification


router = APIRouter(
    prefix="/connections",
    tags=["Connections"]
)


# =========================================================
# SEND CONNECTION REQUEST
# =========================================================

@router.post("/request")
def send_connection_request(
    sender_id: int,
    receiver_id: int,
    db: Session = Depends(get_db)
):

    if sender_id == receiver_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot connect with yourself"
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

    existing = (
        db.query(Connection)
        .filter(
            Connection.sender_id == sender_id,
            Connection.receiver_id == receiver_id
        )
        .first()
    )

    reverse = (
        db.query(Connection)
        .filter(
            Connection.sender_id == receiver_id,
            Connection.receiver_id == sender_id
        )
        .first()
    )

    if existing or reverse:
        raise HTTPException(
            status_code=400,
            detail="Connection already exists or is pending"
        )

    connection = Connection(
        sender_id=sender_id,
        receiver_id=receiver_id,
        status="pending"
    )

    db.add(connection)
    db.flush()

    notification = Notification(
        user_id=receiver_id,
        connection_id=connection.connection_id,
        message=f"{sender.name} sent you a connection request.",
        notification_type="connection_request"
    )

    db.add(notification)

    db.commit()
    db.refresh(connection)

    return {
        "message": "Connection request sent",
        "connection_id": connection.connection_id
    }


# =========================================================
# GET ACCEPTED CONNECTIONS
# =========================================================

@router.get("/{user_id}")
def get_connections(
    user_id: int,
    db: Session = Depends(get_db)
):

    connections = (
        db.query(Connection)
        .filter(
            (
                (Connection.sender_id == user_id)
                |
                (Connection.receiver_id == user_id)
            ),
            Connection.status == "accepted"
        )
        .all()
    )

    result = []

    for connection in connections:

        other_user_id = (
            connection.receiver_id
            if connection.sender_id == user_id
            else connection.sender_id
        )

        other_user = (
            db.query(User)
            .filter(User.user_id == other_user_id)
            .first()
        )

        if other_user:

            result.append({
                "connection_id": connection.connection_id,
                "user_id": other_user.user_id,
                "name": other_user.name,
                "email": other_user.email
            })

    return result


# =========================================================
# GET PENDING REQUESTS RECEIVED
# =========================================================

@router.get("/{user_id}/requests")
def get_connection_requests(
    user_id: int,
    db: Session = Depends(get_db)
):

    requests = (
        db.query(Connection)
        .filter(
            Connection.receiver_id == user_id,
            Connection.status == "pending"
        )
        .all()
    )

    result = []

    for connection in requests:

        sender = (
            db.query(User)
            .filter(User.user_id == connection.sender_id)
            .first()
        )

        if sender:

            result.append({
                "connection_id": connection.connection_id,
                "user_id": sender.user_id,
                "name": sender.name,
                "email": sender.email
            })

    return result

# =========================================================
# GET OUTGOING PENDING REQUESTS
# =========================================================

@router.get("/{user_id}/sent")
def get_sent_connection_requests(
    user_id: int,
    db: Session = Depends(get_db)
):

    requests = (
        db.query(Connection)
        .filter(
            Connection.sender_id == user_id,
            Connection.status == "pending"
        )
        .all()
    )

    result = []

    for connection in requests:

        receiver = (
            db.query(User)
            .filter(
                User.user_id == connection.receiver_id
            )
            .first()
        )

        if receiver:

            result.append({
                "connection_id": connection.connection_id,
                "user_id": receiver.user_id,
                "name": receiver.name,
                "email": receiver.email
            })

    return result

# =========================================================
# ACCEPT CONNECTION REQUEST
# =========================================================

@router.put("/{connection_id}/accept")
def accept_connection_request(
    connection_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):

    connection = (
        db.query(Connection)
        .filter(
            Connection.connection_id == connection_id
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Connection request not found"
        )

    if connection.receiver_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot accept this request"
        )

    if connection.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Connection request already processed"
        )

    connection.status = "accepted"

    sender = (
        db.query(User)
        .filter(User.user_id == connection.sender_id)
        .first()
    )

    receiver = (
        db.query(User)
        .filter(User.user_id == connection.receiver_id)
        .first()
    )

    if sender:

        notification = Notification(
            user_id=sender.user_id,
            connection_id=connection.connection_id,
            message=(
                f"{receiver.name} accepted your "
                "connection request."
                if receiver
                else "Your connection request was accepted."
            ),
            notification_type="connection_accepted"
        )

        db.add(notification)

    db.commit()

    return {
        "message": "Connection request accepted"
    }


# =========================================================
# REJECT CONNECTION REQUEST
# =========================================================

@router.put("/{connection_id}/reject")
def reject_connection_request(
    connection_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):

    connection = (
        db.query(Connection)
        .filter(
            Connection.connection_id == connection_id
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Connection request not found"
        )

    if connection.receiver_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot reject this request"
        )

    if connection.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Connection request already processed"
        )

    connection.status = "rejected"

    sender = (
        db.query(User)
        .filter(User.user_id == connection.sender_id)
        .first()
    )

    receiver = (
        db.query(User)
        .filter(User.user_id == connection.receiver_id)
        .first()
    )

    if sender:

        notification = Notification(
            user_id=sender.user_id,
            connection_id=connection.connection_id,
            message=(
                f"{receiver.name} rejected your "
                "connection request."
                if receiver
                else "Your connection request was rejected."
            ),
            notification_type="connection_rejected"
        )

        db.add(notification)

    db.commit()

    return {
        "message": "Connection request rejected"
    }