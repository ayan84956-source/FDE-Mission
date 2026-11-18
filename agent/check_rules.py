import json
from config import settings

MET = "met"
NOT_MET = "not_met"
UNKNOWN = "unknown"

def load_checklist(name):
    path = settings. CHECKLIST_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding = "utf-8"))

def check_experience(facts, minimum):
    years = facts.get("total_years_experience")
    if years is None:
        return UNKNOWN, "Years of experience not found in the resume"
    if years >= minimum:
        return MET, f"{years:g} years of experience (needs {minimum:g})"
    return NOT_MET, f"Only {years:g} years of experience (needs {minimum:g})"

def check_skill(facts, skill):
    known = [s.lower() for s in facts.get("skills", [])]
    if skill.lower() in known:
        return MET, f"{skill} found in the resume"
    return NOT_MET, f"{skill} not found in the resume"

def check_location(facts, places):
    location = facts.get("location")
    if not location:
        return UNKNOWN, "Location not found in the resume"
    for place in places:
        if place.lower() in location.lower():
            return MET, f"Location is {location}"
    return NOT_MET, f"Location is {location} (wanted: {', '.join(places)})"

def make_row(rule, result):
    status, reason = result
    return {"rule": rule, "status": status, "reason": reason}

def evaluate(facts, checklist):
    """Compare a candidate's facts with a checklist. No model is used here."""
    rules = checklist["must_have"]
    must = [make_row("Experience", check_experience(facts, rules["min_years_experience"]))]
    for skill in rules["required_skills"]:
        must.append(make_row(f"Skill: {skill}", check_skill(facts, skill)))
    must.append(make_row("Location", check_location(facts, rules["locations"])))

    nice = []
    for skill in checklist["nice_to_have"]["skills"]:
        nice.append(make_row(f"Skill: {skill}", check_skill(facts, skill)))

    must_statuses = [row["status"] for row in must]
    if NOT_MET in must_statuses:
        label, note = "need_review", "Missing a must-have"
    elif UNKNOWN in must_statuses:
        label, note = "needs_review", "Could not confirm a must-have"
    else:
        label, note = "strong_match", "Meets all must-haves"

    met_must = must_statuses.count(MET)
    met_nice = [row["status"] for row in nice].count(MET)
    summary = (
        f"Meets {met_must} of {len(must)} must-haves, "
        f"{met_nice} of {len(nice)} nice-to-haves"
    )

    return {
        "label": label,
        "note": note,
        "summary": summary,
        "must_have": must,
        "nice_to_have": nice,
    }

if __name__ == "__main__":
    checklist = load_checklist("backend_python_developer")

    candidates = {
        "Rahul (good fit)": {
            "skills": ["Python", "Flask", "FastAPI", "PostgreSQL", "SQL", "Git", "pytest"],
            "total_years_experience": 3.0,
            "location": "Ahmedabad, Gujarat",
        },
        "Priya (weak fit)": {
            "skills": ["Java", "Spring"],
            "total_years_experience": 1.0,
            "location": "Mumbai",
        },
        "Anil (missing info)": {
            "skills": ["Python", "SQL"],
            "total_years_experience": None,
            "location": None,
        },
    }

    for name, facts in candidates.items():
        result = evaluate(facts, checklist)
        print(f"\n{name}: {result['label']} - {result['note']}")
        print(result["summary"])
        for row in result["must_have"] + result["nice_to_have"]:
            print(f"  [{row['status']}] {row['rule']}: {row['reason']}")