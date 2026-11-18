import mimetypes
from email.message import EmailMessage
from config import settings

OUT_DIR = settings.ROOT / "sample_data" / "inbox_sim"
TEST_DIR = settings.ROOT / "sample_data" / "test_set"
RESUME_DIR = settings.SAMPLE_DATA
HR_ADDRESS = "hr@example-company.com"

def attach(path):
    return path.name, path.read_bytes()

EMAILS = [
    (
        "aarav.patel@example.com",
        "Application for Backend Python Developer",
        "Hello, please find my resume attached.",
        [attach(TEST_DIR / "resume_00.txt")],
    ),
    (
        "diya.shah@example.com",
        "Applying: Python Developer, Gandhinagar",
        "Dear HR team, I am interested in this role. Resume attached.",
        [attach(TEST_DIR / "resume_01.txt")],
    ),
    (
        "rahul.mehta@example.com",
        "Backend Developer role - CV attached",
        "Hi, my CV is attached as a PDF.",
        [attach(RESUME_DIR / "rahul_mehta.pdf")],
    ),
    (
        "someone@example.com",
        "Is the Python job still open?",
        "Hello, is the Python developer position still open?",
        [],
    ),
    (
        "kabir.desai@example.com",
        "Application for Backend Python Developer",
        "Resume and my photo are attached.",
        [attach(TEST_DIR / "resume_02.txt"), ("photo.jpg", b"not a real image")],
    ),
]

def build_message(sender, subject, body, attachments):
    message = EmailMessage()
    message["From"] = sender
    message["To"] = HR_ADDRESS
    message["Subject"] = subject
    message.set_content(body)
    for name, data in attachments:
        kind = mimetypes.guess_type(name)[0] or "application/octet-stream"
        maintype, subtype = kind.split("/")
        message.add_attachment(data, maintype=maintype, subtype=subtype, filename=name)
    return message

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for number, (sender, subject, body, attachments) in enumerate(EMAILS, start=1):
        message = build_message(sender, subject, body, attachments)
        path = OUT_DIR / f"email_{number:03d}.eml"
        path.write_bytes(message.as_bytes())
        print(f"{path.name}: {subject} ({len(attachments)} attachments)")
    print(f"Wrote {len(EMAILS)} emails to {OUT_DIR}")

if __name__ == "__main__":
    main()