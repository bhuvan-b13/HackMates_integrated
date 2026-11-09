from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .database import Base, engine, get_db
from .models import CompletedHackathon

from .routes import (
    auth,
    users,
    teams,
    invitations,
    ratings,
    recommendations,
    notifications,
    connections,
    messages,
    completed_hackathons,
)

from .services.completed_hackathon_updater import (
    update_completed_hackathons
)


# Load environment variables
load_dotenv()


# Create database tables that do not already exist
Base.metadata.create_all(bind=engine)


# Add new project fields to the existing database safely
def migrate_completed_hackathons():
    with engine.begin() as connection:

        inspector = inspect(connection)

        if not inspector.has_table("completed_hackathons"):
            raise RuntimeError(
                "The completed_hackathons table does not exist."
            )

        existing_columns = {
            column["name"]
            for column in inspector.get_columns(
                "completed_hackathons"
            )
        }

        new_columns = {
            "first_project_name": "VARCHAR(300) DEFAULT ''",
            "first_project_description": "TEXT DEFAULT ''",
            "second_project_name": "VARCHAR(300) DEFAULT ''",
            "second_project_description": "TEXT DEFAULT ''",
            "third_project_name": "VARCHAR(300) DEFAULT ''",
            "third_project_description": "TEXT DEFAULT ''",
        }

        for column_name, column_type in new_columns.items():

            if column_name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE completed_hackathons "
                        f"ADD COLUMN {column_name} {column_type}"
                    )
                )

                print(
                    f"Added database column: {column_name}"
                )


# Run the database migration
migrate_completed_hackathons()


# Create FastAPI application
app = FastAPI(
    title="HackMate API",
    description=(
        "Hackathon Team Formation and Recommendation Platform"
    ),
    version="1.0.0"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Register existing routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(invitations.router)
app.include_router(ratings.router)
app.include_router(recommendations.router)
app.include_router(notifications.router)
app.include_router(connections.router)
app.include_router(messages.router)
app.include_router(completed_hackathons.router)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "HackMate Backend API is running",
        "version": "1.0.0",
        "status": "success"
    }


# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
 