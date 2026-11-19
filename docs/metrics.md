# Success metrics

All results below come from a test set of 30 synthetic resumes
(sample_data/test_set, generated with seed 42). Baselines are assumptions
for a simulated client, not measurements.

| # | Metric | Target | Result | Status |
|---|--------|--------|--------|--------|
| 1 | Recruiter time per resume | under 1 min (baseline about 4 min assumed for real resumes; 15 s measured on short test resumes) | 8 s per resume on the dashboard (10 resumes, 80 s) | met on short synthetic resumes |
| 2 | Screening time per opening | about 3 h (baseline about 13 h, assumed) | estimate for 200 resumes: about 27 min of recruiter time plus about 2.1 h of machine time in the background | estimated from the stopwatch test, not measured end to end |
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
## Stopwatch test (recruiter time)
Done by one person (the builder) with a phone stopwatch.

| | Part A: no agent | Part B: dashboard |
|---|---|---|
| Resumes | resume_10 to resume_19, read raw in VS Code | 10 resumes chosen by the tester: 6 strong matches and 4 not (resume_08, 21, 28, 12, 27, 07, 09, 18, 10, 14) |
| Total time | 154 s | 80 s |
| Per resume | about 15 s | about 8 s |
| Correct decisions | 7 of 10 (missed 2 of 4 real strong matches, 1 false strong) | 10 of 10 |

Extrapolation to 200 resumes (an estimate, not a measurement):
- Recruiter time with the agent: about 27 min. Without the agent: about 51 min
  (short test resumes). Machine time: about 2.1 h, running in the background.
- The 4 min per resume and 13 h per opening baselines remain assumptions for
  real 1 to 2 page resumes. They were not measured.

Limits of this test:
- One tester, 10 resumes per part, short synthetic resumes (about 15 lines).
- The tester knows the rules and the system, so is faster than a real recruiter.
- Four resumes in Part B (10, 12, 14, 18) were already read in Part A.
- In Part B the rule was "approve strong_match, reject the rest", so decision
  accuracy mostly reflects the agent's own label accuracy.
- On the same kind of resumes the unassisted tester made more mistakes (70%)
  than the agent (100%), but the tester worked quickly. Real recruiters may
  be more careful on real resumes.