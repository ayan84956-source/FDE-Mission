import time
from agent import database
from agent.check_rules import evaluate, load_checklist
from agent.extract import extract
from agent.score import calculate_score
from agent.convert import convert
from agent.anonymize import anonymize
from config import settings

def process_resume(path, checklist):
    start = time.time()
    job_id = checklist["job_id"]

    text, status = convert(path)
    if status != "ok":
        database.save_result(path.name, job_id, status)
        return status, 0, time.time() - start

    clean_text, name = anonymize(text)

    facts, status = extract(clean_text)
    if facts is None:
        database.save_result(path.name, job_id, status, display_name=name)
        return status, 0, time.time() - start

    evaluation = evaluate(facts, checklist)
    score = calculate_score(evaluation)
    database.save_result(
        path.name, job_id, "ok", facts, evaluation, score, display_name=name
    )
    return "ok", score, time.time() - start

def run(folder, job_name, force= False, pattern= "*"):
    database.init_db()
    checklist = load_checklist(job_name)
    job_id = checklist["job_id"]

    files = [
        f
        for f in sorted(folder.glob(pattern))
        if f.is_file() and not f.name.startswith((".", "~$"))
    ]
    print(f"Found {len(files)} files for {checklist['title']}")
    counts = {}
    for number, path in enumerate(files, start=1):
        label = f"[{number}/{len(files)}] {path.name}"
        if not force and database.is_processed(path.name, job_id):
            print(f"{label}: already done, skipped")
            counts["skipped"] = counts.get("skipped", 0) + 1
            continue
        try:
            status, score, seconds = process_resume(path, checklist)
        except Exception as error:
            print(f"  error: {error}")
            database.save_result(path.name, job_id, "pipeline_error")
            status, score, seconds = "pipeline_error", 0, 0.0
        counts[status] = counts.get(status, 0) + 1
        print(f"{label}: {status}, score {score}, {seconds:.0f}s")
    print("\nDone", counts)
    return job_name

def rescore(job_name):
    """Check the saved facts against the current checklist. No model is used."""
    database.init_db()
    checklist = load_checklist(job_name)
    job_id = checklist["job_id"]

    count = 0
    for row in database.list_candidates(job_id):
        if row["read_status"] != "ok":
            continue

        facts = {
            "skills": row["skills"],
            "unverified_skills": row["unverified_skills"],
            "total_years_experience": row["years_experience"],
            "location": row["location"],
            "education": row["education"],
            "job_titles": row["job_titles"],
        }
        evaluation = evaluate(facts, checklist)
        score = calculate_score(evaluation)
        database.save_result(
            row["source_file"], job_id, "ok", facts, evaluation, score,
            display_name=row["display_name"],
        )
        count += 1

    return count

if __name__=="__main__":
    job_id = run(settings.SAMPLE_DATA, "backend_python_developer")
    print("\nRanked List:")
    for row in database.list_candidates(job_id):
        print(
            f"  {row['source_file']:20} {row['label']:13}  "
            f"score {row['score']:3} {row['note']}"
        )