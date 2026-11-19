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

## 4. Design decisions
| Decision | Why | Cost or trade-off |
|----------|-----|-------------------|
| One agent made of small stages, with the model in only one stage | Rules, scoring and ranking are plain code, so they are fast, free and easy to test. Re-scoring after a checklist change takes about 1 second without the model | A skill the model never listed cannot be found by re-scoring. A forced re-run is needed |
| The agent never rejects anyone | Wrongly rejecting a good candidate is the costliest mistake, and a person must be accountable for hiring decisions | Recruiters still review every flagged candidate |
| Name, gender, age and marital status are hidden from the model | Protects against bias in the model's reading. No rule or score uses them | Masking catches labelled lines and "|" header lines only. Free text like "27-year-old male" can leak. The recruiter does see the name |
| Every skill must appear in the resume text | Stops the model from inventing skills. Unmatched skills go to unverified skills | Proves the word is there, not that the person has the skill |
| A local model only (llama3.2, 3B) | Resume data never leaves the machine | Slower (about 38 s per resume) and less accurate than a large model. I lowered the reading accuracy target from 95% to 90% for this reason |
| The dashboard shows a label and a summary, not the score | The score only orders the list, which reduces over-trust in a number | Recruiters cannot see how close a candidate was to the line |
| The checklist is a JSON file edited on a page | Recruiters can change the rules without a developer | The page does not catch typos or preview the effect before saving |
| Built the test set before email fetching | It produces the numbers for this report, and my internship ends on Dec 28 | The email channel is shown with a simulated inbox only |
| OCR, email drafting and automatic job matching postponed | Time was limited. A scan is flagged for a manual check, and there is only one opening | Listed as not built in the README and the client brief |

## 5. Results
Measured on 30 synthetic resumes with known answers, except where marked.

| # | Metric | Target | Result | How measured |
|---|--------|--------|--------|--------------|
| 1 | Recruiter time per resume | under 1 minute | about 8 s with the agent, about 15 s without, on short test resumes | stopwatch test, 10 resumes per part |
| 2 | Screening time per opening | about 3 hours | estimate for 200 resumes: about 27 min of recruiter time plus about 2.1 h of machine time in the background | extrapolated from the stopwatch test and 38 s per resume |
| 3 | Shortlist agreement | at least 80% | 30 of 30 | agent label against the expected label |
| 4 | Missed candidates | under 5% | 0 of 13 strong matches | strong matches not labelled strong_match |
| 5 | Reading accuracy | 90% (working target) | 86 of 90 facts (96%) | years, skills, location against known facts |

Details:
- Reading accuracy by field: skills 30 of 30, location 30 of 30, years 26 of 30.
  The 4 wrong years are freshers (true experience 0) where the model returned
  "not found". The rule engine treats that as unknown and labels the candidate
  needs_review, so the failure is safe: a human looks, nobody is rejected.
- Nice-to-have counts matched the expected count in 30 of 30 resumes. A trap
  resume line ("Currently learning Docker") was correctly not counted.
- Machine time: 19.1 minutes for 30 resumes.
- Stopwatch test: Part A (no agent, 10 raw resumes) took 154 s with 7 of 10
  correct decisions, missing 2 of 4 real strong matches. Part B (dashboard, 10
  resumes) took 80 s with 10 of 10 correct. Method and limits are in
  docs/metrics.md.
- "Shortlist agreement" here means the agent's label against the expected
  label from my test generator. It is not agreement with a real recruiter.
- The baselines (4 minutes per resume, 13 hours per opening) are assumptions
  for real 1 to 2 page resumes. On the short test resumes I measured 15 s per
  resume instead, so the time saving I can show is smaller than the assumed one.

## 6. Problems found while testing
1. A one-letter typo hid every result. My first measurement said 0 of 30
   labels agreed, and the results were exactly inverted. A real model error is
   scattered, so a perfect 0 pointed to a bug in the code. I looked at one
   resume in three places (the answer file, the resume, the saved result) and
   found the label "need_review" in one line of the rules, which should have been
   "needs_review". Changing one word fixed it.
2. A bad checklist made every candidate fail. A saved summary said "meets 4 of 5
   must-haves" for a candidate who met everything, but the real checklist had a
   stray required skill ("Java") and a skill written as "Docker," with a comma. Both were
   left over from earlier tests. I restored the file and re-scored the saved
   facts in about a second, without repeating the 19-minute model run.
3. A function went missing. The pipeline stopped with an AttributeError because
   the "already processed" check had disappeared from the database file. I listed
   the names the file offered, saw it was absent, and put it back.
4. Freshers read as "years not found" (4 of 30). I did not fix it. A prompt
   change can alter other results and means another full run, and the failure is
   safe. It is documented as a known limit.
