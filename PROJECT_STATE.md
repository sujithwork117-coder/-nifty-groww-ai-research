# Project State

Updated: 2026-09-23

## Status

- Research-only NIFTY system; real order execution is disabled.
- `EXECUTION_ALLOWED=false` and `PAPER_ONLY=true` are enforced by `app.safety.ExecutionLock` and `app.config`.
- Baseline strategies remain unchanged: Level-to-Level and Ekalayava, 5-minute candles, Asia/Kolkata, NIFTY CE/PE ITM ranks 2 and 3.
- The persistent agent infrastructure is implemented in `app/research_state.py` and `app/research_agent.py`.

## Latest Milestone

- Latest report: `data/reports/final_research_report_3.json`.
- Latest research period: 2026-09-23 intraday, completed candles through 13:35 IST.
- Latest result: 4 eligible contracts, 2 Level-to-Level setups, 0 confirmed Ekalayava setups.
- Latest commit before this infrastructure task: `bbddabc`.

## Known Limitations

- The live snapshot is an intraday observation, not a completed trading-day result.
- Ekalayava has no numeric stop-loss rule in the source definition and must remain marked undefined.
- Historical option coverage is uneven across contracts and periods; coverage must be checked before comparisons.
- Out-of-sample validation is insufficient for strategy evolution until separate development and validation periods are assembled.

## Next Objective

Run a bounded historical experiment on a completed week, compare both baseline strategies by CE/PE, ITM rank, and time of day, and document a hypothesis before any experimental rule change.