from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
INBOX_DIR = DATA_DIR / "inbox"
TEXT_DIR = DATA_DIR / "text"
DB_PATH = DATA_DIR / "resume_agent.db"
CHECKLIST_DIR = ROOT / "config" / "checklists"
SAMPLE_DATA = ROOT / "sample_data" / "resumes"
MODEL_NAME = "llama3.2:latest"
KEEP_ALIVE = "30m"
TEMPERATURE = 0
MAX_RETRIVE = 1