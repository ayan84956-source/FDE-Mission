import csv
from agent import database
from config import settings

FOLDER = settings.ROOT / "sample_data" / "test_set"
JOB_ID = "backend_python_developer"

def count_nice(row):
    if not row["rule_rows"]:
        return 0
    items = row["rule_rows"]["nice_to_have"]
    return sum(1 for item in items if item["status"]== "met")

def main():
    with open(FOLDER / "answers.csv", encoding="utf-8") as file:
        answers = {row["file"]: row for row in csv.DictReader(file)}

    saved = {row["source_file"]: row for row in database.list_candidates(JOB_ID)}

    agree = 0
    nice_agree = 0
    missed = []
    false_strong = []

    for file_name, answer in answers.items():
        row = saved.get(file_name)
        if row is None:
            print(f"{file_name}: not found in the database")
            continue

        expected = answer["expected_label"]
        actual = row["label"]
        if expected == actual:
            agree += 1
        elif expected == "strong_match":
            missed.append(file_name)
        else:
            false_strong.append(file_name)

        found = count_nice(row)
        wanted = int(answer["expected_nice_count"])
        if found == wanted:
            nice_agree += 1
        else:
            print(f"{file_name}: nice-to-haves found {found}, expected {wanted}")

    total = len(answers)
    expected_strong = sum(1 for a in answers.values() if a["expected_label"] == "strong_match")

    print()
    print(f"Label agreement: {agree} of {total} ({agree / total * 100:.0f}%)")
    print(f"Missed candidates: {len(missed)} of {expected_strong} expected strong matches")
    for name in missed:
        print("   missed:", name)
    print(f"False strong matches: {len(false_strong)}")
    for name in false_strong:
        print("   false strong:", name)
    print(f"Nice-to-have count agreement: {nice_agree} of {total}")

if __name__ == "__main__":
    main() 