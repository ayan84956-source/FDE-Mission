import csv
import random
from config import settings

random.seed(42)

OUT_DIR = settings.ROOT / "sample_data" / "test_set"

FIRST = ["Aarav", "Diya", "Kabir", "Meera", "Vihaan", "Ananya", "Arjun", "Isha", "Rohan", "Sneha"]
LAST = ["Patel", "Shah", "Desai", "Joshi", "Trivedi", "Mehta", "Parikh", "Bhatt", "Modi", "Gandhi"]
IN_STATE = ["Ahmedabad, Gujarat", "Gandhinagar, Gujarat", "Surat, Gujarat"]
OUT_STATE = ["Mumbai, Maharashtra", "Pune, Maharashtra", "Bengaluru, Karnataka"]
NICE = ["Docker", "AWS", "FastAPI", "Kubernetes"]
YEARS = [0, 1, 2, 2, 3, 3, 4, 6, 8]

def make_resume(number):
    name = f"{FIRST[number % 10]} {LAST[(number + number // 10) % 10]}"
    years = random.choice(YEARS)
    has_python = random.random() < 0.85
    has_sql = random.random() < 0.85
    in_state = random.random() < 0.7
    nice = random.sample(NICE, random.randint(0, 4))

    language = "Python" if has_python else "Java"
    database = "SQL" if has_sql else "MongoDB"
    skills = [language, "Git", database] + nice
    location = random.choice(IN_STATE if in_state else OUT_STATE)

    style = number % 3
    lines = [name, f"Email: {name.lower().replace(' ', '.')}@example.com | Phone: 98XXXXXX{number:02d}"]
    if style == 1:
        lines += ["Gender: Female", f"Age: {25 + number % 10}", "Date of Birth: 12/03/1998"]
    if style == 2:
        lines += [f"Male | {25 + number % 10} years | Married"]
    lines += [f"Location: {location}", "", "SUMMARY", "Backend developer with experience building APIs.", "", "EXPERIENCE"]

    if years == 0:
        lines += ["Fresher, no work experience yet", f"- Built a college project in {language}."]
    else:
        lines += [
            f"Software Engineer, TechCorp ({2026 - years} - Present) - {years} years",
            f"- Built REST APIs in {language}.",
            f"- Worked with {database} databases.",
        ]
    if "Docker" not in nice and random.random() < 0.3:
        lines += ["- Currently learning Docker."]

    lines += ["", "EDUCATION", f"B.Tech in Computer Engineering, {2025 - years}", "", "SKILLS", ", ".join(skills)]

    strong = years >= 2 and has_python and has_sql and in_state
    return name, "\n".join(lines), ("strong_match" if strong else "needs_review"), len(nice), style

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for number in range(30):
        name, text, expected, nice_count, style = make_resume(number)
        file_name = f"resume_{number:02d}.txt"
        (OUT_DIR / file_name).write_text(text, encoding="utf-8")
        rows.append([file_name, name, expected, nice_count, style])

    with open(OUT_DIR / "answers.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["file", "name", "expected_label", "expected_nice_count", "header_style"])
        writer.writerows(rows)

    strong = sum(1 for row in rows if row[2] == "strong_match")
    print(f"Wrote {len(rows)} resumes to {OUT_DIR}")
    print(f"Expected strong matches: {strong}, needs review: {len(rows) - strong}")

if __name__ == "__main__":
    main()