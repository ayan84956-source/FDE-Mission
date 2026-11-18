import csv
from agent import database
from config import settings

FOLDER = settings.ROOT / "sample_data" / "test_set"
JOB_ID = "backend_python_developer"

def main():
    with open(FOLDER / "answers.csv", encoding="utf-8") as file:
        answers = {row["file"]: row for row in csv.DictReader(file)}

    saved = {row["source_file"]: row for row in database.list_candidates(JOB_ID)}

    correct = {"years": 0, "skills": 0, "location": 0}
    checked = 0

    for file_name, answer in answers.items():
        row = saved.get(file_name)
        if row is None:
            print(f"{file_name}: not found in the database")
            continue
        checked += 1

        want_years = float(answer["years"])
        want_skills = {s.lower() for s in answer["skills"].split(";")}
        want_location = answer["location"].strip().lower()

        got_years = row["years_experience"]
        got_skills = {s.lower() for s in row["skills"]}
        got_location = (row["location"] or "").strip().lower()

        if got_years == want_years:
            correct["years"] += 1
        else:
            print(f"{file_name}: years read {got_years}, true {want_years:g}")

        if got_skills == want_skills:
            correct["skills"] += 1
        else:
            missing = sorted(want_skills - got_skills)
            extra = sorted(got_skills - want_skills)
            print(f"{file_name}: skills missing {missing}, extra {extra}")

        if got_location == want_location:
            correct["location"] += 1
        else:
            print(f"{file_name}: location read '{got_location}', true '{want_location}'")

    print()
    for field, count in correct.items():
        print(f"{field:9} {count} of {checked} correct")
    total_right = sum(correct.values())
    total = checked * 3
    print(f"Reading accuracy: {total_right} of {total} ({total_right / total * 100:.0f}%)")

if __name__ == "__main__":
    main()