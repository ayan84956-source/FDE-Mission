import json
import sqlite3
from contextlib import closing
from datetime import datetime
from config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    job_id TEXT NOT NULL,
    display_name TEXT,
    read_status TEXT NOT NULL,
    skills TEXT,
    unverified_skills TEXT,
    years_experience REAL,
    location TEXT,
    education TEXT,
    job_titles TEXT,
    label TEXT NOT NULL,
    note TEXT,
    summary TEXT,
    score INTEGER NOT NULL DEFAULT 0,
    rule_rows TEXT,
    decision TEXT NOT NULL DEFAULT 'pending',
    decided_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (source_file, job_id)
);
"""
STATUS_NOTES = {
    "needs_ocr": "Scanned resume, please check manually",
    "unreadable": "Could not open the file, please check manually",
    "unsupported": "Unsupported file type, please check manually",
    "model_failed": "The AI could not read this resume, please check manually",
    "no_attachment": "The email has no attachment, please check it manually",}
DECISIONS = ("pending", "approved", "rejected")

def connect():
    settings.DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(connect()) as conn:
        conn.executescript(SCHEMA)

def run(sql, params=()):
    with closing(connect()) as conn:
        with conn:
            conn.execute(sql, params)

def fetch(sql, params=()):
    with closing(connect()) as conn:
        return [dict(row) for row in conn.execute(sql, params)]

def save_result(source_file, job_id, read_status, facts=None, evaluation=None,
                score=0, display_name=None):
    """Save one resume's result. Keeps any decision the recruiter already made."""
    facts = facts or {}
    if evaluation is None:
        label = "needs_review"
        note = STATUS_NOTES.get(read_status, "Please check this resume manually")
        summary = None
        rule_rows = None
    else:
        label = evaluation["label"]
        note = evaluation["note"]
        summary = evaluation["summary"]
        rule_rows = json.dumps(
            {
                "must_have": evaluation["must_have"],
                "nice_to_have": evaluation["nice_to_have"],
            }
        )

    run(
        """
        INSERT INTO resumes (
            source_file, job_id, display_name, read_status, skills,
            unverified_skills, years_experience, location, education,
            job_titles, label, note, summary, score, rule_rows, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (source_file, job_id) DO UPDATE SET
            display_name = excluded.display_name,
            read_status = excluded.read_status,
            skills = excluded.skills,
            unverified_skills = excluded.unverified_skills,
            years_experience = excluded.years_experience,
            location = excluded.location,
            education = excluded.education,
            job_titles = excluded.job_titles,
            label = excluded.label,
            note = excluded.note,
            summary = excluded.summary,
            score = excluded.score,
            rule_rows = excluded.rule_rows
        """,
        (
            source_file,
            job_id,
            display_name,
            read_status,
            json.dumps(facts.get("skills", [])),
            json.dumps(facts.get("unverified_skills", [])),
            facts.get("total_years_experience"),
            facts.get("location"),
            facts.get("education"),
            json.dumps(facts.get("job_titles", [])),
            label,
            note,
            summary,
            score,
            rule_rows,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

def list_candidates(job_id):
    """All resumes for one opening, in ranking order."""
    rows = fetch(
        """
        SELECT * FROM resumes
        WHERE job_id = ?
        ORDER BY (label = 'strong_match') DESC, score DESC, years_experience DESC
        """,
        (job_id,),
    )
    for row in rows:
        for key in ("skills", "unverified_skills", "job_titles"):
            row[key] = json.loads(row[key] or "[]")
        row["rule_rows"] = json.loads(row["rule_rows"]) if row["rule_rows"] else None
    return rows

def set_decision(resume_id, decision):
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of {DECISIONS}")
    decided_at = None
    if decision != "pending":
        decided_at = datetime.now().isoformat(timespec="seconds")
    run(
        "UPDATE resumes SET decision = ?, decided_at = ? WHERE id = ?",
        (decision, decided_at, resume_id),
    )

def delete_decided(job_id, decision):
    """Delete every saved result with this decision. Returns their file names."""
    rows = fetch(
        "SELECT source_file FROM resumes WHERE job_id = ? AND decision = ?",
        (job_id, decision),
    )
    run("DELETE FROM resumes WHERE job_id = ? AND decision = ?", (job_id, decision))
    return [row["source_file"] for row in rows]


def is_processed(source_file, job_id):
    """True if this resume was already read successfully for this opening."""
    rows = fetch(
        "SELECT 1 FROM resumes WHERE source_file = ? AND job_id = ? AND read_status = 'ok'",
        (source_file, job_id),
    )
    return len(rows) > 0

if __name__ == "__main__":
    from agent.check_rules import evaluate, load_checklist
    from agent.score import calculate_score

    init_db()
    checklist = load_checklist("backend_python_developer")
    job_id = checklist["job_id"]

    samples = {
        "rahul_mehta.pdf": {
            "skills": ["Python", "Flask", "FastAPI", "PostgreSQL", "SQL", "Git", "pytest"],
            "total_years_experience": 3.0,
            "location": "Ahmedabad, Gujarat",
            "education": "B.Tech in Computer Engineering",
            "job_titles": ["Software Engineer", "Backend Developer"],
        },
        "priya_shah.pdf": {
            "skills": ["Java", "Spring"],
            "total_years_experience": 1.0,
            "location": "Mumbai",
            "education": "BCA",
            "job_titles": ["Java Developer"],
        },
    }

    for filename, facts in samples.items():
        evaluation = evaluate(facts, checklist)
        score = calculate_score(evaluation)
        save_result(filename, job_id, "ok", facts, evaluation, score)

    save_result("scan_001.pdf", job_id, "needs_ocr")

    rows = list_candidates(job_id)
    for row in rows:
        print(
            f"{row['id']}. {row['source_file']:16} {row['label']:13} "
            f"score {row['score']:3}  decision: {row['decision']:9} {row['note']}"
        )

    set_decision(rows[0]["id"], "approved")
    print("\nApproved:", rows[0]["source_file"])