from .matching import skill_match, role_match, interest_match
from .scoring import compatibility_score
from .ranking import rank_candidates
from .explanation import explain_candidate


def recommend_candidates(candidates, team):
    recommendations = []

    for candidate in candidates:

        skill_score, matched_skills = skill_match(
            candidate["skills"],
            team["required_skills"]
        )

        role_score, matched_roles = role_match(
            candidate["roles"],
            team["required_roles"]
        )

        interest_score, matched_interests = interest_match(
            candidate["interests"],
            team["interests"]
        )

        score = compatibility_score(
            skill_score,
            role_score,
            interest_score,
            candidate["rating"]
        )

        reasons = explain_candidate(
            matched_skills,
            matched_roles,
            matched_interests,
            candidate["rating"]
        )

        recommendations.append({
            "id": candidate["id"],
            "name": candidate["name"],
            "score": score,
            "reasons": reasons
        })

    return rank_candidates(recommendations)