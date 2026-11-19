# Risks and approvals

## Principle
The agent ranks and flags. People decide. The agent never rejects a candidate
and never sends an email.

## Risks
| Risk | How it is reduced | What remains |
|------|-------------------|--------------|
| A good candidate is wrongly rejected | The agent never rejects. Only a recruiter clicks Reject. A candidate who fails a rule is labelled needs_review, not rejected. Every candidate stays visible on the dashboard | On the test set 0 of 13 strong matches were missed, but the test resumes are clean and synthetic |
| Bias by name, gender, age or marital status | Name, gender, age, marital status, email and phone are hidden before the model sees the text. None of them is used in any rule or score | Masking catches labelled lines and header lines with "|" separators in the first 8 lines. Free text such as "27-year-old male" in a sentence can leak. A header piece such as "Python | 10 years" could be removed by mistake. The recruiter does see the name on the dashboard |
| The model invents a skill | A skill counts only if its word appears in the resume text. Otherwise it is listed as unverified | The check proves the word is in the resume, not that the person has the skill. Ignoring skills a person is only learning depends on the prompt. The test trap ("Currently learning Docker") passed, but one trap is not a guarantee |
| The small local model misreads a resume | Reading accuracy on the test set was 96% (86 of 90 facts). A missing fact becomes unknown and the candidate is labelled needs_review, so the failure is safe. Reasons and a button to open the original resume are shown | A 3B model is less accurate than a large one. Real resumes are messier than the test resumes, so real accuracy will be lower |
| Recruiters trust the ranking too much | The dashboard shows a label, a one-line summary and a reason for every rule, not the score. The original resume opens with one click | In the stopwatch test the tester followed the labels every time. That is the intended speed-up, but it is also how over-trust starts. Recruiters need to know the agent can be wrong |
| A wrong checklist silently fails everyone | The checklist page refuses empty skill and location lists and can re-score saved resumes without the model. A missing rule shows as a clear reason on every candidate | During testing a stray extra required skill ("Java") and a comma inside a skill name ("Docker,") made every candidate fail. The page does not catch typos. A preview of the effect before saving is not built |
| Candidate data leaves the company | Only a local model (Ollama) is used. Nothing is sent to an outside service. The data folder is excluded from Git | Resumes stay on the disk with no automatic deletion and the dashboard has no login. A retention and deletion policy and access control are not built |
| A resume or email is silently dropped | Scans, unreadable files, unsupported attachments, model failures and emails with no attachment each get a status and appear on the dashboard as needs_review | Scanned resumes are not read (no OCR). They are flagged for a manual check |
| A wrong email goes to a candidate | The agent sends nothing. The recruiter sends every email | Email drafting is not built |
| A bug changes results without notice | A test set of 30 resumes with known answers and measuring scripts checks labels and reading accuracy. It already found a misspelled label that made every result wrong | The test set is small and synthetic. Run the measuring scripts again after every change to rules or prompts |

## Approvals kept by people
| Decision | Who decides |
|----------|-------------|
| Approve or reject a candidate | Recruiter |
| Change the must-haves and nice-to-haves | Recruiter |
| Re-score saved resumes after a checklist change | Recruiter |
| Check a flagged resume or email (scan, unreadable, no attachment) | Recruiter |
| Send any email to a candidate | Recruiter |
| Change a model, prompt or rule in the code | The developer, with the test set re-run |

## Before real use
- Test with real resumes and a recruiter's own judgement, not only synthetic data.
- Add a retention and deletion policy and access control for stored resumes.
- Improve the masking for free-text personal details.
- Add OCR for scanned resumes.
- Test the live mailbox connection (IMAP). Only a simulated inbox was tested.