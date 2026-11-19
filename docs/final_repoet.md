# Final report: Resume Screening Agent
FDE Mission (Level 3)

## 1. Summary
I picked a manual process from a simulated client, resume screening for a
2-person HR team, and automated the reading and ranking with an AI agent built
for business users. The client is simulated, so every client number is an
assumption, and all test data is synthetic.

What I built: one agent made of small stages (convert, anonymize, extract,
check rules, score, save). Only the extract stage uses a model, a local one
(llama3.2 through Ollama), so no resume data leaves the machine. Recruiters use
a Streamlit dashboard with a ranked list, plain-language reasons and Approve,
Reject and Reset buttons. They edit the job checklist on a page and can upload
a resume or process a simulated shared inbox.

Key results on 30 synthetic resumes:
- Label agreement with the known answers: 30 of 30.
- Missed candidates: 0 of 13 expected strong matches.
- Reading accuracy (years, skills, location): 86 of 90 facts (96%).
- Machine time: about 38 seconds per resume (19.1 minutes for 30).
- Recruiter time in a small stopwatch test: about 15 seconds per resume without
  the agent and about 8 seconds with it, on short test resumes.

The agent never rejects a candidate and never sends an email. Those stay with
the recruiters. The results come from clean, short, synthetic resumes, so real
accuracy will be lower. See sections on limits and docs/risks_and_approvals.md.

## 2. The client and the problem
A mid-size IT services company with a 2-person HR recruitment team, hiring 15 to
20 people a month. Each opening gets 100 to 300 resumes in a shared inbox, and
recruiters read each one by hand. I assumed about 4 minutes per resume, about
13 hours for an opening with 200 resumes. These are assumptions, not measurements
(docs/client_brief.md).

The risk I wanted to design around: in a rushed manual read, good candidates get
missed. In my own stopwatch test, reading 10 short resumes quickly gave 7 of 10
correct decisions, with 2 of the 4 real strong matches missed.

## 3. What I built
The pipeline, one resume at a time:
1. Convert: PDF, Word or text to plain text. A scan with no text is flagged.
2. Anonymize: hide name, gender, age, marital status, email and phone, so the
   model never sees them and no rule can use them.
3. Extract: the local model reads skills, years of experience and location.
   A skill counts only if its word appears in the resume text.
4. Check rules: compare the facts with the recruiter's checklist (must-haves
   and nice-to-haves). Each rule is met, not met or unknown.
5. Score and rank: the score is only used to order the list.
6. Save: results go to a local database. A recruiter's decision is kept if the
   resume is processed again.

What the recruiters use:
- Dashboard: label, one-line summary, a reason for every rule, a button to open
  the original resume, and the sender and subject for emailed resumes.
- Checklist page: edit the must-haves and nice-to-haves, then re-score the
  saved resumes without running the model again.
- Upload page: add one resume and see the result.

The email channel: a fetcher saves attachments under unique names and records
the sender and subject. Emails with no attachment, unreadable files and
unsupported attachments are flagged for a human, never dropped. Only a
simulated inbox of saved .eml files was tested, not a live mailbox.

The process before and after the agent, step by step, is in docs/process_map.md.