from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)

    is_email_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )

    verification_code_hash = Column(
        String(255),
        nullable=True
    )

    verification_code_expires_at = Column(
        DateTime,
        nullable=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    skills = Column(
        Text,
        default=""
    )

    skill_levels = Column(
        Text,
        default="{}"
    )

    roles = Column(
        Text,
        default=""
    )

    interests = Column(
        Text,
        default=""
    )

    bio = Column(Text, default="")
    location = Column(String(150), default="")

    rating = Column(
        Float,
        default=0.0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    team_memberships = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Team(Base):
    __tablename__ = "teams"

    team_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    team_name = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        default=""
    )

    team_size = Column(
        Integer,
        nullable=False,
        default=4
    )

    location = Column(
        String(150),
        nullable=False,
        default=""
    )

    required_skills = Column(
        Text,
        default=""
    )

    required_roles = Column(
        Text,
        default=""
    )

    interests = Column(
        Text,
        default=""
    )

    created_by = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    hackathon_date = Column(
        DateTime,
        nullable=True
    )

    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan"
    )


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.team_id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    joined_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    team = relationship(
        "Team",
        back_populates="members"
    )

    user = relationship(
        "User",
        back_populates="team_memberships"
    )


class JoinRequest(Base):
    __tablename__ = "join_requests"

    request_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.team_id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    status = Column(
        String(30),
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Invitation(Base):
    __tablename__ = "invitations"

    invitation_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.team_id"),
        nullable=False
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    status = Column(
        String(30),
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Rating(Base):
    __tablename__ = "ratings"

    rating_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    rated_user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    rated_by_user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    rating = Column(
        Float,
        nullable=False
    )

    comment = Column(
        Text,
        default=""
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    connection_id = Column(
        Integer,
        ForeignKey("connections.connection_id"),
        nullable=True
    )

    message = Column(
        Text,
        nullable=False
    )

    notification_type = Column(
        String(50),
        default="general"
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Connection(Base):
    __tablename__ = "connections"

    connection_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    status = Column(
        String(30),
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    receiver_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class TeamMessage(Base):
    __tablename__ = "team_messages"

    message_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.team_id"),
        nullable=False
    )

    sender_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    
        
class CompletedHackathon(Base):
    __tablename__ = "completed_hackathons"

    hackathon_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Hackathon details
    title = Column(
        String(200),
        nullable=False
    )

    organizer = Column(
        String(200),
        default=""
    )

    college = Column(
        String(200),
        default=""
    )

    date = Column(
        String(100),
        default=""
    )

    location = Column(
        String(200),
        default=""
    )

    problem_statement = Column(
        Text,
        default=""
    )

    # General project ideas
    project_ideas = Column(
        Text,
        default="[]"
    )

    # First-place winner
    first_place = Column(
        String(200),
        default=""
    )

    first_project_name = Column(
        String(300),
        default=""
    )

    first_project_description = Column(
        Text,
        default=""
    )

    # Second-place winner
    second_place = Column(
        String(200),
        default=""
    )

    second_project_name = Column(
        String(300),
        default=""
    )

    second_project_description = Column(
        Text,
        default=""
    )

    # Third-place winner
    third_place = Column(
        String(200),
        default=""
    )

    third_project_name = Column(
        String(300),
        default=""
    )

    third_project_description = Column(
        Text,
        default=""
    )

    # Official source
    source_url = Column(
        Text,
        default=""
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )