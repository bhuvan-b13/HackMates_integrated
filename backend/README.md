# HackMate Backend

FastAPI + SQLite backend for the HackMate hackathon team formation platform.

## Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:
http://127.0.0.1:8000/docs

## Main APIs

- POST /auth/register
- POST /auth/login
- GET /users/
- GET /users/{user_id}
- POST /teams/
- GET /teams/
- GET /teams/{team_id}
- GET /teams/{team_id}/members
- POST /teams/{team_id}/join?user_id=2
- GET /recommendations/{team_id}
- POST /invitations/
- GET /invitations/user/{user_id}
- PUT /invitations/{invitation_id}?status=accepted
- POST /ratings/
- GET /ratings/user/{user_id}

The recommendation service is currently a compatible placeholder. Replace its internal algorithm with Bhuvan's completed recommendation function when his code is available.
