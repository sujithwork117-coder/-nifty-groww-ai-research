# Ekalayava Target/Stop Count Reconciliation

## Decision and scope

**No exit policy is approved.** The six Guide 7 candidates and the
archived fractional `A_STRUCTURAL_TROUGH_B4_TP25` policy were each
accounted once on the fixed candidate set. This accounting does not
change the prior validation selection or select a policy from test
results. The additional November–December counts for non-selected
candidates are descriptive only; they are not used for ranking or
tuning.

The combined ledger has 447 recorded eligible entry observations:
194 independently redetected on exact 2025 H2 contract paths and 253
from the saved 2026 entry ledger. Exact post-entry paths exist for 194
2025 entries (192 complete, 2 partial) and 7 of the 253 2026 entries;
the other 246 2026 outcomes remain unresolved due to missing exact
contract candles. Entry observations in the historical 2026 saved
ledger are not all independently revalidated.
The canonical detector/ledger records entry signals, not all
pre-entry candidate formations or rejected setups; those skipped
formation counts are not available and are not estimated.

Outcome categories are mutually exclusive. `simulated_entries_with_exact_path`
counts valid candidate replays on available paths; `unresolved_entries`
also includes the 246 missing-path observations. Consequently the
eligible-entry reconciliation includes missing paths, while the
simulated-entry reconciliation excludes them. Negative reconciliation
deltas indicate an accounting defect and must be zero.

## Overall counts by candidate

| Candidate | Target | Stop | Ambiguous | EOD | Other | Unresolved | Eligible | Simulated with path | Gross points | Approval |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A_B4_OPENING_HIGH_V1 | 78 | 104 | 0 | 19 | 0 | 246 | 447 | 201 | -1.20 | Not approved |
| A_B4_TP25_V1 | 93 | 100 | 0 | 8 | 0 | 246 | 447 | 201 | -198.75 | Not approved |
| A_STRUCTURAL_TROUGH_B4_TP25 | 131 | 67 | 0 | 3 | 0 | 246 | 447 | 201 | -122.20 | Not approved |
| B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 57 | 143 | 0 | 1 | 0 | 246 | 447 | 201 | 197.50 | Not approved |
| C_B2_1R_V1 | 86 | 104 | 0 | 11 | 0 | 246 | 447 | 201 | -577.85 | Not approved |
| C_B2_1_5R_V1 | 71 | 115 | 0 | 15 | 0 | 246 | 447 | 201 | -259.72 | Not approved |
| C_B2_2R_V1 | 61 | 123 | 0 | 17 | 0 | 246 | 447 | 201 | -80.95 | Not approved |

The combined table includes 2025 H2 plus the full saved 2026 ledger.
Every policy has 447 eligible entries; 201 have exact paths to run
(including two partial 2025 paths) and 246 2026 entries have no exact
path. Candidate gross totals include only resolved simulations, not
missing or unresolved paths. A positive gross total is not evidence
of net profitability.

### Strongest experimental candidate (not approved)

`B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1` has the highest combined gross points (197.50), the highest combined profit factor (1.143), and the lowest combined drawdown (190.70) among these fixed candidates. Its
chronological results do not establish stability:
* Training: 217.65 gross points (PF 1.528).
* Validation: -19.85 (PF 0.960).
* Test: 1.25 (PF 1.003).
* Seven exact 2026 paths: -1.55 gross points.
The test-period mean was 0.018 gross points per entry; fees, spread and slippage are unavailable,
so even this small gross edge cannot support a net-efficiency claim.
This candidate is the lead for further evidence collection only; it
is not approved for the paper engine or trading.

### Target-touch reconciliation by candidate (combined ledger)

