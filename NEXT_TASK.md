# Next Task

Configure `RESEARCH_LLM_PROVIDER` and `RESEARCH_LLM_API_KEY` in the environment, then run one bounded experiment on the latest completed historical week.

Hypothesis to test: CE and PE setup outcomes may differ by ITM rank and entry time, but the difference should be checked across a development period and an unseen validation period before proposing any strategy change.

The repository selected 2026-09-07 through 2026-09-11 as the latest complete Monday-Friday week. The deterministic baseline path is ready; the AI demo cannot begin until a real provider is configured.

Required steps:

1. Select and document a completed week with sufficient underlying and option coverage.
2. Run the unchanged `baseline-v1` strategies through `ResearchAgent`.
3. Report setup count, valid/skipped/ambiguous outcomes, target and SL results, points, MFE, MAE, holding time, drawdown, streaks, CE/PE, ITM rank, and time-of-day distributions.
4. Split the data chronologically and explicitly report `INSUFFICIENT OUT-OF-SAMPLE DATA` if the validation sample is too small.
5. Save a new report and update `PROJECT_STATE.md` and `EXPERIMENT_LOG.md`.