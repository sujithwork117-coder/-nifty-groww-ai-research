# Ekalayava Guide 8 Execution Summary

> **Historical snapshot:** This report predates Guide 9's bounded 2026
> exact-path recovery. Its 7/253 coverage and resulting candidate ranking are
> superseded by
> [EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md](./EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md),
> [EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md](./EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md),
> and [EKALAYAVA_FINAL_SL_TARGET_DECISION.md](./EKALAYAVA_FINAL_SL_TARGET_DECISION.md).
> The Guide 8 run and test record below remains historical.

## Result

The seven fixed candidates were reconciled once across the 2025 H2 entry set
and all exact-path 2026 observations; the archived fractional TP25 policy was
kept separate from fixed +25 points. The validation screen's 2R choice was
not changed. The strongest gross descriptive candidate is the B2 lower-low
trailing proxy, but the validation, test and sparse 2026 results are flat or
negative. **No candidate is approved.**

## Main findings

* Combined saved-entry denominator: 447 per policy (194 redetected exact
  2025 H2 entries plus 253 saved 2026 entries).
* Exact paths: 192 complete and 2 partial in 2025 H2; 7 complete of 253 in
  the saved 2026 ledger. The 246 unavailable 2026 paths remain unresolved.
* `B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1` had the strongest combined gross
  result: +197.50 points, PF 1.143, max drawdown 190.70 across 201 exact-path
  replays. Its split was +217.65 training, −19.85 validation, +1.25 test and
  −1.55 over seven exact 2026 paths. That is not robust net efficiency.
* The previously reported 2R test was reproduced for all 69 entries, matching
  outcome, points and exit timestamp: 21 target exits, 40 stops, 8
  experimental end-of-session exits, +172.70 gross points, 221.25 max
  drawdown, and a 10-trade longest losing streak.
* The archived fractional TP25 replay matched all 7 eligible exact 2026
  outcomes, points and exit timestamps. The other two archived policy
  replays had previously matched 14/14 comparisons; together this is 21/21
  exact-path comparisons, not verification of the full 253-entry ledger.
* Every candidate's eligible and simulated outcome reconciliation delta is
  zero. No-path entries are explicitly unresolved; no outcomes were imputed.
* Canonical Opening-High touch observations are separated from candidate
  exits. A later touch after a stop is never counted as a target exit.

## Reproduction and tests

The Guide 8 accounting pass is offline; the ignored exact-contract candle
data from the earlier bounded retrieval must exist:

```sh
.venv/bin/python -m tools.run_ekalayava_guide8_reconciliation
```

The command recreates
`reports/EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md`,
`reports/ekalayava_guide8_candidate_counts.csv`,
`reports/ekalayava_guide8_candidate_trade_outcomes.csv`,
`reports/ekalayava_guide8_canonical_opening_high_touches.csv`,
`reports/ekalayava_guide8_test_reproduction.csv`, and
`reports/ekalayava_guide8_reconciliation_summary.json`.

The focused Guide 8 plus related simulator/research tests passed: **17 tests**.
The full repository suite passed: **124 tests**. Syntax compilation passed
for the new runner and tests.

## Constraints and safeguards

* No new data retrieval, additional provider, costs, or trading actions were
  used. All outputs are gross premium points.
* 246 saved 2026 observations lack exact paths; all are unresolved. Entry
  ledgers record qualifying signals, not all rejected pre-entry formations,
  so skipped setup counts cannot be reconstructed.
* The Nov–Dec period was first used once for the frozen 2R candidate. Guide 8
  then performed a single accounting pass for the remaining pre-existing
  candidates to satisfy the requested outcome totals. Those extra results
  are descriptive only and did not change candidate selection.
* `EXECUTION_ALLOWED=False`, `PAPER_ONLY=True`; no orders were submitted.
  No policy was connected to the paper engine.
