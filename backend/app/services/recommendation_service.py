from recommendation.engine import recommend_candidates
from recommendation.matching import (
    skill_match,
    role_match,
    interest_match,
)


def recommend_users_for_team(team, users):
    candidates = [
        {
            "id": user.user_id,
            "name": user.name,
            "skills": [
                skill.strip()
                for skill in (user.skills or "").split(",")
                if skill.strip()
            ],
            "roles": [
                role.strip()
                for role in (user.roles or "").split(",")
                if role.strip()
            ],
            "interests": [
                interest.strip()
                for interest in (user.interests or "").split(",")
                if interest.strip()
            ],
            "rating": user.rating or 0,
        }
        for user in users
    ]

    team_data = {
        "required_skills": [
            skill.strip()
            for skill in (team.required_skills or "").split(",")
            if skill.strip()
        ],
        "required_roles": [
            role.strip()
            for role in (team.required_roles or "").split(",")
            if role.strip()
        ],
        "interests": [
            interest.strip()
            for interest in (team.interests or "").split(",")
            if interest.strip()
        ],
    }
    engine_results = recommend_candidates(candidates, team_data)

    results = []

    for result in engine_results:
        # Find the original candidate so we can calculate
        # the detailed matches for the API response.
        candidate = next(
            (
                user
                for user in candidates
                if user["id"] == result["id"]
            ),
            None,
        )

        if candidate is None:
            continue

        _, matched_skills = skill_match(
            candidate["skills"],
            team_data["required_skills"],
        )

        _, matched_roles = role_match(
            candidate["roles"],
            team_data["required_roles"],
        )

        _, matched_interests = interest_match(
            candidate["interests"],
            team_data["interests"],
        )

        results.append(
            {
                "user_id": result["id"],
                "name": result["name"],
                "compatibility_score": result["score"],
                "matched_skills": matched_skills,
                "matched_roles": matched_roles,
                "matched_interests": matched_interests,
                "reason": ". ".join(result["reasons"]),
            }
        )

    return results