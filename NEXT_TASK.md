# Next Task

Use the persisted EXP-8ee0e64d66 result as the baseline for the next bounded research question; do not treat its NEED_MORE_DATA decision as strategy approval.

Hypothesis to test: CE and PE setup outcomes may differ by ITM rank and entry time, but the difference should be checked across a development period and an unseen validation period before proposing any strategy change.

The repository previously selected 2026-09-07 through 2026-09-11, but the next run must re-check data quality rather than assume that week is suitable. Groq credentials are configured through `llmkey.md` for the bounded run.

A current-week read-only snapshot is also available under `data/raw/live-2026-09-21_2026-09-23/` with a deterministic preflight report. It must not be treated as a completed-week validation result.

Required steps:

1. Select and document a completed week with sufficient underlying and option coverage.
2. Run the unchanged `baseline-v1` strategies through `ResearchAgent`.
3. Report setup count, valid/skipped/ambiguous outcomes, target and SL results, points, MFE, MAE, holding time, drawdown, streaks, CE/PE, ITM rank, and time-of-day distributions.
4. Split the data chronologically and explicitly report `INSUFFICIENT OUT-OF-SAMPLE DATA` if the validation sample is too small.
5. Save a new report and update `PROJECT_STATE.md` and `EXPERIMENT_LOG.md`.