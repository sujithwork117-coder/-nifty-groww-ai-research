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
- AI status: real Groq call was attempted using the key in [llmkey.md](llmkey.md), but the provider returned `HTTP 403 Forbidden`; the autonomous experiment remained externally blocked and no AI interpretation was recorded.

## EXP-425143a757

- Canonical grounding successful for NIFTY Level-to-Level and Ekalayava using completed 5-minute candles, ITM 2/3 CE/PE, causal processing, and no interpolation.
- Previous SMA experiment request discarded as invalid/inconclusive for canonical project research.
- The experiment exposed missing result-metric enforcement: aggregate strategy counts did not include per-strategy points or average daily points.
- Data completeness was limited by missing option intervals and one completed week; no fabricated values were used.

## EXP-8ee0e64d66

- Dataset: 60-day read-only Groww fetch at `data/runs/canonical_two_months_20260923_151545/`.
- Selected bounded period: 2026-09-07 through 2026-09-11 after completed-week and contract eligibility checks.
- Structured ExperimentSpec validated before execution; baseline-v1 remained unchanged.
- Result completeness: PASS. Lookahead: PASS. Missing option candles remained unavailable and were not interpolated.
- Result: 31 setups, 25 valid, 16 targets, 9 SL, 6 open, average 7.04 points.
- Strategy breakdown: Level-to-Level average daily points 21.28; Ekalayava 17.40.
- Groq decision: NEED_MORE_DATA.