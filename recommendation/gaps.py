def find_missing_skills(required_skills, current_team_skills):
    required_skills = set(required_skills)
    current_team_skills = set(current_team_skills)

    missing_skills = required_skills - current_team_skills

    return list(missing_skills)

def find_missing_roles(required_roles, current_team_roles):
    required_roles = set(required_roles)
    current_team_roles = set(current_team_roles)

    missing_roles = required_roles - current_team_roles

    return list(missing_roles)

def team_strength_score(required_skills, current_team_skills):
    required_skills = set(required_skills)
    current_team_skills = set(current_team_skills)

    if len(required_skills) == 0:
        return 0

    covered_skills = required_skills.intersection(current_team_skills)

    score = len(covered_skills) / len(required_skills)

    return round(score * 100, 2)