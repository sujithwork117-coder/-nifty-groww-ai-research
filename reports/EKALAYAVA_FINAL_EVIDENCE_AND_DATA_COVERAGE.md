# Ekalayava Final Evidence and Data Coverage

## Verified local inventory

The 2025 H2 exact-option data came from the bounded Groww catalog-first
retrieval recorded in `data/derived/ekalayava_2025_h2_groww/manifest.json`.
Its 492 selected contract-session paths comprise 488 complete and 4
partial sessions; the unchanged canonical detector produced 194
qualifying Ekalayava entries with 192 complete and 2 partial exact paths.
These include 61 training, 64 validation and 69 historical-test entries.

The saved 2026 ledger has 253 entry observations across Jan–September
2026. A one-time, read-only recovery attempt requested only the exact
symbol/date sessions missing from that ledger, with no retries or
substitutions.

* Planned recovery requests: 246.
* Completed requests: 246; data responses: 246;
  empty responses: 0.
* Recovery completed without an API exception.

## Entry-path status by period, contract type and ITM rank

| Dataset | Period | Type | ITM rank | Path status | Entries |
|---|---|---|---:|---|---:|
| EXISTING_2026_ENTRY_LEDGER | OOS_SEP_INCOMPLETE | CE | 2 | COMPLETE_POST_ENTRY_PATH | 4 |
| EXISTING_2026_ENTRY_LEDGER | OOS_SEP_INCOMPLETE | CE | 3 | COMPLETE_POST_ENTRY_PATH | 5 |
| EXISTING_2026_ENTRY_LEDGER | OOS_SEP_INCOMPLETE | PE | 2 | COMPLETE_POST_ENTRY_PATH | 3 |
| EXISTING_2026_ENTRY_LEDGER | OOS_SEP_INCOMPLETE | PE | 3 | COMPLETE_POST_ENTRY_PATH | 3 |
| EXISTING_2026_ENTRY_LEDGER | TRAIN_JAN_JUN | CE | 2 | COMPLETE_POST_ENTRY_PATH | 48 |
| EXISTING_2026_ENTRY_LEDGER | TRAIN_JAN_JUN | CE | 3 | COMPLETE_POST_ENTRY_PATH | 47 |
| EXISTING_2026_ENTRY_LEDGER | TRAIN_JAN_JUN | PE | 2 | COMPLETE_POST_ENTRY_PATH | 50 |
| EXISTING_2026_ENTRY_LEDGER | TRAIN_JAN_JUN | PE | 3 | COMPLETE_POST_ENTRY_PATH | 46 |
| EXISTING_2026_ENTRY_LEDGER | VALIDATION_JUL_AUG | CE | 2 | COMPLETE_POST_ENTRY_PATH | 12 |
| EXISTING_2026_ENTRY_LEDGER | VALIDATION_JUL_AUG | CE | 3 | COMPLETE_POST_ENTRY_PATH | 10 |
| EXISTING_2026_ENTRY_LEDGER | VALIDATION_JUL_AUG | PE | 2 | COMPLETE_POST_ENTRY_PATH | 11 |
| EXISTING_2026_ENTRY_LEDGER | VALIDATION_JUL_AUG | PE | 3 | COMPLETE_POST_ENTRY_PATH | 14 |
| GROWW_2025_H2 | TEST_2025_NOV_DEC | CE | 2 | COMPLETE_POST_ENTRY_PATH | 20 |
| GROWW_2025_H2 | TEST_2025_NOV_DEC | CE | 3 | COMPLETE_POST_ENTRY_PATH | 16 |
| GROWW_2025_H2 | TEST_2025_NOV_DEC | PE | 2 | COMPLETE_POST_ENTRY_PATH | 17 |
| GROWW_2025_H2 | TEST_2025_NOV_DEC | PE | 3 | COMPLETE_POST_ENTRY_PATH | 16 |
| GROWW_2025_H2 | TRAIN_2025_JUL_AUG | CE | 2 | COMPLETE_POST_ENTRY_PATH | 17 |
| GROWW_2025_H2 | TRAIN_2025_JUL_AUG | CE | 3 | COMPLETE_POST_ENTRY_PATH | 18 |
| GROWW_2025_H2 | TRAIN_2025_JUL_AUG | PE | 2 | COMPLETE_POST_ENTRY_PATH | 13 |
| GROWW_2025_H2 | TRAIN_2025_JUL_AUG | PE | 3 | COMPLETE_POST_ENTRY_PATH | 13 |
| GROWW_2025_H2 | VALIDATION_2025_SEP_OCT | CE | 2 | COMPLETE_POST_ENTRY_PATH | 12 |
| GROWW_2025_H2 | VALIDATION_2025_SEP_OCT | CE | 2 | PARTIAL_POST_ENTRY_PATH | 1 |
| GROWW_2025_H2 | VALIDATION_2025_SEP_OCT | CE | 3 | COMPLETE_POST_ENTRY_PATH | 10 |
| GROWW_2025_H2 | VALIDATION_2025_SEP_OCT | CE | 3 | PARTIAL_POST_ENTRY_PATH | 1 |
| GROWW_2025_H2 | VALIDATION_2025_SEP_OCT | PE | 2 | COMPLETE_POST_ENTRY_PATH | 20 |
| GROWW_2025_H2 | VALIDATION_2025_SEP_OCT | PE | 3 | COMPLETE_POST_ENTRY_PATH | 20 |

Path status uses exact contract symbol, saved entry timestamp, and
five-minute continuity through the simulator's terminal point. A
complete path has the session candles needed for a same-day replay;
partial paths are not extended or interpolated. Any no-path or
invalid/mismatched entries remain unresolved or excluded and are not
counted as wins or losses.

## Integrity and limitations

* Duplicate saved entry observations beyond exact date/symbol/time keys:
  0.
* Duplicate resolved exit timestamps for the same date and contract:
  0.
* Overlapping resolved positions in the same contract/date:
  0. The equal-event
  sequence is not a capital-weighted portfolio simulation.
* The saved historical entry ledger contains qualifying entries, not
  every rejected pre-entry setup; skipped-setup counts cannot be inferred.
* A recovered 2026 candle path validates a price path for the saved
  contract and timestamp; it does not independently re-run and verify
  every historical entry decision.
* All option data are OHLC bars. OHLC cannot establish intrabar order
  or executable limit fills, and partial data can conceal excursions.
* Fees, taxes, spread, slippage, lot multipliers and account sizing are
  not configured as reliable historical inputs. Gross premium points
  are not rupee returns.
* Previously inspected 2025 test outcomes and archived 2026 policy
  summaries make these candidate comparisons retrospective, not a
  genuinely untouched out-of-sample selection.

The complete B2 row-level replay and cost sensitivity are in
`EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md` and
`ekalayava_guide9_b2_trailing_proxy_trade_audit.csv`.