| Candidate | Touched while open | Ambiguous touch order | Touched after exit | Not touched | Unverifiable |
|---|---:|---:|---:|---:|---:|
| A_B4_OPENING_HIGH_V1 | 78 | 0 | 9 | 112 | 248 |
| A_B4_TP25_V1 | 93 | 0 | 15 | 91 | 248 |
| A_STRUCTURAL_TROUGH_B4_TP25 | 131 | 0 | 14 | 54 | 248 |
| B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 57 | 0 | 30 | 112 | 248 |
| C_B2_1R_V1 | 86 | 0 | 20 | 93 | 248 |
| C_B2_1_5R_V1 | 71 | 0 | 14 | 114 | 248 |
| C_B2_2R_V1 | 61 | 0 | 10 | 128 | 248 |

## Period results

Counts are policy-specific; target exits across different candidates
must not be added. `Unresolved` includes missing exact-path entries.

| Period | Candidate | Eligible | Simulated with path | Target | Stop | Ambiguous | EOD | Other | Unresolved | Gross points | Win rate | PF | Max DD | Longest loss streak |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EXISTING_2026_ENTRY_LEDGER | A_B4_OPENING_HIGH_V1 | 253 | 7 | 5 | 2 | 0 | 0 | 0 | 246 | 94.05 | 71.4% | 2.689 | 55.70 | 2 |
| EXISTING_2026_ENTRY_LEDGER | A_B4_TP25_V1 | 253 | 7 | 3 | 4 | 0 | 0 | 0 | 246 | -76.00 | 42.9% | 0.497 | 151.00 | 4 |
| EXISTING_2026_ENTRY_LEDGER | A_STRUCTURAL_TROUGH_B4_TP25 | 253 | 7 | 7 | 0 | 0 | 0 | 0 | 246 | 45.04 | 100.0% | n/a | 0.00 | 0 |
| EXISTING_2026_ENTRY_LEDGER | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 253 | 7 | 2 | 5 | 0 | 0 | 0 | 246 | -1.55 | 57.1% | 0.960 | 28.10 | 2 |
| EXISTING_2026_ENTRY_LEDGER | C_B2_1R_V1 | 253 | 7 | 3 | 4 | 0 | 0 | 0 | 246 | -74.90 | 42.9% | 0.476 | 143.00 | 4 |
| EXISTING_2026_ENTRY_LEDGER | C_B2_1_5R_V1 | 253 | 7 | 2 | 5 | 0 | 0 | 0 | 246 | -94.60 | 28.6% | 0.425 | 143.00 | 4 |
| EXISTING_2026_ENTRY_LEDGER | C_B2_2R_V1 | 253 | 7 | 2 | 5 | 0 | 0 | 0 | 246 | -71.30 | 28.6% | 0.567 | 143.00 | 4 |
| GROWW_2025_H2 | A_B4_OPENING_HIGH_V1 | 194 | 194 | 73 | 102 | 0 | 19 | 0 | 0 | -95.25 | 44.3% | 0.961 | 602.05 | 12 |
| GROWW_2025_H2 | A_B4_TP25_V1 | 194 | 194 | 90 | 96 | 0 | 8 | 0 | 0 | -122.75 | 47.4% | 0.948 | 601.85 | 10 |
| GROWW_2025_H2 | A_STRUCTURAL_TROUGH_B4_TP25 | 194 | 194 | 124 | 67 | 0 | 3 | 0 | 0 | -167.24 | 64.9% | 0.881 | 343.10 | 6 |
| GROWW_2025_H2 | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 194 | 194 | 55 | 138 | 0 | 1 | 0 | 0 | 199.05 | 42.8% | 1.148 | 190.70 | 10 |
| GROWW_2025_H2 | C_B2_1R_V1 | 194 | 194 | 83 | 100 | 0 | 11 | 0 | 0 | -502.95 | 43.8% | 0.799 | 766.65 | 8 |
| GROWW_2025_H2 | C_B2_1_5R_V1 | 194 | 194 | 69 | 110 | 0 | 15 | 0 | 0 | -165.12 | 38.7% | 0.939 | 467.88 | 10 |
| GROWW_2025_H2 | C_B2_2R_V1 | 194 | 194 | 59 | 118 | 0 | 17 | 0 | 0 | -9.65 | 34.5% | 0.997 | 472.70 | 10 |
| OOS_SEP_INCOMPLETE | A_B4_OPENING_HIGH_V1 | 15 | 1 | 0 | 1 | 0 | 0 | 0 | 14 | -23.90 | 0.0% | 0.000 | 23.90 | 1 |
| OOS_SEP_INCOMPLETE | A_B4_TP25_V1 | 15 | 1 | 0 | 1 | 0 | 0 | 0 | 14 | -23.90 | 0.0% | 0.000 | 23.90 | 1 |
| OOS_SEP_INCOMPLETE | A_STRUCTURAL_TROUGH_B4_TP25 | 15 | 1 | 1 | 0 | 0 | 0 | 0 | 14 | 5.00 | 100.0% | n/a | 0.00 | 0 |
| OOS_SEP_INCOMPLETE | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 15 | 1 | 0 | 1 | 0 | 0 | 0 | 14 | -12.35 | 0.0% | 0.000 | 12.35 | 1 |
| OOS_SEP_INCOMPLETE | C_B2_1R_V1 | 15 | 1 | 0 | 1 | 0 | 0 | 0 | 14 | -21.90 | 0.0% | 0.000 | 21.90 | 1 |
| OOS_SEP_INCOMPLETE | C_B2_1_5R_V1 | 15 | 1 | 0 | 1 | 0 | 0 | 0 | 14 | -21.90 | 0.0% | 0.000 | 21.90 | 1 |
| OOS_SEP_INCOMPLETE | C_B2_2R_V1 | 15 | 1 | 0 | 1 | 0 | 0 | 0 | 14 | -21.90 | 0.0% | 0.000 | 21.90 | 1 |
| TEST_2025_NOV_DEC | A_B4_OPENING_HIGH_V1 | 69 | 69 | 30 | 35 | 0 | 4 | 0 | 0 | 167.25 | 49.3% | 1.251 | 269.05 | 10 |
| TEST_2025_NOV_DEC | A_B4_TP25_V1 | 69 | 69 | 34 | 35 | 0 | 0 | 0 | 0 | 148.20 | 49.3% | 1.211 | 251.40 | 10 |
| TEST_2025_NOV_DEC | A_STRUCTURAL_TROUGH_B4_TP25 | 69 | 69 | 45 | 24 | 0 | 0 | 0 | 0 | -7.36 | 65.2% | 0.980 | 114.40 | 6 |
| TEST_2025_NOV_DEC | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 69 | 69 | 22 | 47 | 0 | 0 | 0 | 0 | 1.25 | 43.5% | 1.003 | 163.70 | 10 |
| TEST_2025_NOV_DEC | C_B2_1R_V1 | 69 | 69 | 34 | 31 | 0 | 4 | 0 | 0 | 76.95 | 50.7% | 1.113 | 185.00 | 7 |
| TEST_2025_NOV_DEC | C_B2_1_5R_V1 | 69 | 69 | 26 | 37 | 0 | 6 | 0 | 0 | 118.22 | 42.0% | 1.154 | 194.53 | 10 |
| TEST_2025_NOV_DEC | C_B2_2R_V1 | 69 | 69 | 21 | 40 | 0 | 8 | 0 | 0 | 172.70 | 37.7% | 1.207 | 221.25 | 10 |
| TRAIN_2025_JUL_AUG | A_B4_OPENING_HIGH_V1 | 61 | 61 | 21 | 31 | 0 | 9 | 0 | 0 | -120.90 | 42.6% | 0.857 | 306.85 | 10 |
| TRAIN_2025_JUL_AUG | A_B4_TP25_V1 | 61 | 61 | 30 | 25 | 0 | 6 | 0 | 0 | 50.90 | 52.5% | 1.072 | 203.85 | 6 |
| TRAIN_2025_JUL_AUG | A_STRUCTURAL_TROUGH_B4_TP25 | 61 | 61 | 40 | 18 | 0 | 3 | 0 | 0 | 26.09 | 68.9% | 1.063 | 190.09 | 5 |
| TRAIN_2025_JUL_AUG | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 61 | 61 | 18 | 42 | 0 | 1 | 0 | 0 | 217.65 | 45.9% | 1.528 | 150.00 | 7 |
| TRAIN_2025_JUL_AUG | C_B2_1R_V1 | 61 | 61 | 23 | 33 | 0 | 5 | 0 | 0 | -303.65 | 39.3% | 0.670 | 374.10 | 8 |
| TRAIN_2025_JUL_AUG | C_B2_1_5R_V1 | 61 | 61 | 19 | 37 | 0 | 5 | 0 | 0 | -274.30 | 32.8% | 0.732 | 361.17 | 8 |
| TRAIN_2025_JUL_AUG | C_B2_2R_V1 | 61 | 61 | 16 | 40 | 0 | 5 | 0 | 0 | -258.20 | 27.9% | 0.764 | 325.90 | 8 |
| TRAIN_JAN_JUN | A_B4_OPENING_HIGH_V1 | 191 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.00 | n/a | n/a | 0.00 | 0 |
| TRAIN_JAN_JUN | A_B4_TP25_V1 | 191 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.00 | n/a | n/a | 0.00 | 0 |
| TRAIN_JAN_JUN | A_STRUCTURAL_TROUGH_B4_TP25 | 191 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.00 | n/a | n/a | 0.00 | 0 |
| TRAIN_JAN_JUN | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 191 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.00 | n/a | n/a | 0.00 | 0 |
| TRAIN_JAN_JUN | C_B2_1R_V1 | 191 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.00 | n/a | n/a | 0.00 | 0 |
| TRAIN_JAN_JUN | C_B2_1_5R_V1 | 191 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.00 | n/a | n/a | 0.00 | 0 |
| TRAIN_JAN_JUN | C_B2_2R_V1 | 191 | 0 | 0 | 0 | 0 | 0 | 0 | 191 | 0.00 | n/a | n/a | 0.00 | 0 |
| VALIDATION_2025_SEP_OCT | A_B4_OPENING_HIGH_V1 | 64 | 64 | 22 | 36 | 0 | 6 | 0 | 0 | -141.60 | 40.6% | 0.851 | 249.55 | 7 |
| VALIDATION_2025_SEP_OCT | A_B4_TP25_V1 | 64 | 64 | 26 | 36 | 0 | 2 | 0 | 0 | -321.85 | 40.6% | 0.669 | 406.00 | 8 |
| VALIDATION_2025_SEP_OCT | A_STRUCTURAL_TROUGH_B4_TP25 | 64 | 64 | 39 | 25 | 0 | 0 | 0 | 0 | -185.96 | 60.9% | 0.698 | 261.27 | 6 |
| VALIDATION_2025_SEP_OCT | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 64 | 64 | 15 | 49 | 0 | 0 | 0 | 0 | -19.85 | 39.1% | 0.960 | 190.70 | 6 |
| VALIDATION_2025_SEP_OCT | C_B2_1R_V1 | 64 | 64 | 26 | 36 | 0 | 2 | 0 | 0 | -276.25 | 40.6% | 0.693 | 412.90 | 8 |
| VALIDATION_2025_SEP_OCT | C_B2_1_5R_V1 | 64 | 64 | 24 | 36 | 0 | 4 | 0 | 0 | -9.05 | 40.6% | 0.990 | 333.42 | 8 |
| VALIDATION_2025_SEP_OCT | C_B2_2R_V1 | 64 | 64 | 22 | 38 | 0 | 4 | 0 | 0 | 75.85 | 37.5% | 1.079 | 306.70 | 8 |
| VALIDATION_JUL_AUG | A_B4_OPENING_HIGH_V1 | 47 | 6 | 5 | 1 | 0 | 0 | 0 | 41 | 117.95 | 83.3% | 4.709 | 31.80 | 1 |
| VALIDATION_JUL_AUG | A_B4_TP25_V1 | 47 | 6 | 3 | 3 | 0 | 0 | 0 | 41 | -52.10 | 50.0% | 0.590 | 127.10 | 3 |
| VALIDATION_JUL_AUG | A_STRUCTURAL_TROUGH_B4_TP25 | 47 | 6 | 6 | 0 | 0 | 0 | 0 | 41 | 40.04 | 100.0% | n/a | 0.00 | 0 |
| VALIDATION_JUL_AUG | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 47 | 6 | 2 | 4 | 0 | 0 | 0 | 41 | 10.80 | 66.7% | 1.408 | 15.75 | 1 |
| VALIDATION_JUL_AUG | C_B2_1R_V1 | 47 | 6 | 3 | 3 | 0 | 0 | 0 | 41 | -53.00 | 50.0% | 0.562 | 121.10 | 3 |
| VALIDATION_JUL_AUG | C_B2_1_5R_V1 | 47 | 6 | 2 | 4 | 0 | 0 | 0 | 41 | -72.70 | 33.3% | 0.490 | 121.10 | 3 |
| VALIDATION_JUL_AUG | C_B2_2R_V1 | 47 | 6 | 2 | 4 | 0 | 0 | 0 | 41 | -49.40 | 33.3% | 0.654 | 121.10 | 3 |

