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
from the saved 2026 entry ledger. The exact-path inventory has 192 complete and 2 partial 2025 entry paths, plus 253 exact 2026 paths out of 253; 0 saved 2026 entries have no exact path after the bounded recovery attempt. The 2026 entry signals themselves were not all
independently redetected.
The canonical detector/ledger records entry signals, not all
pre-entry candidate formations or rejected setups; those skipped
formation counts are not available and are not estimated.

Outcome categories are mutually exclusive. `simulated_entries_with_exact_path`
counts valid candidate replays on available paths; `unresolved_entries`
also includes any missing-path observations. Consequently the
eligible-entry reconciliation includes missing paths, while the
simulated-entry reconciliation excludes them. Negative reconciliation
deltas indicate an accounting defect and must be zero.

## Overall counts by candidate

| Candidate | Target | Stop | Ambiguous | EOD | Other | Unresolved | Eligible | Simulated with path | Gross points | Approval |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A_B4_OPENING_HIGH_V1 | 164 | 243 | 0 | 40 | 0 | 0 | 447 | 447 | 685.55 | Not approved |
| A_B4_TP25_V1 | 197 | 232 | 0 | 18 | 0 | 0 | 447 | 447 | -1476.05 | Not approved |
| A_STRUCTURAL_TROUGH_B4_TP25 | 281 | 160 | 0 | 6 | 0 | 0 | 447 | 447 | -440.14 | Not approved |
| B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 112 | 331 | 0 | 4 | 0 | 0 | 447 | 447 | 278.10 | Not approved |
| C_B2_1R_V1 | 190 | 239 | 0 | 18 | 0 | 0 | 447 | 447 | -1740.85 | Not approved |
| C_B2_1_5R_V1 | 154 | 265 | 0 | 28 | 0 | 0 | 447 | 447 | -1289.90 | Not approved |
| C_B2_2R_V1 | 127 | 282 | 0 | 38 | 0 | 0 | 447 | 447 | -1151.50 | Not approved |

The combined table includes 2025 H2 plus the full saved 2026 ledger.
Every policy has 447 eligible entries; 447 have exact paths to run, including 2 partial 2025 paths. 0 saved 2026 entries remain without exact paths. Candidate gross totals include only resolved simulations, not
missing or unresolved paths. A positive gross total is not evidence
of net profitability.

### Strongest experimental candidate (not approved)

`A_B4_OPENING_HIGH_V1` has the highest combined gross points (685.55) among the fixed candidates; its
combined PF is 1.105 and drawdown is 602.05. This descriptive lead is not
stable across the chronological slices:
* Training: -120.90 gross points (PF 0.857).
* Validation: -141.60 (PF 0.851).
* Test: 167.25 (PF 1.251).
* Saved 2026 entries (253/253 exact paths): 780.80 gross points.
The additional all-candidate test replays are retrospective count
accounting; no test results were used to change or retune the frozen
candidate definitions. The lead remains unapproved for the paper
engine or trading.

### Target-touch reconciliation by candidate (combined ledger)

| Candidate | Touched while open | Ambiguous touch order | Touched after exit | Not touched | Unverifiable |
|---|---:|---:|---:|---:|---:|
| A_B4_OPENING_HIGH_V1 | 164 | 0 | 26 | 255 | 2 |
| A_B4_TP25_V1 | 197 | 0 | 46 | 202 | 2 |
| A_STRUCTURAL_TROUGH_B4_TP25 | 281 | 0 | 46 | 118 | 2 |
| B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 112 | 0 | 78 | 255 | 2 |
| C_B2_1R_V1 | 190 | 0 | 59 | 196 | 2 |
| C_B2_1_5R_V1 | 154 | 0 | 38 | 253 | 2 |
| C_B2_2R_V1 | 127 | 0 | 30 | 288 | 2 |

## Period results

Counts are policy-specific; target exits across different candidates
must not be added. `Unresolved` includes missing exact-path entries.

