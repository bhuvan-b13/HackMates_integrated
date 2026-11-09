def rating_score(rating):
    return rating / 5


def compatibility_score(
    skill_score,
    role_score,
    interest_score,
    rating
):
    score = (
        skill_score * 0.40 +
        role_score * 0.30 +
        interest_score * 0.15 +
        rating_score(rating) * 0.15
    )

    return round(score * 100, 2)

def hackathon_match_score(skill_score, interest_score):
    score = (
        skill_score * 0.70 +
        interest_score * 0.30
    )

    return round(score * 100, 2)