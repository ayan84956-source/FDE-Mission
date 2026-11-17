from agent.check_rules import MET, UNKNOWN, evaluate, load_checklist
from config import settings

def calculate_score(evaluation):
    must = evaluation["must_have"]
    nice = evaluation["nice_to_have"]
    must_points = 0.0
    for row in must:
        if row["status"] == MET:
            must_points += 1
        elif row["status"] == UNKNOWN:
            must_points += settings.UNKNOWN_CREDIT
    must_part = 0.0
    if must:
        must_part = must_points / len(must) * settings.MUST_HAVE_WEIGHT
    nice_met = sum(1 for row in nice if row["status"]== MET)
    nice_part = 0.0
    if nice:
        nice_part = nice_met / len(nice) * settings.NICE_TO_HAVE_WEIGHT
    return int(must_part + nice_part + 0.5)

def rank(candidates):
    """Sort candidates: strong matches first, then by score, then experience."""

    def sort_key(candidate):
        is_strong = candidate["evaluation"]["label"] == "strong_match"
        years = candidate["facts"].get("total_years_experience") or 0
        return (0 if is_strong else 1, -candidate["score"], -years)
    return sorted(candidates, key = sort_key)

if __name__ == "__main__":
    checklist = load_checklist("backend_python_developer")

    people = {
        "Rahul": {
            "skills": ["Python", "Flask", "FastAPI", "PostgreSQL", "SQL", "Git", "pytest"],
            "total_years_experience": 3.0,
            "location": "Ahmedabad, Gujarat",
        },
        "Priya": {
            "skills": ["Java", "Spring"],
            "total_years_experience": 1.0,
            "location": "Mumbai",
        },
        "Anil": {
            "skills": ["Python", "SQL"],
            "total_years_experience": None,
            "location": None,
        },
        "Dev": {
            "skills": ["Python", "SQL", "Docker", "AWS", "FastAPI"],
            "total_years_experience": 5.0,
            "location": "Ahmedabad",
        },
    }

    candidates = []
    for name, facts in people.items():
        evaluation = evaluate(facts, checklist)
        candidates.append(
            {
                "name": name,
                "facts": facts,
                "evaluation": evaluation,
                "score": calculate_score(evaluation),
            }
        )

    for position, c in enumerate(rank(candidates), start=1):
        ev = c["evaluation"]
        print(f"{position}. {c['name']:6} score {c['score']:3}  {ev['label']:13} {ev['summary']}")