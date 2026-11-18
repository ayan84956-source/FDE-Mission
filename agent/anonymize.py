import re
    
PRIVATE_LINE = re.compile(
    r"^\s*(?:gender|sex|age|date of birth|dob|birth date|"
    r"marital status|nationality|religion|photo)\s*[:\-]",
    re.IGNORECASE,
)

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

PHONE = re.compile(
    r"\b(?:phone|mobile|mob|tel|contact)\b[ \t]*[:\-]?[ \t]*[+\dXx][\dXx \t\-()]{6,}",
    re.IGNORECASE,
)

NAME_LINE = re.compile(r"^[A-Za-z.'-]+(?: [A-Za-z.'-]+){1,3}$")
NOT_NAMES = {"resume", "curriculum vitae", "cv"}

HEADER_LINES = 8

PRIVATE_PART = re.compile(
    r"(?:male|female|man|woman|married|single|unmarried|divorced|"
    r"\d{2}\s*(?:years|yrs)(?:\s*old)?)",
    re.IGNORECASE,
)


def clean_header(lines):
    """Remove private pieces from header lines like 'Male | 27 years | Married'."""
    result = []
    for number, line in enumerate(lines):
        if number < HEADER_LINES and "|" in line:
            parts = [part.strip() for part in line.split("|")]
            parts = [part for part in parts if not PRIVATE_PART.fullmatch(part)]
            if not parts:
                continue
            line = " | ".join(parts)
        result.append(line)
    return result

def find_name(text):
    """The name is the first non-empty line, if it looks like a name."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if NAME_LINE.match(line) and line.lower() not in NOT_NAMES:
            return line
        return None
    return None

def anonymize(text):
    """Hide personal details. Returns (clean_text, name)."""
    name = find_name(text)

    lines = [line for line in text.splitlines() if not PRIVATE_LINE.match(line)]
    lines = clean_header(lines)
    clean = "\n".join(lines)

    if name:
        clean = re.sub(re.escape(name), "[CANDIDATE]", clean, flags=re.IGNORECASE)
    clean = EMAIL.sub("[EMAIL]", clean)
    clean = PHONE.sub("[PHONE]", clean)
    return clean, name

if __name__ == "__main__":
    sample = """Priya Shah
Email: priya.shah@example.com | Phone: +91 98765 43210
Gender: Female
Age: 29
Date of Birth: 12/03/1997
Location: Ahmedabad, Gujarat

Agile methodology and Python (2021 - 2023). Priya Shah led the team.
"""
    clean, name = anonymize(sample)
    print("Name found:", name)
    print("---")
    print(clean)