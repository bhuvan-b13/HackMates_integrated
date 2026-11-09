from app.services.ollama_service import ask_ollama
from app.services.hackathon_validator import validate_hackathon


prompt = """
Return ONLY valid JSON.

Extract this hackathon information:

{
    "title": "",
    "organizer": "",
    "college": "",
    "date": "",
    "location": "",
    "problem_statement": "",
    "project_ideas": [],
    "first_place": "",
    "second_place": "",
    "third_place": "",
    "source_url": ""
}

Text:
HackMates Sample Hackathon was organized by ABC Technologies
at XYZ College on 15 September 2026 in Bengaluru.
The problem statement was to build innovative AI solutions.
The winning project was Smart AI Assistant.
Second place was HealthConnect.
Third place was GreenTech.
"""


data = ask_ollama(prompt)

print("AI DATA:")
print(data)

print("\nVALID:")
print(validate_hackathon(data))