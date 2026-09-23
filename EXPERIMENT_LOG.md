# Experiment Log

The machine-readable experiment history is stored as JSON Lines in `data/agent_state/experiments.jsonl` after an experiment is run. This file records the durable milestones that predate the state manager.

## EXP-2026-09-23-LIVE-03

- Hypothesis: current-session NIFTY option candles can be evaluated causally without using incomplete future candles.
- Dataset: 2026-09-23 completed 5-minute candles through 13:35 IST.
- Strategy version: baseline-v1.
- Result: 4 eligible ITM contracts; 2 Level-to-Level setups; 0 Ekalayava setups.
- Data quality: underlying and option candles had zero invalid OHLC rows and zero duplicate timestamps.
- Decision: observation only; insufficient evidence for a strategy change or out-of-sample claim.

## PRECHECK-2026-09-23-CURRENT-WEEK

- Type: deterministic paper-only preflight; not an AI experiment.
- Dataset: read-only Groww snapshot for 2026-09-21 through 2026-09-23, through 15:25 IST.
- Coverage: 240 underlying candles and four current 2nd/3rd ITM contracts; zero invalid OHLC rows and zero duplicates.
- Result: 19 setups, 13 valid, 6 open/skipped, 6 targets, 7 SL outcomes; lookahead check passed.
- AI status: blocked because no `RESEARCH_LLM_PROVIDER` or `RESEARCH_LLM_API_KEY` is configured.