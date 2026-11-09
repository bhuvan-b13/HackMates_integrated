def skill_match(candidate_skills, required_skills):
    candidate_lookup = {
        skill.strip().casefold(): skill.strip()
        for skill in candidate_skills
        if skill.strip()
    }

    required_lookup = {
        skill.strip().casefold(): skill.strip()
        for skill in required_skills
        if skill.strip()
    }

    matched_keys = candidate_lookup.keys() & required_lookup.keys()

    if not required_lookup:
        return 0, []

    score = len(matched_keys) / len(required_lookup)

    matched_skills = [
        required_lookup[key]
        for key in matched_keys
    ]

    return score, matched_skills


def role_match(candidate_roles, required_roles):
    candidate_lookup = {
        role.strip().casefold(): role.strip()
        for role in candidate_roles
        if role.strip()
    }

    required_lookup = {
        role.strip().casefold(): role.strip()
        for role in required_roles
        if role.strip()
    }

    matched_keys = candidate_lookup.keys() & required_lookup.keys()

    if not required_lookup:
        return 0, []

    score = len(matched_keys) / len(required_lookup)

    matched_roles = [
        required_lookup[key]
        for key in matched_keys
    ]

    return score, matched_roles


def interest_match(candidate_interests, team_interests):
    candidate_lookup = {
        interest.strip().casefold(): interest.strip()
        for interest in candidate_interests
        if interest.strip()
    }

    team_lookup = {
        interest.strip().casefold(): interest.strip()
        for interest in team_interests
        if interest.strip()
    }

    matched_keys = candidate_lookup.keys() & team_lookup.keys()

    if not team_lookup:
        return 0, []

    score = len(matched_keys) / len(team_lookup)

    matched_interests = [
        team_lookup[key]
        for key in matched_keys
    ]

    return score, matched_interests


def hackathon_match(
    candidate_skills,
    hackathon_skills,
    candidate_interests,
    hackathon_interests
):
    skill_score, matched_skills = skill_match(
        candidate_skills,
        hackathon_skills
    )

    interest_score, matched_interests = interest_match(
        candidate_interests,
        hackathon_interests
    )

    return {
        "skill_score": skill_score,
        "interest_score": interest_score,
        "matched_skills": matched_skills,
        "matched_interests": matched_interests
    }