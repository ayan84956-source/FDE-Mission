# Resume Screening Agent

FDE Mission (Level 3): an AI agent that helps a 2-person HR team screen
resumes. The agent reads, ranks and explains. Recruiters decide.

The client is simulated. All client numbers are assumptions and all test
resumes are synthetic. No real candidate data is used.

## What it does
- Reads resumes (PDF, Word, text) from a shared inbox or from an upload page.
- Hides name, gender, age, marital status, email and phone before the model
  sees the text.
- Extracts skills, years of experience and location with a local model.
- Checks them against a recruiter-edited checklist of must-haves and
  nice-to-haves.
- Shows a ranked dashboard with a label, a one-line summary and a reason for
  every rule. Recruiters click Approve, Reject or Reset.
- Never rejects anyone and never sends an email.
- Flags scans, unreadable files, unsupported attachments and emails with no
  attachment for a manual check.

## How it works
One agent made of small stages. Only the extract stage uses a model.

convert -> anonymize -> extract (local model) -> check rules -> score -> save

Everything runs locally with Ollama. No resume data leaves the machine.

## Requirements
- Windows, Python 3.14, about 8 GB of RAM (no GPU needed)
- [Ollama](https://ollama.com) with the model `llama3.2:latest`

## Setup
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3.2
```
pytesseract and imap-tools are listed in requirements.txt for planned
features (OCR and a live mailbox). They are not used yet.

## Run
Ollama must be running. Run every command from the project folder with the
virtual environment active.

Start the dashboard (it also has the Checklist and Upload pages in the sidebar):
```
python -m streamlit run app/dashboard.py
```

Process the 30 synthetic test resumes (this deletes the old database first,
and takes about 20 minutes):
```
python -m scripts.run_test_set
```

Demo of the email channel with a simulated inbox:
```
python -m scripts.make_sample_inbox
python -m agent.fetch_email
python -c "from agent import pipeline; from config import settings; pipeline.run(settings.INBOX_DIR, 'backend_python_developer')"
```

Measure the results against the known answers:
```
python -m scripts.measure
python -m scripts.measure_reading
```

## Results (synthetic test set, 30 resumes)
| Metric | Result |
|--------|--------|
| Label agreement | 30 of 30 |
| Missed candidates | 0 of 13 strong matches |
| Reading accuracy (years, skills, location) | 86 of 90 facts (96%) |
| Machine time | about 38 s per resume |
| Recruiter time, stopwatch test | about 15 s per resume without the agent, about 8 s with it |

These are results on clean, short, synthetic resumes. Real resumes will give
lower accuracy. The method, the stopwatch test and its limits are in
docs/metrics.md.

## Project layout
- agent/: the pipeline stages, the database and the email fetcher
- app/: the Streamlit dashboard and its pages (checklist, upload)
- config/: settings and the job checklist (JSON)
- scripts/: test set generator, test runner, measuring scripts, sample inbox
- sample_data/: synthetic resumes, jobs and the simulated inbox
- docs/: client brief, process map, risks and approvals, metrics

## Not built yet
- OCR for scanned resumes (they are flagged for a manual check)
- Drafting emails for recruiters
- Matching an email to a job opening automatically (one opening in the demo)
- A live mailbox connection (only the simulated inbox was tested)
- Access control and a deletion policy for stored resumes

## Known limits
See docs/risks_and_approvals.md. In short: masking can miss personal details
written as free text, the 3B model is less accurate than a large one, and all
results come from synthetic data.