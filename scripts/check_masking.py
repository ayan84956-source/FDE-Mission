import csv
import re

from agent.anonymize import anonymize
from config import settings

FOLDER = settings.ROOT / "sample_data" / "test_set"

LEAK_PATTERNS = [
    r"\bgender\b", r"\bfemale\b", r"\bmale\b", r"\bmarried\b",
    r"date of birth", r"\bage\b", r"@example\.com", r"98XXXXXX",
]


def main():
    with open(FOLDER / "answers.csv", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    failed = 0
    for row in rows:
        text = (FOLDER / row["file"]).read_text(encoding="utf-8")
        clean, name = anonymize(text)
        lowered = clean.lower()

        problems = [p for p in LEAK_PATTERNS if re.search(p, lowered, re.IGNORECASE)]
        if row["name"].lower() in lowered:
            problems.append("name still in text")
        if name != row["name"]:
            problems.append(f"name found as {name}")

        if problems:
            failed += 1
            print(row["file"], "->", ", ".join(problems))

    print(f"Checked {len(rows)} resumes, {failed} with problems")


if __name__ == "__main__":
    main()