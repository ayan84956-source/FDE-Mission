# Process map: resume screening

## Before the agent (assumed process of the simulated client)
1. Resumes arrive by email in the shared inbox (hr@).
2. A recruiter opens each email and downloads the attachment.
3. The recruiter reads the resume (assumed about 4 minutes each).
4. The recruiter compares it with the job description and their own checklist.
5. The recruiter notes the decision for each candidate.
6. The recruiter emails the candidates who are shortlisted or declined.

## After the agent
| # | Step | Who | What happens | Where in the project |
|---|------|-----|--------------|----------------------|
| 1 | Fetch | Agent | Saves each attachment under a unique name, records sender and subject, flags emails with no attachment | agent/fetch_email.py |
| 2 | Convert | Agent (plain code) | Turns PDF, Word or text into text. A scan is flagged needs_ocr | agent/convert.py |
| 3 | Anonymize | Agent (plain code) | Hides name, gender, age, marital status, email and phone before the model sees the text | agent/anonymize.py |
| 4 | Extract | Agent (local model) | Reads skills, years of experience and location. A skill must appear in the resume text, otherwise it goes to unverified skills | agent/extract.py |
| 5 | Check rules | Agent (plain code) | Compares the facts with the checklist. Each rule is met, not met or unknown | agent/check_rules.py |
| 6 | Score and rank | Agent (plain code) | The score is used only to order the list. Strong matches come first | agent/score.py |
| 7 | Save | Agent (plain code) | Stores the result in a local database. A recruiter's decision is kept if the resume is processed again | agent/database.py |
| 8 | Review | Recruiter | Reads the label, summary and reasons on the dashboard, opens the original resume if needed, clicks Approve, Reject or Reset | app/dashboard.py |
| 9 | Edit the checklist | Recruiter | Changes the must-haves and nice-to-haves on a page, then re-scores the saved resumes without the model | app/pages/checklist.py |
| 10 | Contact candidates | Recruiter | Sends every email personally. Drafting emails is not built yet | not built |

Resumes can also be added one at a time on the upload page (app/pages/upload.py).
It runs the same steps 2 to 7.

## Where a human decides
- Only a recruiter can approve or reject a candidate.
- Only a recruiter can change the checklist.
- Only a recruiter sends emails.
- The agent ranks and flags. It never rejects and never sends anything.

## What happens to problem cases
| Case | What the agent does |
|------|---------------------|
| Scanned resume (no text) | Status needs_ocr, flagged for a manual check |
| File cannot be opened | Status unreadable, flagged |
| Attachment is not a resume file (for example a photo) | Status unsupported, flagged |
| The model returns unusable output | Status model_failed, flagged |
| Email has no attachment | Saved as a needs_review row with the sender's address |
| A must-have fact is missing from the resume | The rule is marked unknown and the candidate is labelled needs_review |