from app.services.web_search import search_web
from app.services.hackathon_finder import find_completed_hackathons


results = search_web(
    "completed hackathon 2026 India winners",
    max_results=5
)

print("SEARCH RESULTS:")
print(results)

print("\nCOMPLETED HACKATHONS:")
print(find_completed_hackathons(results))