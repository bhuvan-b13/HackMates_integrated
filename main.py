from recommendation.matching import (
    skill_match,
    role_match,
    interest_match
)
from recommendation.explanation import explain_candidate
from recommendation.gaps import (
    find_missing_skills,
    find_missing_roles
)
from recommendation.engine import recommend_candidates
from recommendation.ranking import rank_candidates
from recommendation.gaps import team_strength_score
from recommendation.matching import hackathon_match
from recommendation.scoring import hackathon_match_score
from recommendation.scoring import compatibility_score


candidate_skills = ["Python", "SQL", "Machine Learning"]
required_skills = ["Python", "SQL", "React"]

candidate_roles = ["Data Scientist", "Backend Developer"]
required_roles = ["Data Scientist", "Frontend Developer"]

candidate_interests = ["AI", "Data Science"]
team_interests = ["AI", "Web Development"]

candidate_rating = 4.5


skill_score, matched_skills = skill_match(
    candidate_skills,
    required_skills
)

role_score, matched_roles = role_match(
    candidate_roles,
    required_roles
)

interest_score, matched_interests = interest_match(
    candidate_interests,
    team_interests
)

final_score = compatibility_score(
    skill_score,
    role_score,
    interest_score,
    candidate_rating
)


print("Skill Match:", skill_score * 100, "%")
print("Role Match:", role_score * 100, "%")
print("Interest Match:", interest_score * 100, "%")
print("Rating:", candidate_rating)
print("Compatibility Score:", final_score, "%")

required_team_skills = [
    "Python",
    "SQL",
    "React",
    "Machine Learning"
]

current_team_skills = [
    "Python",
    "SQL"
]

required_team_roles = [
    "Frontend Developer",
    "Backend Developer",
    "ML Developer"
]

current_team_roles = [
    "Backend Developer"
]

missing_skills = find_missing_skills(
    required_team_skills,
    current_team_skills
)

missing_roles = find_missing_roles(
    required_team_roles,
    current_team_roles
)

print("Missing Skills:", missing_skills)
print("Missing Roles:", missing_roles)

candidates = [
    {
        "name": "Bhuvan",
        "score": 85.5
    },
    {
        "name": "Harshitha",
        "score": 92.0
    },
    {
        "name": "Hari",
        "score": 78.5
    }
]

ranked_candidates = rank_candidates(candidates)

print("Ranked Candidates:")

for candidate in ranked_candidates:
    print(candidate["name"], "-", candidate["score"], "%")

reasons = explain_candidate(
    matched_skills,
    matched_roles,
    matched_interests,
    candidate_rating
)

print("\nWhy this candidate?")

for reason in reasons:
    print("-", reason)   
candidates = [
    {
        "id": 1,
        "name": "Bhuvan",
        "skills": ["Python", "SQL", "Machine Learning"],
        "roles": ["Data Scientist"],
        "interests": ["AI", "Data Science"],
        "rating": 4.5
    },
    {
        "id": 2,
        "name": "Harshitha",
        "skills": ["React", "JavaScript", "HTML"],
        "roles": ["Frontend Developer"],
        "interests": ["Web Development", "AI"],
        "rating": 4.2
    },
    {
        "id": 3,
        "name": "Hari",
        "skills": ["Python", "SQL"],
        "roles": ["Backend Developer"],
        "interests": ["Web Development"],
        "rating": 4.0
    }
]

team = {
    "required_skills": [
        "Python",
        "SQL",
        "React"
    ],
    "required_roles": [
        "Data Scientist",
        "Frontend Developer"
    ],
    "interests": [
        "AI",
        "Web Development"
    ]
}

recommendations = recommend_candidates(
    candidates,
    team
)

print("\nRECOMMENDATIONS")

for candidate in recommendations:
    print("\n", candidate["name"])
    print("Score:", candidate["score"], "%")
    print("Why:", candidate["reasons"])  

print("\nTEAM STRENGTH")

required_skills = ["Python", "SQL", "React", "Testing"]
team_skills = ["Python", "SQL", "React"]

strength = team_strength_score(
    required_skills,
    team_skills
)

print("Team Strength:", strength, "%")


print("\nHACKATHON MATCH")

candidate_skills = ["Python", "SQL"]
hackathon_skills = ["Python", "React"]

candidate_interests = ["AI"]
hackathon_interests = ["AI", "Web Development"]

match = hackathon_match(
    candidate_skills,
    hackathon_skills,
    candidate_interests,
    hackathon_interests
)

print("Skill Match:", round(match["skill_score"] * 100, 2), "%")
print("Interest Match:", round(match["interest_score"] * 100, 2), "%")
print("Matched Skills:", match["matched_skills"])
print("Matched Interests:", match["matched_interests"])


hackathon_score = hackathon_match_score(
    match["skill_score"],
    match["interest_score"]
)

print("Hackathon Match Score:", hackathon_score, "%")  