## Canonical Opening-High touch observations

* Recorded entry observations: **447**.
* Opening High touched on the observed post-entry path: **87**.
* Complete paths with no touch: **112**.
* Touch rate among verifiable paths: **43.7%** (87/199).
* Incomplete or missing paths where touch is not verifiable: **248**.

These are observational price touches, not policy exits or wins. Policy
target-touch classifications are separately recorded in
`reports/ekalayava_guide8_candidate_trade_outcomes.csv` and summarized
in `reports/ekalayava_guide8_candidate_counts.csv`.

## Previous 2R holdout reconciliation

The existing 69-row 2R test ledger was matched against an independent
rerun of the exact 2025 entry paths: 69/
69 rows matched on outcome, points and
exit timestamp. Reproduced outcomes: 21 targets, 40 stops, 8 end-of-session, 0 ambiguous, and 0 unresolved. Gross points: 172.70; maximum drawdown: 221.25; longest losing streak: 10. The reported 21/40/8
result is therefore reproduced.

The archived fractional TP25 replay matched 7/7 available exact-path
events on outcome, points, and exit timestamp. This does not verify
archived outcomes for entries without exact paths.

## Category and denominator rules

* The candidate count CSV explicitly names each percentage denominator:
  exit rates of eligible entries or simulated entries, unresolved rate
  of eligible entries, and win rate of resolved outcomes with points.
  Percentages must not be compared without checking that denominator.
* A target touch is counted as an actual target exit only when the
  simulator exited at target. Later touches after a stop are recorded
  separately. Same-bar stop/target collisions are ambiguous, and the
  target-touch ordering for that bar is not asserted.
* Partial/missing candle paths are not interpolated. A target touch
  not observed on an incomplete path is unverifiable, not a no-touch.
* End-of-session close is experimental. Fees, spreads, slippage, taxes
  and account sizing are unavailable; points are gross only.
* Detailed rows, period counts, and rerun output are available in the
  accompanying CSV/JSON artifacts. Reproduce with
  `.venv/bin/python -m tools.run_ekalayava_guide8_reconciliation`.

## Independent reproduction details

* 2025 exact-path rows replayed across each candidate: 1358.
* Exact 2026 paths: 7/253.
* Archived fractional TP25 exact-path reproductions: 7/7.
* Full saved-ledger outcome counts are not inferable where exact 2026
  paths are missing.