5. The test answers did not store the true facts. To measure reading accuracy I
   added columns to the answer file without changing the resumes (same random seed).
   Git showed only two files changed, which confirmed it.
6. A stopwatch run whose saved decisions did not match what I had written down
   was discarded and redone. I trusted the saved data over my notes.

What these show: a test set with known answers catches bugs a 3-resume check
never would. A result that is perfectly wrong is a code bug. And each number
should live in one place, so documents cannot drift apart.

## 7. Limits and risks
The full table is in docs/risks_and_approvals.md. The ones that matter most:
- All results come from 30 clean, short, synthetic resumes. They are not a
  claim about real accuracy. Real resumes are messier and results will be lower.
- The generator and the checker share the same rules, so agreement is partly
  built in. A test with a recruiter's own judgement on real resumes is still
  needed.
- The recruiter-time numbers come from one tester (the builder), 10 resumes per
  part, with some resumes seen twice. The assumed baselines (4 minutes per
  resume, 13 hours per opening) were not measured.
- Masking can miss personal details written as free text. The recruiter sees the
  name on the dashboard.
- A skill check proves the word is in the resume, not that the person has the
  skill.
- The 3B model sometimes returns nothing for a fresher's years. The result is
  flagged for a human, not rejected.
- The live mailbox connection, OCR and email drafting are not built or not tested.
- No login and no deletion policy for stored resumes.

## 8. Next steps (in priority order)
1. Test with real resumes and a recruiter's own decisions, and measure again.
2. Add a retention and deletion policy and access control.
3. Improve masking for free-text personal details.
4. Add skill aliases (for example Postgres and PostgreSQL, AWS and Amazon Web
   Services). The test set does not use them, so they are untested so far.
5. Fix the fresher years case in the prompt, then re-run the test set to
   check nothing else changed.
6. OCR for scanned resumes (a vision model is already installed for this).
7. A live mailbox connection and automatic matching of an email to the right
   opening.
8. Drafting emails for the recruiter to review and send.

## 9. Demo script (about 8 minutes)
Before the demo:
- Ollama is running and the laptop is plugged in.
- The database still holds the 30 test results and the inbox results.
- The checklist file says 2.0 years, required skills Python and SQL.

1. The problem (1 min). Show docs/client_brief.md. Say: 2 recruiters, 200 resumes
   per opening, all read by hand. This client is simulated.
2. The dashboard (2 min). Run `python -m streamlit run app/dashboard.py`.
   Open a strong match: summary, reasons with icons, the original resume
   button. Open a needs_review one and show which rule failed. Point out
   that there is no score, only a label and reasons.
3. Privacy (1 min). Run `python -m agent.anonymize` and show the name, email,
   phone, gender, age and date of birth replaced or removed. Say: the model only
   sees the masked text, and it runs locally.
4. The recruiter in control (1 min). On the Checklist page change the minimum
   years to 5, click Save checklist, then Re-score saved resumes. Go back to
   the dashboard: most candidates moved to needs_review, in about a second,
   without the model. Then set it back to 2, save and re-score again.
5. The email channel (1 min). Show the five simulated emails. Run
   `python -m agent.fetch_email`, then the pipeline command on the inbox folder
   (the finished files are skipped, so it takes seconds). On the dashboard
   show: a resume with its sender and subject, the photo flagged as
   unsupported, and the email with no attachment flagged for a human.
6. Upload (1 min, optional). On the Upload page add sample_data/test_set/
   resume_05.txt. It takes about 40 seconds. Explain the pipeline stages
   while it runs.
7. Numbers (1 min). Run `python -m scripts.measure` and
   `python -m scripts.measure_reading`. Show 30 of 30, 0 of 13 missed, 86 of 90.
   Then say what they are and are not: synthetic data, partly built in.
8. Close. The agent never rejects and never sends an email. Show the
   "Not built yet" list in the README.

After the demo: check that config/checklists/backend_python_developer.json
still says 2.0 years.

Questions to expect:
- "Is 100% real?" It is correct on clean synthetic resumes whose rules match
  my own. It shows the pipeline works, not that real resumes will score 100%.
- "What if the model is wrong?" A missing fact becomes unknown and the
  candidate is flagged for a human. Nobody is rejected by the agent.
- "Why not a bigger model?" Privacy and an 8 GB laptop. The price is speed and
  some accuracy, and I lowered the reading target from 95% to 90% for it.
- "Could this be biased?" Name, gender, age and marital status are hidden from
  the model and no rule uses them. Masking is not perfect on free text, and
  the recruiter still sees the name.

## 10. Conclusion
The agent turns a slow reading job into a short review job: it reads, ranks and
explains, and the recruiters decide. On synthetic data it matched every expected
label and cut review time in a small stopwatch test. The next real test is
real resumes judged by real recruiters.