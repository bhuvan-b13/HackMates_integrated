from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    skills: List[str] = []
    roles: List[str] = []
    interests: List[str] = []


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    skill_levels: Optional[dict] = None
    roles: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    bio: Optional[str] = None
    location: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    skills: List[str]
    skill_levels: dict = {}
    skills: List[str]
    roles: List[str]
    interests: List[str]
    bio: str = ""
    location: str = ""
    rating: float
    created_at: datetime


class TeamCreate(BaseModel):
    team_name: str
    description: str = ""
    team_size: int
    location: str
    required_skills: List[str] = []
    required_roles: List[str] = []
    interests: List[str] = []
    created_by: int
    hackathon_date: Optional[datetime] = None


class TeamUpdate(BaseModel):
    team_name: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    required_roles: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    hackathon_date: Optional[datetime] = None

class TeamResponse(BaseModel):
    team_id: int
    team_name: str
    description: str
    team_size: int = 4
    location: str = ""
    required_skills: List[str]
    required_roles: List[str]
    interests: List[str]
    created_by: int
    created_at: datetime
    hackathon_date: Optional[datetime] = None


class InvitationCreate(BaseModel):
    team_id: int
    sender_id: int
    receiver_id: int


class InvitationResponse(BaseModel):
    invitation_id: int
    team_id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime


class RatingCreate(BaseModel):
    rated_user_id: int
    rated_by_user_id: int
    rating: float = Field(ge=1, le=5)
    comment: str = ""


class RatingResponse(BaseModel):
    rating_id: int
    rated_user_id: int
    rated_by_user_id: int
    rating: float
    comment: str
    created_at: datetime


class RecommendationResponse(BaseModel):
    user_id: int
    name: str
    compatibility_score: float
    matched_skills: List[str]
    matched_roles: List[str]
    matched_interests: List[str]
    reason: str


class OTPVerify(BaseModel):
    user_id: int
    verification_code: str

class CompletedHackathonCreate(BaseModel):
    title: str
    organizer: str = ""
    college: str = ""
    date: str = ""
    location: str = ""
    problem_statement: str = ""
    project_ideas: List[str] = Field(default_factory=list)

    # First-place winner
    first_place: str = ""
    first_project_name: str = ""
    first_project_description: str = ""

    # Second-place winner
    second_place: str = ""
    second_project_name: str = ""
    second_project_description: str = ""

    # Third-place winner
    third_place: str = ""
    third_project_name: str = ""
    third_project_description: str = ""

    source_url: str = ""


class CompletedHackathonResponse(CompletedHackathonCreate):
    hackathon_id: int

    model_config = ConfigDict(from_attributes=True)