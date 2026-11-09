from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Rating, User
from ..schemas import RatingCreate, RatingResponse

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.post("/", response_model=RatingResponse)
def create_rating(data: RatingCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == data.rated_user_id).first()
    if not user: raise HTTPException(status_code=404, detail="Rated user not found")
    rating = Rating(
        rated_user_id=data.rated_user_id,
        rated_by_user_id=data.rated_by_user_id,
        rating=data.rating, comment=data.comment
    )
    db.add(rating); db.commit(); db.refresh(rating)
    ratings = db.query(Rating).filter(Rating.rated_user_id == data.rated_user_id).all()
    user.rating = round(sum(r.rating for r in ratings) / len(ratings), 2)
    db.commit()
    return rating

@router.get("/user/{user_id}")
def get_user_ratings(user_id: int, db: Session = Depends(get_db)):
    return db.query(Rating).filter(Rating.rated_user_id == user_id).all()
