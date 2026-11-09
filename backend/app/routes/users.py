import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserResponse, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


def split_data(value):
    return [
        x.strip()
        for x in (value or "").split(",")
        if x.strip()
    ]


def convert_user(user):
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "skills": split_data(user.skills),
        "skill_levels": json.loads(user.skill_levels or "{}"),
        "roles": split_data(user.roles),
        "interests": split_data(user.interests),
        "rating": user.rating or 0,
        "location": user.location or "",
        "bio": user.bio or "",
        "created_at": user.created_at,
        
    }


@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):

    users = db.query(User).filter(
        User.is_email_verified == True
    ).all()

    return [
        convert_user(user)
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return convert_user(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if data.name is not None:
        user.name = data.name

    if data.skills is not None:
        user.skills = ",".join(data.skills)

    if data.skill_levels is not None:
        user.skill_levels = json.dumps(data.skill_levels)        

    if data.roles is not None:
        user.roles = ",".join(data.roles)

    if data.interests is not None:
        user.interests = ",".join(data.interests)

    if data.bio is not None:
        user.bio = data.bio
    
    if data.location is not None:
        user.location = data.location

    db.commit()
    db.refresh(user)

    return convert_user(user)