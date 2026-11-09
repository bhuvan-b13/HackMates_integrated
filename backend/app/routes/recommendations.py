from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Team, TeamMember, User
from ..schemas import RecommendationResponse
from ..services.recommendation_service import recommend_users_for_team

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/{team_id}", response_model=list[RecommendationResponse])
def get_recommendations(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.team_id == team_id).first()
    if not team: raise HTTPException(status_code=404, detail="Team not found")

    member_ids = {m.user_id for m in db.query(TeamMember).filter(TeamMember.team_id == team_id).all()}
    users = db.query(User).filter(~User.user_id.in_(member_ids)).all()

    return recommend_users_for_team(team, users)