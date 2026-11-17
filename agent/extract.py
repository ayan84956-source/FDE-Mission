from agent.llm import ask_json
from config import settings

PROMPT = """You extract facts from a resume. Use ONLY information that is
written in the resume. If something is not stated, use null.
Do not list skills the person is only learning or planning to learn.
Return JSON with exactly these fields:
- "skills": list of technical skills the person already has
- "total_years_experience": number
- "location": string
- "education": string
- "job_titles": list of strings

Resume:
{resume}
"""

def as_list(value):
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]

def as_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def as_text(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def verify_skills(skills, resume_text):
    """Split skills into those found in the resume text and those not found."""
    lowered = resume_text.lower()
    verified = [s for s in skills if s.lower() in lowered]
    unverified = [s for s in skills if s.lower() not in lowered]
    return verified, unverified

def extract(resume_text):
    """Ask the model for facts. Returns (facts, status)."""
    text = resume_text[: settings.MAX_RESUME_CHARS]
    data, seconds = ask_json(PROMPT.format(resume=text))

    if not isinstance(data, dict):
        return None, "model_failed"

    skills = as_list(data.get("skills"))
    verified, unverified = verify_skills(skills, text)

    facts = {
        "skills": verified,
        "unverified_skills": unverified,
        "total_years_experience": as_number(data.get("total_years_experience")),
        "location": as_text(data.get("location")),
        "education": as_text(data.get("education")),
        "job_titles": as_list(data.get("job_titles")),
        "seconds": round(seconds, 1),
    }
    return facts, "ok"

if __name__ == "__main__":
    import json
    from agent.convert import convert
    path = settings.SAMPLE_DATA / "rahul_mehta.pdf"
    text, status = convert(path)
    print("Convert Status:", status)
    facts, status = extract(text)
    print("Extract Status:", status)
    print(json.dumps(facts, indent = 2))