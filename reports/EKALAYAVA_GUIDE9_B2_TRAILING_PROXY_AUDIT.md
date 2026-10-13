# Guide 9 — B2 Trailing-Proxy Trade-Path Audit

## Conclusion

**No exit policy is approved.** The B2 lower-low trailing proxy is
audited here because it was the previous gross leader. Following
recovery of the missing 2026 paths, it is no longer the highest
combined-gross candidate: `A_B4_OPENING_HIGH_V1` at 685.55 points. No candidate has
demonstrated stable net expectancy. This audit reruns
the fixed policy on its exact available paths and does not change its
rules or select a new policy.

## Candidate rule and scope

Initial stop = causal structural trough − 2 premium points; target =
Opening High; after a completed candle makes a lower low than the
previous two completed lows, the proposed stop is that candle low − 2;
the stop only tightens and is active on the next five-minute candle.
It is a lower-low proxy, not a right-side-confirmed pivot rule.
Candidate outcomes use completed OHLC bars, existing gap and
same-bar-ambiguity conventions, and experimental session-end exits.

## Available data and reproducibility

* 2025 H2 entries: 194;
  192 complete and
  2 partial exact paths.
* Saved 2026 entries: 253;
  253 exact paths after the
  Guide 9 recovery attempt; 0
  entries remain without exact paths.
* Exact-path trades matched in a separate audit replay: 447/
  447.

Run `.venv/bin/python -m tools.run_ekalayava_guide8_reconciliation`
followed by `.venv/bin/python -m tools.run_ekalayava_guide9_audit`.
The detailed audit rows are in
`ekalayava_guide9_b2_trailing_proxy_trade_audit.csv`.

## Period outcomes on exact paths

| Period | Entries | Resolved | Target | Stop | EOD | Unresolved | Gross points | Mean gross / resolved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| OOS_SEP_INCOMPLETE | 15 | 15 | 1 | 13 | 1 | 0 | -83.90 | -5.593 |
| TEST_2025_NOV_DEC | 69 | 69 | 22 | 47 | 0 | 0 | 1.25 | 0.018 |
| TRAIN_2025_JUL_AUG | 61 | 61 | 18 | 42 | 1 | 0 | 217.65 | 3.568 |
| TRAIN_JAN_JUN | 191 | 191 | 45 | 144 | 2 | 0 | 143.55 | 0.752 |
| VALIDATION_2025_SEP_OCT | 64 | 64 | 15 | 49 | 0 | 0 | -19.85 | -0.310 |
| VALIDATION_JUL_AUG | 47 | 47 | 11 | 36 | 0 | 0 | 19.40 | 0.413 |

## Trade-path diagnostics

* MFE mean/median: 20.35 / 12.05 points; MAE mean/median: -14.77 / -11.50 points, measured through each
  simulated terminal bar. OHLC extremes within the terminal bar are
  not ordered; these are excursions, not executable path sequencing.
* Stops within 5 minutes: 5; within
  15 minutes: 51; stops after a
  trailing update: 266;
  gap-through-stop exits: 0.
* Trades with at least one trail update: 303;
  every recorded update was monotonic: True.
* Stop exits followed by an observed later Opening-High touch:
  78/
  331 stops. This is a counterfactual path
  diagnostic, never counted as an actual target exit.
* The top five winners contributed
  15.5% of positive trade points.
* Duplicate entry observations: 0;
  duplicate exit timestamps: 0;
  overlapping same-contract positions: 0.
  See the audit CSV for every entry, path, excursion, stop update and
  whether the independently repeated outcome matched.

## Hypothetical transaction-cost sensitivity

No actual fee, spread, slippage, tax, fill, contract multiplier or
position-size input is configured. The following values are explicitly
scenarios in premium points per completed round trip, not Groww fee
estimates or rupee returns.

| Scenario cost (points/trade) | Resolved trades | Gross points | Scenario net points | Scenario expectancy | PF | Max DD |
|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 447 | 278.10 | 278.10 | 0.622 | 1.067 | 660.90 |
| 0.25 | 447 | 278.10 | 166.35 | 0.372 | 1.040 | 703.65 |
| 0.50 | 447 | 278.10 | 54.60 | 0.122 | 1.013 | 746.40 |
| 1.00 | 447 | 278.10 | -168.90 | -0.378 | 0.962 | 831.90 |
| 2.00 | 447 | 278.10 | -615.90 | -1.378 | 0.869 | 1005.20 |

Uniform round-trip cost reaches gross break-even at approximately 0.622 premium points per
resolved trade. This threshold does not establish whether real costs
are below it. The historical test segment is already retrospective;
its gross contribution is too small to tolerate meaningful costs.

## Interpretation and decision

The exact-path results show both early adverse movement and frequent
trailing exits; neither alone proves the entry or stop is defective.
An observed later target touch after a stop cannot justify holding
through the stop. The proxy was implemented consistently on this
replay, but no new structural pivot variant is promoted: the sample
does not support a fair selection, test results are retrospective, and
net costs are unmeasured. Keep the canonical exit unresolved and
do not connect this candidate to the paper engine.

Execution safety: `EXECUTION_ALLOWED=False`, `PAPER_ONLY=True`; no
orders were submitted.
