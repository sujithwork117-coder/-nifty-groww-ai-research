# Level-to-Level Final Validation — Jan–Sep 2026

**Window:** 2026-01-01 through 2026-09-30 requested; underlying source ends 2026-09-29. This validation reuses the corrected baseline and existing timing ledger. No market data was downloaded and the strategy entry rule was not changed.

## Final event accounting

| Measure | Result |
|---|---:|
| Setups | 361 |
| Resolved target/SL outcomes | 202 |
| Opening High targets | 57 |
| Stop losses | 145 |
| Skipped at/below SL | 157 |
| Skipped because entry was already at/above target | 1 |
| Ambiguous same-bar SL/target | 1 |
| Target share of target/SL-resolved trades | 57/202 (28.2%) |
| Gross premium points on resolved trades | +237.45 |
| Mean / median resolved trade | +1.18 / −4.53 points |
| Average / median target outcome | +29.25 / +27.35 points |
| Average / median SL outcome | −9.86 / −8.05 points |
| Mean / median MFE, resolved | +18.22 / +11.93 points |
| Mean / median MAE, resolved | −12.82 / −10.70 points |
| Mean / median holding time, resolved | 21.66 / 10 minutes |
| Maximum drawdown, equal-unit resolved-event sequence | 250.05 points |
| Longest target / SL streak | 4 / 23 |

Premium-point totals are not rupee/account returns. Position size, fees, spread, slippage, and capital are not modeled. Missing option contracts may suppress setups and outcomes.

## Entry-at/above-target edge case

One 2026-01-01 PE ITM2 event entered at 129.10 while the Opening High target was 126.50. The prior simulator later marked it `TARGET` because a later bar high was greater than 126.50. That is not an upward move to the target: the long entry was already above the target. This final validation treats it as `SKIPPED_TARGET_ALREADY_REACHED`, leaves points blank, and excludes it from resolved and target-hit rates. Removing its −2.60 recorded points changes the gross resolved sum from +234.85 to +237.45.

The backtest and stateful paper engine now both skip an entry whose completed close is at or above the target. The canonical target and entry sequence are unchanged. Earlier detailed reports remain preserved as source-history artifacts; this report and its JSON carry the explicit correction.

## Target timing after the completed entry close

The entry timestamp in source is the start of the completed green candle; entry occurs at its close. The target bar is later. OHLC supports a five-minute touch interval, not an exact intrabar time. The invalid entry-above-target case is excluded from the timing sample.

| First target bar window after entry | Hits | Cumulative |
|---|---:|---:|
| 0–5 min | 13 | 13 |
| 5–10 min | 11 | 24 |
| 10–15 min | 9 | 33 |
| 15–30 min | 5 | 38 |
| 30–60 min | 10 | 48 |
| 60–90 min | 8 | 56 |
| Later than 90 min | 1 | 57 |

The median time-to-target interval is **10–15 minutes**; the mean is bounded by **24.0–29.0 minutes**. The fastest valid target observation was in the first later candle (0–5 minutes); the latest was 110–115 minutes. Thus short-duration target moves occur, and a long tail remains. The data does not establish a 90-minute holding rule.

Two entry candles among the original 58 target-labelled rows had a high at/above Opening High. Those highs occurred before the entry close within the same candle, so they cannot be counted as post-entry target touches. The event above is separately skipped because its entry close was already above the target.

## Observed distributions

| Group | Setups | Targets | SL | Skipped | Gross resolved points | Target / resolved |
|---|---:|---:|---:|---:|---:|---:|
| CE | 185 | 26 | 78 | 80 | −16.60 | 25.0% |
| PE | 176 | 31 | 67 | 78 | +254.05 | 31.6% |
| ITM2 | 183 | 26 | 75 | 82 | −63.85 | 25.7% |
| ITM3 | 178 | 31 | 70 | 76 | +301.30 | 30.7% |

“Skipped” combines the 157 stop-already-breached entries and the one target-already-reached entry. The sole target-already-reached entry was PE ITM2.

| Month | Setups | Target | SL | Skipped | Ambiguous | Gross resolved points |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 55 | 10 | 21 | 23 | 1 | +49.95 |
| Feb | 49 | 6 | 9 | 34 | 0 | +41.60 |
| Mar | 26 | 2 | 14 | 10 | 0 | −92.35 |
| Apr | 36 | 4 | 15 | 17 | 0 | −65.65 |
| May | 52 | 14 | 14 | 24 | 0 | +298.00 |
| Jun | 51 | 5 | 33 | 13 | 0 | −96.70 |
| Jul | 34 | 3 | 22 | 9 | 0 | −64.70 |
| Aug | 38 | 9 | 7 | 22 | 0 | +146.10 |
| Sep* | 20 | 4 | 10 | 6 | 0 | +21.20 |

*September ends Sep 29 in available source data. May contributes +298.00 points, exceeding the +237.45 combined total; the total is therefore not broadly distributed across months. Monthly behavior is mixed and coverage is incomplete.

Entry-time result: 09:15–09:59 produced 39 targets / 114 SL / 132 skipped and −18.30 points; 10:00–10:59 produced 18 / 30 / 25 and +255.90; the two 11:00 setups produced no target, one SL and one skip, for −0.15 points. These are descriptive, sample- and coverage-dependent distributions, not a time filter recommendation.

## Canonical logic and causal checks

The entry remains: first completed 5-minute candle sets Opening High/Low; a completed red candle must break below Opening Low; enter at the close of the first subsequent completed green candle, within the configured 09:15–11:00 window. No second-green substitution, indicator, or future candle is used. The stateful paper engine consumes completed bars in order and prevents duplicate daily entries. Stops and targets are checked only on bars after the entry candle; a same-bar SL/target touch is ambiguous.

The canonical stop remains Opening Low minus the configured 4 premium points; target remains Opening High. The only implementation correction in this finalization is rejecting entries already at/above target instead of reporting a false target result.

## Data coverage and limits

The requested period contains 185 sessions; 184 have underlying source data. Underlying coverage is 13,783/13,875 regular bars (99.3%). Option coverage is 42,149/55,500 bars (75.9%) across 740 expected contract-days: 561 complete, 1 partial, and 178 missing/unselectable. There are 112 fully usable, 55 partially usable, and 18 unusable sessions. The 361 observed L2L setups include 290 on fully usable and 71 on partially usable dates; no setup was detected on unusable dates. Missing contracts may suppress otherwise possible setups.

## Readiness

**L2L: NOT READY for live paper observation.** Canonical historical behavior and stateful replay are covered, but a complete read-only Groww coordinator, exchange holiday/special-session calendar, four-stream feed orchestration, and real reconnect/recovery integration remain unwired. No live observer or order process was started. Safety remains `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`.

Machine-readable metrics and group tables: [`L2L_FINAL_VALIDATION.json`](L2L_FINAL_VALIDATION.json). Earlier timing ledger: [`l2l_target_timing_research.md`](l2l_target_timing_research.md).
