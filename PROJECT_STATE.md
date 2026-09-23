# Project State

Updated: 2026-09-23

## Status

- Research-only NIFTY system; real order execution is disabled.
- `EXECUTION_ALLOWED=false` and `PAPER_ONLY=true` are enforced by `app.safety.ExecutionLock` and `app.config`.
- Baseline strategies remain unchanged: Level-to-Level and Ekalayava, 5-minute candles, Asia/Kolkata, NIFTY CE/PE ITM ranks 2 and 3.
- The persistent agent infrastructure is implemented in `app/research_state.py` and `app/research_agent.py`.
- The real LLM loop and deterministic weekly engine are implemented in `app/llm.py` and `app/weekly_experiment.py`.

## Latest Milestone

- Latest report: `data/reports/final_research_report_3.json`.
- Latest research period: 2026-09-23 intraday, completed candles through 13:35 IST.
- Latest result: 4 eligible contracts, 2 Level-to-Level setups, 0 confirmed Ekalayava setups.
- Latest commit before this infrastructure task: `bbddabc`.
- Latest completed-week candidate: 2026-09-07 through 2026-09-11; 16 eligible option files, zero invalid OHLC rows.
- AI demo status: attempted real Groq execution using the key in [llmkey.md](llmkey.md), but the external provider returned `HTTP 403 Forbidden`; no fake AI result was used. The Groq alias compatibility fix in [app/llm.py](app/llm.py) was added so the repo can use the configured provider correctly.
- Current-week snapshot fetched read-only for 2026-09-21 through 2026-09-23: 240 underlying candles and four 2026-09-29 ITM contracts; deterministic baseline preflight produced 19 setups.

## Known Limitations

- The live snapshot is an intraday observation, not a completed trading-day result.
- Ekalayava has no numeric stop-loss rule in the source definition and must remain marked undefined.
- Historical option coverage is uneven across contracts and periods; coverage must be checked before comparisons.
- Out-of-sample validation is insufficient for strategy evolution until separate development and validation periods are assembled.
- The deterministic weekly baseline path is validated, but no AI hypothesis or AI interpretation exists until a real provider is configured.

## Next Objective

Latest bounded demo EXP-8ee0e64d66 completed against a two-month Groww dataset and selected 2026-09-07 through 2026-09-11 after contract and data checks. Decision: NEED_MORE_DATA. Do not promote any strategy change.

## EXP-425143a757 Follow-up

- Previous SMA experiment request discarded as invalid/inconclusive for canonical research.
- The experiment exposed missing result-metric enforcement: aggregate strategy counts did not include per-strategy points or average daily points.
- Missing option intervals and one completed week limited evidence; no fabricated values were used.
- ExperimentSpec validation and result-completeness enforcement now run before Groq interpretation.

## Latest Demo

- Result completeness: PASS; lookahead: PASS; safety: paper-only/read-only.
- Deterministic result: 31 setups, 25 valid, 16 targets, 9 SL, 6 open; average 7.04 points.
- Per-strategy average daily points: Level-to-Level 21.28; Ekalayava 17.40.