# Success metrics

All results below come from a test set of 30 synthetic resumes
(sample_data/test_set, generated with seed 42). Baselines are assumptions
for a simulated client, not measurements.

| # | Metric | Target | Result | Status |
|---|--------|--------|--------|--------|
| 1 | Recruiter time per resume | under 1 min (baseline about 4 min, assumed) | not measured yet | pending demo |
| 2 | Screening time per opening | about 3 h (baseline about 13 h, assumed) | machine time about 38 s per resume, recruiter time not measured yet | pending demo |
| 3 | Shortlist agreement | at least 80% | 30 of 30 (100%) | met on synthetic data |
| 4 | Missed candidates | under 5% | 0 of 13 (0%) | met on synthetic data |
| 5 | Reading accuracy | 90% (working target) | 86 of 90 facts (96%) | met on synthetic data |

## How each result was measured
- Metrics 3 and 4: scripts/measure.py compares the agent's label with the
  expected label in answers.csv. A missed candidate is a resume expected to be
  strong_match that was not labelled strong_match.
- Metric 5: scripts/measure_reading.py compares years, skills and location
  with the true facts in answers.csv (30 resumes x 3 facts = 90 facts).
- Machine time: 30 resumes took 19.1 minutes (llama3.2, CPU only, 8 GB RAM).

## Known limits
- The test resumes are clean and regular. Real resumes will be messier,
  so real accuracy will be lower and must be checked with real samples.
- Four resumes of freshers (true experience 0 years) were read as "years
  not found". The agent flags them for a human check, it never rejects.
- Masking catches labelled lines and header lines with "|" separators.
  Free-form text such as "27-year-old male" in a sentence can leak.
- Skills the model never listed cannot be found by re-scoring.