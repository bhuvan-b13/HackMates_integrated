from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Invitation, Team, User
from ..schemas import InvitationCreate, InvitationResponse

router = APIRouter(prefix="/invitations", tags=["Invitations"])

@router.post("/", response_model=InvitationResponse)
def create_invitation(data: InvitationCreate, db: Session = Depends(get_db)):
    if not db.query(Team).filter(Team.team_id == data.team_id).first():
        raise HTTPException(status_code=404, detail="Team not found")
    if not db.query(User).filter(User.user_id == data.sender_id).first():
        raise HTTPException(status_code=404, detail="Sender not found")
    if not db.query(User).filter(User.user_id == data.receiver_id).first():
        raise HTTPException(status_code=404, detail="Receiver not found")
    invitation = Invitation(team_id=data.team_id, sender_id=data.sender_id, receiver_id=data.receiver_id, status="pending")
    db.add(invitation); db.commit(); db.refresh(invitation)
    return invitation

@router.get("/user/{user_id}", response_model=list[InvitationResponse])
def get_user_invitations(user_id: int, db: Session = Depends(get_db)):
    return db.query(Invitation).filter(Invitation.receiver_id == user_id).all()

@router.put("/{invitation_id}")
def update_invitation(invitation_id: int, status: str, db: Session = Depends(get_db)):
    if status not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Status must be accepted or rejected")
    invitation = db.query(Invitation).filter(Invitation.invitation_id == invitation_id).first()
    if not invitation: raise HTTPException(status_code=404, detail="Invitation not found")
    invitation.status = status; db.commit()
    return {"message": f"Invitation {status}"}
