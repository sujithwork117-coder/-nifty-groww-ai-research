# Strategy Versions

## baseline-v1

- Status: current baseline.
- Strategies: Level-to-Level and Ekalayava.
- Rules: defined in `NIFTY_Strategy_Definitions_Level_to_Level_Ekalavya.md`.
- Scope: NIFTY only; 5-minute completed candles; Asia/Kolkata; CE/PE; ITM ranks 2 and 3.
- Safety: paper-only, no order placement/modification/cancellation.

## Experimental Versions

None. The infrastructure task intentionally makes no strategy-rule changes.

Every future experimental version must record the prior version, exact rule change, hypothesis, datasets, in-sample result, out-of-sample result, robustness result, decision, date, and experiment ID.