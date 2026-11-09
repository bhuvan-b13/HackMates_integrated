def explain_candidate(
    matched_skills,
    matched_roles,
    matched_interests,
    rating
):
    reasons = []

    if matched_skills:
        reasons.append(
            "Matches required skills: "
            + ", ".join(sorted(matched_skills))
        )

    if matched_roles:
        reasons.append(
            "Matches required roles: "
            + ", ".join(sorted(matched_roles))
        )

    if matched_interests:
        reasons.append(
            "Shares interests: "
            + ", ".join(sorted(matched_interests))
        )

    if rating >= 4:
        reasons.append("Strong participant rating")
    elif rating >= 3:
        reasons.append("Good participant rating")

    if not reasons:
        reasons.append(
            "Considered based on overall compatibility"
        )

    return reasons