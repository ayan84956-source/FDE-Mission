import re
from pathlib import Path
import fitz
import docx

MIN_TEXT_CHARS = 50

def read_txt(path):
    return path.read_text(encoding="utf-8", errors="ignore")

def read_pdf(path):
    pages = []
    with fitz.open(path) as pdf:
        for page in pdf:
            pages.append(page.get_text())
    return "\n".join(pages)

def read_docx(path):
    document = docx.Document(path)
    lines = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            lines.append("|".join(cell.text for cell in table.cells))
    return "\n".join(lines)

READERS = {".txt": read_txt, ".pdf": read_pdf, ".docx": read_docx}

def clean(text):
    text = text.replace("\r","")
    text = re.sub(r"[\t]+", " ", text)
    text = re.sub(r"\n{3,}","\n\n", text)
    return text.strip()

def convert(path):
    path = Path(path)
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        return "", "unsupported"
    try:
        text = clean(reader(path))
    except Exception:
        return "", "unreadable"
    if len(text) < MIN_TEXT_CHARS:
        return text , "needs_ocr"
    return text, "ok"

if __name__=="__main__":
    from config import settings
    for files in sorted(settings.SAMPLE_DATA.iterdir()):
        text, status = convert(files)
        print(f"{files.name:25} {status:12} {len(text)} characters")