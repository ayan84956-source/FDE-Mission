# Client brief: resume screening

Note: the client is simulated. Every number about the client below is an
assumption for this project, not a fact from a real company.

## Client
A mid-size IT services company with a 2-person HR recruitment team. The team
makes 15 to 20 hires a month.

## Problem
Every job opening gets 100 to 300 resumes, sent by email to a shared inbox
(hr@). Recruiters open and read every resume by hand to decide who goes on a
shortlist. Assumed effort: about 4 minutes per resume, so about 13 hours of
reading for one opening with 200 resumes. Good candidates can be missed when
reading is rushed, and the recruiters' time goes to reading, not to talking
with candidates.

## Goal
Recruiters spend their time on the people who fit the role, not on reading
every resume. The agent reads the resumes, ranks the candidates and explains
each ranking in plain language. The recruiters make every decision.

## Users
Two recruiters. They are business users, not developers. They need to:
- edit the job checklist (must-haves and nice-to-haves) on a simple page,
- review a ranked list with reasons,
- approve, reject or reset each candidate with one click,
- send every email to candidates themselves.

## In scope (this version)
- Resumes from the shared inbox, as PDF, Word or text files.
- One job opening at a time, with a checklist of must-haves and nice-to-haves.
- Ranking with plain-language reasons for every rule.
- Flagging for a human check: scanned resumes, unreadable files, unsupported
  attachments, and emails with no attachment.
- Running fully on the company's own computer.

## Out of scope (this version)
- Automatic rejection. The agent never rejects anyone.
- Sending emails. The agent does not send anything. Drafting candidate emails
  for the recruiter to send is part of the design but is not built yet.
- Reading scanned resumes (OCR). They are flagged for a manual check.
- Matching an email to the right opening automatically. The demo has one
  opening.
- A live connection to a real mailbox. The demo uses a simulated inbox of
  saved .eml files, so the live connection is untested.
- Using name, photo, gender or age in any decision. These are never used.

## Success metrics
See metrics.md. The five metrics are recruiter time per resume, screening
time per opening, shortlist agreement, missed candidates and reading accuracy.

## Assumptions
- Volumes, minutes per resume and the team size above are invented for the
  simulation.
- Test data is synthetic. No real candidate data was used.