import json
import re
from email import policy
from email.parser import BytesParser
from agent import database
from config import settings

INDEX_FILE = settings.INBOX_DIR / ".emails.json"
JOB_ID = "backend_python_developer"

def safe_name(name):
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)

def read_email(path):
    with open(path, "rb") as file:
        return BytesParser(policy=policy.default).parse(file)

def fetch_folder(folder):
    settings.INBOX_DIR.mkdir(parents=True, exist_ok=True)

    index = {}
    if INDEX_FILE.exists():
        index = json.loads(INDEX_FILE.read_text(encoding="utf-8"))

    summary = []
    for eml in sorted(folder.glob("*.eml")):
        message = read_email(eml)
        sender = str(message["From"])
        subject = str(message["Subject"])

        saved = []
        for number, part in enumerate(message.iter_attachments(), start=1):
            data = part.get_payload(decode=True)
            if data is None:
                continue
            original = part.get_filename() or f"attachment_{number}"
            file_name = f"{eml.stem}_{number}_{safe_name(original)}"
            (settings.INBOX_DIR / file_name).write_bytes(data)
            index[file_name] = {"sender": sender, "subject": subject}
            saved.append(file_name)

        if not saved:
            database.init_db()
            database.save_result(
                f"{eml.name} (no attachment)",
                JOB_ID,
                "no_attachment",
                display_name=sender,
            )

        summary.append({"email": eml.name, "sender": sender,
                        "subject": subject, "saved": saved})

    INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return summary

if __name__ == "__main__":
    folder = settings.ROOT / "sample_data" / "inbox_sim"
    for item in fetch_folder(folder):
        if item["saved"]:
            print(f"{item['email']}: {item['subject']} -> {len(item['saved'])} saved")
        else:
            print(f"{item['email']}: {item['subject']} -> NO ATTACHMENT, needs a human")