| Period | Candidate | Eligible | Simulated with path | Target | Stop | Ambiguous | EOD | Other | Unresolved | Gross points | Win rate | PF | Max DD | Longest loss streak |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EXISTING_2026_ENTRY_LEDGER | A_B4_OPENING_HIGH_V1 | 253 | 253 | 91 | 141 | 0 | 21 | 0 | 0 | 780.80 | 40.7% | 1.193 | 601.15 | 23 |
| EXISTING_2026_ENTRY_LEDGER | A_B4_TP25_V1 | 253 | 253 | 107 | 136 | 0 | 10 | 0 | 0 | -1353.30 | 43.1% | 0.665 | 1360.60 | 12 |
| EXISTING_2026_ENTRY_LEDGER | A_STRUCTURAL_TROUGH_B4_TP25 | 253 | 253 | 157 | 93 | 0 | 3 | 0 | 0 | -272.90 | 62.8% | 0.884 | 732.09 | 9 |
| EXISTING_2026_ENTRY_LEDGER | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 253 | 253 | 57 | 193 | 0 | 3 | 0 | 0 | 79.05 | 37.9% | 1.028 | 660.90 | 17 |
| EXISTING_2026_ENTRY_LEDGER | C_B2_1R_V1 | 253 | 253 | 107 | 139 | 0 | 7 | 0 | 0 | -1237.90 | 43.1% | 0.717 | 1328.65 | 10 |
| EXISTING_2026_ENTRY_LEDGER | C_B2_1_5R_V1 | 253 | 253 | 85 | 155 | 0 | 13 | 0 | 0 | -1124.77 | 34.8% | 0.768 | 1346.32 | 23 |
| EXISTING_2026_ENTRY_LEDGER | C_B2_2R_V1 | 253 | 253 | 68 | 164 | 0 | 21 | 0 | 0 | -1141.85 | 30.4% | 0.776 | 1711.65 | 23 |
| GROWW_2025_H2 | A_B4_OPENING_HIGH_V1 | 194 | 194 | 73 | 102 | 0 | 19 | 0 | 0 | -95.25 | 44.3% | 0.961 | 602.05 | 12 |
| GROWW_2025_H2 | A_B4_TP25_V1 | 194 | 194 | 90 | 96 | 0 | 8 | 0 | 0 | -122.75 | 47.4% | 0.948 | 601.85 | 10 |
| GROWW_2025_H2 | A_STRUCTURAL_TROUGH_B4_TP25 | 194 | 194 | 124 | 67 | 0 | 3 | 0 | 0 | -167.24 | 64.9% | 0.881 | 343.10 | 6 |
| GROWW_2025_H2 | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 194 | 194 | 55 | 138 | 0 | 1 | 0 | 0 | 199.05 | 42.8% | 1.148 | 190.70 | 10 |
| GROWW_2025_H2 | C_B2_1R_V1 | 194 | 194 | 83 | 100 | 0 | 11 | 0 | 0 | -502.95 | 43.8% | 0.799 | 766.65 | 8 |
| GROWW_2025_H2 | C_B2_1_5R_V1 | 194 | 194 | 69 | 110 | 0 | 15 | 0 | 0 | -165.12 | 38.7% | 0.939 | 467.88 | 10 |
| GROWW_2025_H2 | C_B2_2R_V1 | 194 | 194 | 59 | 118 | 0 | 17 | 0 | 0 | -9.65 | 34.5% | 0.997 | 472.70 | 10 |
| OOS_SEP_INCOMPLETE | A_B4_OPENING_HIGH_V1 | 15 | 15 | 2 | 12 | 0 | 1 | 0 | 0 | -205.05 | 13.3% | 0.270 | 253.65 | 11 |
| OOS_SEP_INCOMPLETE | A_B4_TP25_V1 | 15 | 15 | 3 | 11 | 0 | 1 | 0 | 0 | -185.75 | 20.0% | 0.288 | 218.05 | 10 |
| OOS_SEP_INCOMPLETE | A_STRUCTURAL_TROUGH_B4_TP25 | 15 | 15 | 10 | 4 | 0 | 1 | 0 | 0 | 11.66 | 66.7% | 1.198 | 55.20 | 4 |
| OOS_SEP_INCOMPLETE | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 15 | 15 | 1 | 13 | 0 | 1 | 0 | 0 | -83.90 | 13.3% | 0.423 | 135.10 | 10 |
| OOS_SEP_INCOMPLETE | C_B2_1R_V1 | 15 | 15 | 3 | 11 | 0 | 1 | 0 | 0 | -170.95 | 20.0% | 0.284 | 200.05 | 10 |
| OOS_SEP_INCOMPLETE | C_B2_1_5R_V1 | 15 | 15 | 3 | 11 | 0 | 1 | 0 | 0 | -137.05 | 20.0% | 0.426 | 200.05 | 10 |
| OOS_SEP_INCOMPLETE | C_B2_2R_V1 | 15 | 15 | 2 | 11 | 0 | 2 | 0 | 0 | -140.00 | 20.0% | 0.414 | 200.05 | 10 |
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
| TRAIN_JAN_JUN | A_B4_OPENING_HIGH_V1 | 191 | 191 | 70 | 108 | 0 | 13 | 0 | 0 | 793.70 | 40.8% | 1.243 | 601.15 | 23 |
| TRAIN_JAN_JUN | A_B4_TP25_V1 | 191 | 191 | 85 | 102 | 0 | 4 | 0 | 0 | -982.70 | 44.5% | 0.684 | 985.15 | 12 |
| TRAIN_JAN_JUN | A_STRUCTURAL_TROUGH_B4_TP25 | 191 | 191 | 118 | 73 | 0 | 0 | 0 | 0 | -212.31 | 61.8% | 0.890 | 600.58 | 9 |
| TRAIN_JAN_JUN | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 191 | 191 | 45 | 144 | 0 | 2 | 0 | 0 | 143.55 | 37.7% | 1.062 | 542.95 | 17 |
| TRAIN_JAN_JUN | C_B2_1R_V1 | 191 | 191 | 82 | 106 | 0 | 3 | 0 | 0 | -907.80 | 43.5% | 0.744 | 997.15 | 10 |
| TRAIN_JAN_JUN | C_B2_1_5R_V1 | 191 | 191 | 65 | 118 | 0 | 8 | 0 | 0 | -831.37 | 35.1% | 0.789 | 1018.22 | 23 |
| TRAIN_JAN_JUN | C_B2_2R_V1 | 191 | 191 | 52 | 126 | 0 | 13 | 0 | 0 | -864.65 | 30.9% | 0.792 | 1397.65 | 23 |
| VALIDATION_2025_SEP_OCT | A_B4_OPENING_HIGH_V1 | 64 | 64 | 22 | 36 | 0 | 6 | 0 | 0 | -141.60 | 40.6% | 0.851 | 249.55 | 7 |
| VALIDATION_2025_SEP_OCT | A_B4_TP25_V1 | 64 | 64 | 26 | 36 | 0 | 2 | 0 | 0 | -321.85 | 40.6% | 0.669 | 406.00 | 8 |
| VALIDATION_2025_SEP_OCT | A_STRUCTURAL_TROUGH_B4_TP25 | 64 | 64 | 39 | 25 | 0 | 0 | 0 | 0 | -185.96 | 60.9% | 0.698 | 261.27 | 6 |
| VALIDATION_2025_SEP_OCT | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 64 | 64 | 15 | 49 | 0 | 0 | 0 | 0 | -19.85 | 39.1% | 0.960 | 190.70 | 6 |
| VALIDATION_2025_SEP_OCT | C_B2_1R_V1 | 64 | 64 | 26 | 36 | 0 | 2 | 0 | 0 | -276.25 | 40.6% | 0.693 | 412.90 | 8 |
| VALIDATION_2025_SEP_OCT | C_B2_1_5R_V1 | 64 | 64 | 24 | 36 | 0 | 4 | 0 | 0 | -9.05 | 40.6% | 0.990 | 333.42 | 8 |
| VALIDATION_2025_SEP_OCT | C_B2_2R_V1 | 64 | 64 | 22 | 38 | 0 | 4 | 0 | 0 | 75.85 | 37.5% | 1.079 | 306.70 | 8 |
| VALIDATION_JUL_AUG | A_B4_OPENING_HIGH_V1 | 47 | 47 | 19 | 21 | 0 | 7 | 0 | 0 | 192.15 | 48.9% | 1.381 | 244.90 | 8 |
| VALIDATION_JUL_AUG | A_B4_TP25_V1 | 47 | 47 | 19 | 23 | 0 | 5 | 0 | 0 | -184.85 | 44.7% | 0.723 | 409.85 | 8 |
| VALIDATION_JUL_AUG | A_STRUCTURAL_TROUGH_B4_TP25 | 47 | 47 | 29 | 16 | 0 | 2 | 0 | 0 | -72.25 | 66.0% | 0.807 | 249.84 | 7 |
| VALIDATION_JUL_AUG | B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1 | 47 | 47 | 11 | 36 | 0 | 0 | 0 | 0 | 19.40 | 46.8% | 1.056 | 198.35 | 8 |
| VALIDATION_JUL_AUG | C_B2_1R_V1 | 47 | 47 | 22 | 22 | 0 | 3 | 0 | 0 | -159.15 | 48.9% | 0.735 | 359.30 | 7 |
| VALIDATION_JUL_AUG | C_B2_1_5R_V1 | 47 | 47 | 17 | 26 | 0 | 4 | 0 | 0 | -156.35 | 38.3% | 0.771 | 421.62 | 8 |
| VALIDATION_JUL_AUG | C_B2_2R_V1 | 47 | 47 | 14 | 27 | 0 | 6 | 0 | 0 | -137.20 | 31.9% | 0.806 | 438.70 | 13 |

## Canonical Opening-High touch observations

* Recorded entry observations: **447**.
* Opening High touched on the observed post-entry path: **190**.
* Complete paths with no touch: **255**.
* Touch rate among verifiable paths: **42.7%** (190/445).
* Incomplete or missing paths where touch is not verifiable: **2**.

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

The archived fractional TP25 replay matched 253/253 available exact-path
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
* Exact 2026 paths: 253/253.
* Archived fractional TP25 exact-path reproductions: 253/253.
* All 2026 saved entries have exact paths; 2025 partial paths remain
  explicitly partial and were not extended or interpolated.
