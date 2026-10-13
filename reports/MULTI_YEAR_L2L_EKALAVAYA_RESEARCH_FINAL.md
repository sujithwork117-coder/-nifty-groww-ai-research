# Multi-Year L2L and Ekalayava Research — Final

**Run date:** 2026-10-12
**Scope requested:** 2025-07-01–2025-12-31 and 2026-01-01–2026-09-29, Asia/Kolkata.
**Data actually tested:** 2026-01-01–2026-09-29 only. No 2025 H2 data was available locally.
**Mode:** offline historical research; gross premium points; no live orders or observer.

> **Follow-up:** This report records the inventory available on its run date.
> The requested 2025 H2 history was subsequently retrieved through the
> bounded Groww process and evaluated. Its prior “unavailable/not tested”
> statements are superseded by
> [EKALAYAVA_HISTORICAL_DATA_COVERAGE_JUL_DEC_2025.md](./EKALAYAVA_HISTORICAL_DATA_COVERAGE_JUL_DEC_2025.md)
> and [EKALAYAVA_MULTI_PERIOD_EXIT_VALIDATION.md](./EKALAYAVA_MULTI_PERIOD_EXIT_VALIDATION.md).

## Executive findings

- **2025 H2 was unavailable.** Local inventory and saved caches contained 2026 data only. Groww's documented 5-minute history endpoint is limited to recent history (roughly three months plus request constraints), so 2025 H2 is outside the documented range ([Python SDK docs](https://groww.in/trade-api/docs/python-sdk/historical-data); [cURL docs](https://groww.in/trade-api/docs/curl/historical-data)). No unsupported retrieval was retried and no other provider, expiry, strike, or fabricated bar was substituted. 2022–2024 were not requested or tested.
- **L2L canonical baseline reproduced** from the saved corrected ledger: 361 setups; 203 valid entries; 57 targets, 145 stop-outs, one ambiguous trade, and 158 skips (157 stop-breached at entry, one target already reached at entry); +237.45 gross premium points; PF 1.166; maximum chronological drawdown 250.05 points; longest loss streak 23. The event replay had zero baseline outcome mismatches. One entry at/above target is excluded from valid entry metrics below.
- **L2L candidate screen:** SL2, TP50, and SL4+TP50 were selected using Jan–Jun only and did not pass the existing Jul–Aug validation standard. No candidate is supported for canonical adoption.
- **Ekalayava exit research was executed** on the same 253 saved causal entries. 36 fixed structural/opening-low stop × target combinations (3 anchors × 3 buffers × 4 targets), plus one separately evaluated trailing policy, produced 9,361 trade-policy records. Three candidates passed the limited Jul–Aug numeric screen, but all three had negative gross results in September's incomplete 15-entry diagnostic; none is ready for adoption. The original Ekalayava specification and production behavior remain unchanged.
- These are **gross historical simulations**, not net profitability evidence. Fees, spread, slippage, sizing, and rupee returns are not modeled. 5-minute OHLC cannot resolve all intrabar ordering.

## 1. Scope, data and coverage

The report reuses the corrected exact-contract Jan–Sep 2026 dataset and existing saved event ledger. It performs no Groww calls or data downloads. The underlying/option universe was selected with the repository's daily catalog-first contract selection; no neighboring contracts were substituted.

| Requested period | Data tested | Availability / treatment |
|---|---|---|
| 2025-07-01–2025-12-31 | none | Not present locally; outside Groww's documented 5-minute history window. Not tested. |
| 2026-01-01–2026-09-29 | existing valid data | Tested; 2026-09-29 has missing late-session bars. |

Coverage figures below are adjusted to the requested end date (Sep 29). The existing canonical coverage manifest is scoped through Sep 30; that final day is excluded here because no underlying candles exist for it.

| Measure, 2026-01-01–2026-09-29 | Result |
|---|---:|
| Expected trading sessions | 184 |
| Underlying sessions with data | 184/184; 13,783/13,800 expected 5m bars (99.88%) |
| Expected option contract-days (4/day) | 736 |
| Complete / partial / missing or unselectable contract-days | 561 / 1 / 174 |
| Observed option candles | 42,149/55,200 expected (76.36%) |
| Fully usable / partially usable / unusable days | 112 / 55 / 17 |
| Missing option candle intervals | 13,276 |
| Specific partial contract-day | 2026-02-03 PE ITM3: 74/75 bars |
| Sep 29 underlying tail | 17 expected bars absent, from 14:05 to 15:25 |

A day with missing option data may hide a setup or prevent establishing the full post-entry path. Missing slots are not treated as no-signal observations. Results describe signals found in the validated saved ledger, not the unobserved opportunities on missing contract-days. The exact requested-scope manifest is [`multi_year_final_scope_coverage.json`](multi_year_final_scope_coverage.json); month-level and exact-slot detail remain in [`multi_year_data_coverage.json`](multi_year_data_coverage.json).

## 2. Canonical L2L baseline and entry quality

The canonical entry remains unchanged: completed 5-minute opening candle; completed red candle breaks Opening Low; enter at the close of the first subsequent completed green candle, within the canonical entry window. Canonical stop is Opening Low −4 premium points and target is Opening High.

| Metric | Jan 1–Sep 29, 2026 |
|---|---:|
| Setups | 361 |
| Entered / skipped | 203 / 158 |
| Target / SL / ambiguous / unresolved | 57 / 145 / 1 / 0 |
| Gross premium points | +237.45 |
| Expectancy per resolved trade / eligible setup | +1.18 / +0.66 |
| Profit factor | 1.166 |
| Mean / median winner | +29.25 / +27.35 |
| Mean / median loser | −9.86 / −8.05 |
| MFE mean / median; MAE mean / median | +18.22 / +12.05; −12.88 / −10.75 |
| Mean / median holding time | 21.66 / 10 min |
| Maximum drawdown / longest losing streak | 250.05 points / 23 |

An existing ledger defect was corrected for this entry-quality summary only: on Jan 1 a PE ITM2 entry at 129.10 was already above its Opening High target of 126.50, but its source label was `TARGET`. It is classified as `SKIPPED_TARGET_ALREADY_REACHED` and excluded from the 203 entries and 57 targets, consistent with the corrected simulator and paper engine. The canonical strategy was not changed.

### Entry-quality observations

- **194/203 (95.6%)** had the first completed post-entry candle's low below entry. This is descriptive; it does not establish a useful filter.
- Average opening range was 47.14 premium points; median distance from entry to Opening High was 36.55 points. Mean pre-entry rebound from the observed trough to entry was 17.43 points.
- Valid entry outcome counts by side: CE 26 targets / 78 stops among 105 entries; PE 31 / 67 among 98. By rank: ITM2 26 / 75 among 101; ITM3 31 / 70 among 102. One ambiguous trade is included in entry total but not those target/stop counts.
- By entry time: 09:15–09:59 had 153 entries (39 target, 114 SL); 10:00–10:59 had 49 (18 target, 30 SL); one entry at 11:00 was an SL. The 10:00–10:59 group had a larger average MFE (28.63) than the early group (14.94), but groups differ in size and month composition.
- Monthly target/SL counts for valid entries: Jan 10/21 (one ambiguous in addition); Feb 6/9; Mar 2/14; Apr 4/15; May 14/14; Jun 5/33; Jul 3/22; Aug 9/7; Sep 4/10. Monthly gross baseline points in the existing validated report are Jan +49.95, Feb +41.60, Mar −92.35, Apr −65.65, May +298.00, Jun −96.70, Jul −64.70, Aug +146.10, Sep +21.20. May's +298.00 exceeds the full-period +237.45, so the aggregate is concentrated in a small number of months.
- Stop forensics: 73/145 stop-outs had positive pre-stop MFE; median pre-stop MFE was 0.55; 48 reached ≥25%, 22 ≥50%, 8 ≥75%, and none reached 100% of original target distance before the stop. 72 stops occurred in the first post-entry candle; 67 later touched the target after the original stop. Those later touches do not turn stopped trades into winners.

Detailed entry-level fields and subgroup summaries are in [`multi_year_l2l_entry_quality.csv`](multi_year_l2l_entry_quality.csv) and [`multi_year_l2l_entry_quality_summary.csv`](multi_year_l2l_entry_quality_summary.csv). Baseline and stop-forensics evidence are in the existing [`multi_year_baseline_metrics.csv`](multi_year_baseline_metrics.csv), [`multi_year_l2l_stop_loss_forensics.csv`](multi_year_l2l_stop_loss_forensics.csv), and [`multi_year_l2l_stop_loss_summary.csv`](multi_year_l2l_stop_loss_summary.csv).

## 3. L2L stop, target and combined policy research

The existing bounded experiments were reused: SL2/SL4/SL6; TP100 (Opening High), TP75, TP50 and TP25; and all 12 combinations. Entry signals were held constant. Stop and target outcomes use completed bars; same-candle barrier collisions are ambiguous. Full tables are preserved in the existing trade-level and summary CSVs.

| Experiment | Jan–Jun development result | Jul–Aug validation vs canonical baseline | Decision |
|---|---|---|---|
| Independent stop: SL2 selected on training | +48.30 gross; +0.180/setup | +0.317/setup vs baseline +1.131; drawdown 80.80 vs 74.50 | Rejected |
| Independent target: TP50 selected on training | +221.63; +0.824/setup | +0.495/setup vs baseline +1.131 | Rejected |
| Combined: SL4+TP50 selected on training | +221.63; +0.824/setup | +0.495/setup vs baseline +1.131 | Rejected |

The selected alternatives failed the pre-existing chronological validation criteria; September was inspected and remains incomplete, not an untouched holdout. The policy grids contain trade counts, ambiguous/skipped outcomes, expectancy, PF, drawdown, loss streak, holding, monthly, CE/PE, ITM rank, and entry-time slices. No alternative is recommended. Keep canonical SL4/Opening High unchanged.

## 4. Ekalayava experimental stop and exit research

### Entry population and experiment design

The existing causal Ekalayava entry ledger was reused without changing entry logic: **253 entries** (126 CE, 127 PE; 128 ITM2, 125 ITM3). The original spec has no approved stop/exit lifecycle; the following policies are explicit experiments only. They do not redefine canonical Ekalayava.

Three anchors were tested with 0, 2 and 4 premium-point buffers, crossed with targets at 100%, 75%, 50%, and 25% of the entry-to-Opening-High distance: **36 policies × 253 entries = 9,108 rows**. A separate trailing candidate adds 253 rows, for **9,361 total**. C aliases A because the stored causal recovery/base evidence has no distinct base-invalidation boundary; repeating it would be a duplicate.

- **A — structural trough:** minimum option-premium low from the first completed Opening-Low breakdown through the completed bar immediately before the breakout; stop = trough − buffer.
- **B — breakout candle:** completed breakout-candle low − buffer; active after entry close.
- **C — recovery/base invalidation:** same recorded trough as A; no separate boundary exists in the saved causal event schema, so C is documented as equivalent and not redundantly simulated.
- **D — opening-range reference:** option premium Opening Low − buffer.
- **Targets:** `entry + fraction × (Opening High − entry)` for fractions 1.00, 0.75, 0.50, 0.25. Invalid target/stop entries are excluded for that policy.
- **Execution:** only bars strictly after the completed entry candle are considered. If a bar opens at/below active stop, fill at open (conservative gap-through-stop); otherwise intrabar stop touch fills at stop. A target touch fills at target. If stop and target both lie within one candle and the open does not establish order, classify ambiguous. If no barrier is touched, exit at the 15:25 candle close only when the path is complete; otherwise unresolved. No missing candle is filled.
- **Trailing candidate:** A stop with 2-point buffer; after a completed post-entry candle makes a lower low than the prior two completed candles, tighten to `max(old stop, current low −2)`. Updated level becomes active on the next candle. Target remains Opening High.

A stop's anchor low is chosen solely from information available by entry time. The fixed-policy OHLC results are candle-level theoretical fills; a real fill may differ, especially on gaps and intrabar ambiguity.

### Candidate outcomes by chronological period

| Selected family/policy | Period | Targets / stops / EOD / ambiguous / excluded | Gross points | Points/eligible | PF | Max DD | Loss streak | Median hold |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `A_STRUCTURAL_TROUGH_B0_TP100_OPENING_HIGH` | TRAIN_JAN_JUN | 67 / 114 / 10 / 0 / 0 | 1001.70 | 5.24 | 1.34 | 513.25 | 23 | 35.00m |
| `A_STRUCTURAL_TROUGH_B0_TP100_OPENING_HIGH` | VALIDATION_JUL_AUG | 18 / 24 / 5 / 0 / 0 | 213.00 | 4.53 | 1.47 | 212.90 | 8 | 55.00m |
| `A_STRUCTURAL_TROUGH_B0_TP100_OPENING_HIGH` | OOS_SEP_INCOMPLETE | 2 / 13 / 0 / 0 / 0 | -155.35 | -10.36 | 0.33 | 203.95 | 11 | 50.00m |
| `B_BREAKOUT_CANDLE_B2_TP100_OPENING_HIGH` | TRAIN_JAN_JUN | 51 / 135 / 5 / 0 / 0 | 1142.40 | 5.98 | 1.58 | 306.30 | 25 | 15.00m |
| `B_BREAKOUT_CANDLE_B2_TP100_OPENING_HIGH` | VALIDATION_JUL_AUG | 13 / 33 / 1 / 0 / 0 | 114.70 | 2.44 | 1.34 | 151.20 | 10 | 20.00m |
| `B_BREAKOUT_CANDLE_B2_TP100_OPENING_HIGH` | OOS_SEP_INCOMPLETE | 1 / 14 / 0 / 0 / 0 | -111.40 | -7.43 | 0.30 | 160.00 | 14 | 25.00m |
| `D_OPENING_LOW_B0_TP25` | TRAIN_JAN_JUN | 47 / 29 / 0 / 1 / 114 | -82.34 | -0.43 | 0.80 | 142.60 | 6 | 5.00m |
| `D_OPENING_LOW_B0_TP25` | VALIDATION_JUL_AUG | 12 / 9 / 0 / 0 / 26 | -67.65 | -1.44 | 0.45 | 101.94 | 4 | 5.00m |
| `D_OPENING_LOW_B0_TP25` | OOS_SEP_INCOMPLETE | 6 / 2 / 0 / 0 / 7 | 7.55 | 0.50 | 1.25 | 26.25 | 1 | 10.00m |
| `TRAIL_CAUSAL_LOWER_LOW_B2_TP100` | TRAIN_JAN_JUN | 45 / 144 / 2 / 0 / 0 | 143.55 | 0.75 | 1.06 | 542.95 | 17 | 25.00m |
| `TRAIL_CAUSAL_LOWER_LOW_B2_TP100` | VALIDATION_JUL_AUG | 11 / 36 / 0 / 0 / 0 | 19.40 | 0.41 | 1.06 | 198.35 | 8 | 45.00m |
| `TRAIL_CAUSAL_LOWER_LOW_B2_TP100` | OOS_SEP_INCOMPLETE | 1 / 13 / 1 / 0 / 0 | -83.90 | -5.59 | 0.42 | 135.10 | 10 | 20.00m |

The Jan–Jun family selection maximized gross points per eligible entry within each pre-defined family, with drawdown and loss streak used as tie-breaks. Jul–Aug validation required at least 25 entries, positive gross points per eligible entry, PF above 1, at least 90% resolved valid entries, and <10% ambiguity. A, B, and trailing passed that limited screen; D did not. No candidate was selected from validation or September.

The September diagnostic contains only 15 entries because coverage ends early and is incomplete. Selected A, B, and trailing candidates respectively returned **−155.35, −111.40, and −83.90 gross points** (−10.36, −7.43, −5.59 per entry) with PF **0.327, 0.304, 0.423**. Thus passing the small Jul–Aug screen is not enough to support adoption; their later diagnostic is sharply negative and sample-limited. The A and B families also have large training drawdowns (513.25 and 306.30 points) and loss streaks (23 and 25). The trailing rule's training drawdown is 542.95. No exit policy is robustly supported.

### Policy-grid results

#### A — structural trough

| Policy | Tgt / SL / EOD / ambiguous / excluded | Gross pts | Pts/eligible | PF | Mean stop / target distance | Max DD | Loss streak | Median hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `A_STRUCTURAL_TROUGH_B0_TP100_OPENING_HIGH` | 87 / 151 / 15 / 0 / 0 | 1059.35 | 4.19 | 1.29 | 28.23 / 61.10 | 513.25 | 23 | 40.00m |
| `A_STRUCTURAL_TROUGH_B0_TP25` | 152 / 100 / 1 / 0 / 0 | -87.51 | -0.35 | 0.96 | 28.23 / 15.27 | 533.91 | 9 | 15.00m |
| `A_STRUCTURAL_TROUGH_B0_TP50` | 114 / 135 / 4 / 0 / 0 | 146.57 | 0.58 | 1.05 | 28.23 / 30.55 | 511.50 | 10 | 25.00m |
| `A_STRUCTURAL_TROUGH_B0_TP75` | 95 / 146 / 12 / 0 / 0 | 379.32 | 1.50 | 1.11 | 28.23 / 45.82 | 513.61 | 23 | 30.00m |
| `A_STRUCTURAL_TROUGH_B2_TP100_OPENING_HIGH` | 89 / 145 / 19 / 0 / 0 | 919.50 | 3.63 | 1.24 | 30.23 / 61.10 | 558.00 | 23 | 45.00m |
| `A_STRUCTURAL_TROUGH_B2_TP25` | 155 / 96 / 2 / 0 / 0 | -176.80 | -0.70 | 0.92 | 30.23 / 15.27 | 639.24 | 9 | 15.00m |
| `A_STRUCTURAL_TROUGH_B2_TP50` | 117 / 129 / 7 / 0 / 0 | 25.70 | 0.10 | 1.01 | 30.23 / 30.55 | 597.55 | 10 | 30.00m |
| `A_STRUCTURAL_TROUGH_B2_TP75` | 98 / 140 / 15 / 0 / 0 | 257.46 | 1.02 | 1.07 | 30.23 / 45.82 | 556.36 | 23 | 40.00m |
| `A_STRUCTURAL_TROUGH_B4_TP100_OPENING_HIGH` | 91 / 141 / 21 / 0 / 0 | 780.80 | 3.09 | 1.19 | 32.23 / 61.10 | 601.15 | 23 | 50.00m |
| `A_STRUCTURAL_TROUGH_B4_TP25` | 157 / 93 / 3 / 0 / 0 | -272.90 | -1.08 | 0.88 | 32.23 / 15.27 | 732.09 | 9 | 15.00m |
| `A_STRUCTURAL_TROUGH_B4_TP50` | 119 / 125 / 9 / 0 / 0 | -107.45 | -0.42 | 0.97 | 32.23 / 30.55 | 602.53 | 10 | 35.00m |
| `A_STRUCTURAL_TROUGH_B4_TP75` | 99 / 137 / 17 / 0 / 0 | 69.71 | 0.28 | 1.02 | 32.23 / 45.82 | 597.51 | 23 | 45.00m |

#### B — breakout-candle low

| Policy | Tgt / SL / EOD / ambiguous / excluded | Gross pts | Pts/eligible | PF | Mean stop / target distance | Max DD | Loss streak | Median hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `B_BREAKOUT_CANDLE_B0_TP100_OPENING_HIGH` | 58 / 189 / 6 / 0 / 0 | 1006.65 | 3.98 | 1.46 | 13.53 / 61.10 | 256.30 | 25 | 15.00m |
| `B_BREAKOUT_CANDLE_B0_TP25` | 110 / 137 / 1 / 5 / 0 | 38.37 | 0.15 | 1.03 | 13.53 / 15.27 | 183.56 | 12 | 10.00m |
| `B_BREAKOUT_CANDLE_B0_TP50` | 79 / 171 / 1 / 2 / 0 | 343.75 | 1.36 | 1.18 | 13.53 / 30.55 | 250.97 | 14 | 10.00m |
| `B_BREAKOUT_CANDLE_B0_TP75` | 63 / 185 / 5 / 0 / 0 | 509.60 | 2.01 | 1.24 | 13.53 / 45.82 | 259.00 | 25 | 15.00m |
| `B_BREAKOUT_CANDLE_B2_TP100_OPENING_HIGH` | 65 / 182 / 6 / 0 / 0 | 1145.70 | 4.53 | 1.46 | 15.53 / 61.10 | 306.30 | 25 | 20.00m |
| `B_BREAKOUT_CANDLE_B2_TP25` | 120 / 129 / 1 / 3 / 0 | -5.64 | -0.02 | 1.00 | 15.53 / 15.27 | 266.04 | 9 | 10.00m |
| `B_BREAKOUT_CANDLE_B2_TP50` | 88 / 164 / 1 / 0 / 0 | 322.27 | 1.27 | 1.15 | 15.53 / 30.55 | 347.55 | 13 | 15.00m |
| `B_BREAKOUT_CANDLE_B2_TP75` | 70 / 178 / 5 / 0 / 0 | 546.65 | 2.16 | 1.23 | 15.53 / 45.82 | 321.65 | 25 | 15.00m |
| `B_BREAKOUT_CANDLE_B4_TP100_OPENING_HIGH` | 71 / 173 / 9 / 0 / 0 | 1113.20 | 4.40 | 1.41 | 17.53 / 61.10 | 320.50 | 23 | 25.00m |
| `B_BREAKOUT_CANDLE_B4_TP25` | 131 / 118 / 2 / 2 / 0 | -10.69 | -0.04 | 0.99 | 17.53 / 15.27 | 302.71 | 9 | 10.00m |
| `B_BREAKOUT_CANDLE_B4_TP50` | 95 / 156 / 2 / 0 / 0 | 230.82 | 0.91 | 1.10 | 17.53 / 30.55 | 437.75 | 13 | 15.00m |
| `B_BREAKOUT_CANDLE_B4_TP75` | 77 / 168 / 8 / 0 / 0 | 529.75 | 2.09 | 1.20 | 17.53 / 45.82 | 405.05 | 23 | 20.00m |

#### D — Opening Low comparison

| Policy | Tgt / SL / EOD / ambiguous / excluded | Gross pts | Pts/eligible | PF | Mean stop / target distance | Max DD | Loss streak | Median hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `D_OPENING_LOW_B0_TP100_OPENING_HIGH` | 37 / 69 / 0 / 0 / 147 | -278.55 | -1.10 | 0.75 | 21.82 / 61.10 | 316.40 | 9 | 10.00m |
| `D_OPENING_LOW_B0_TP25` | 65 / 40 / 0 / 1 / 147 | -142.44 | -0.56 | 0.75 | 21.82 / 15.27 | 184.28 | 6 | 5.00m |
| `D_OPENING_LOW_B0_TP50` | 49 / 56 / 0 / 1 / 147 | -273.28 | -1.08 | 0.69 | 21.82 / 30.55 | 273.28 | 7 | 10.00m |
| `D_OPENING_LOW_B0_TP75` | 42 / 64 / 0 / 0 / 147 | -308.38 | -1.22 | 0.71 | 21.82 / 45.82 | 309.14 | 8 | 10.00m |
| `D_OPENING_LOW_B2_TP100_OPENING_HIGH` | 37 / 73 / 0 / 0 / 143 | -418.95 | -1.66 | 0.67 | 22.99 / 61.10 | 418.95 | 11 | 10.00m |
| `D_OPENING_LOW_B2_TP25` | 65 / 44 / 0 / 1 / 143 | -224.84 | -0.89 | 0.65 | 22.99 / 15.27 | 258.19 | 6 | 5.00m |
| `D_OPENING_LOW_B2_TP50` | 49 / 60 / 0 / 1 / 143 | -387.68 | -1.53 | 0.61 | 22.99 / 30.55 | 387.68 | 7 | 10.00m |
| `D_OPENING_LOW_B2_TP75` | 42 / 68 / 0 / 0 / 143 | -438.78 | -1.73 | 0.63 | 22.99 / 45.82 | 438.78 | 10 | 10.00m |
| `D_OPENING_LOW_B4_TP100_OPENING_HIGH` | 39 / 74 / 0 / 0 / 140 | -486.45 | -1.92 | 0.64 | 24.36 / 61.10 | 486.45 | 12 | 15.00m |
| `D_OPENING_LOW_B4_TP25` | 67 / 46 / 0 / 0 / 140 | -275.91 | -1.09 | 0.61 | 24.36 / 15.27 | 304.16 | 4 | 5.00m |
| `D_OPENING_LOW_B4_TP50` | 51 / 62 / 0 / 0 / 140 | -474.85 | -1.88 | 0.57 | 24.36 / 30.55 | 474.85 | 8 | 10.00m |
| `D_OPENING_LOW_B4_TP75` | 44 / 69 / 0 / 0 / 140 | -508.21 | -2.01 | 0.61 | 24.36 / 45.82 | 508.21 | 11 | 10.00m |

The one separate trailing candidate produced, over all 253 entries: 57 targets, 193 stops, 3 end-of-session exits, no ambiguity or unresolved outcomes, +79.05 gross points, +0.31 per eligible entry, PF 1.028, maximum drawdown 660.90 and longest loss streak 17. Its Jul–Aug result was +19.40 (+0.41/entry; PF 1.056), then September was −83.90. Trailing did not establish robust improvement.

### Ekalayava subgroup observations

For the selected A0/TP100 policy, full-period CE/PE outcomes were CE 43 target / 75 stop / 8 EOD (gross +632.35) and PE 44 / 76 / 7 (gross +427.00); ITM2 43 / 76 / 9 (+476.95) and ITM3 44 / 75 / 6 (+582.40). Its entry buckets were 09:15–09:59: 26 / 36 / 0 (−572.40); 10:00–10:59: 37 / 73 / 4 (−256.45); and 11:00 onward: 24 / 42 / 11 (+1,888.20). The late-time gross concentration is highly consequential and requires audit against entry-time distribution, missing coverage and chronology; it should not be turned into a filter from this sample. Month and subgroup metrics for all policies are in the policy summary CSV.

All 253 entries had measured post-entry OHLC sufficient for these policy paths under A/B. D excluded 140–147 of 253 entries per policy because the Opening Low-based stop was not below the entry; this is a substantial policy limitation, and excluded entries remain in the eligible-entry denominator. Across the whole grid there were 16 same-bar ambiguities in breakout-candle policies, no unresolved rows, and exclusions were explicitly recorded. This does not remove the general missing-data bias: the ledger cannot include signals hidden by missing contracts or absent candles.

## 5. Chronological validation, interpretation and recommendation

- **Development:** Jan–Jun 2026; 191 Ekalayava entries and 148 valid L2L entries in the corrected L2L entry-quality population.
- **Validation:** Jul–Aug 2026; 47 Ekalayava entries and 41 valid L2L entries. These are adjacent periods within one calendar year, not independent yearly replications.
- **Later-period diagnostic:** September 2026; 15 Ekalayava entries and 14 L2L entries, with incomplete data. September had prior exposure in related target research; it is not an untouched holdout.
- **2025 chronological development/validation:** impossible with the available permitted dataset. No 2025 result is claimed.

**L2L decision:** retain canonical entry, SL4 and Opening High. Existing SL2, TP50 and combined candidate validations failed; no entry filter is proposed from the 95.6% first-candle adverse observation alone.

**Ekalayava decision:** the requested experimental lifecycle research has been executed, but **no experimental stop/exit is ready for adoption**. A0/TP100, B2/TP100 and trailing passed a limited two-month numeric screen but failed the September diagnostic and show high drawdown/loss streak exposure. The original canonical Ekalayava lifecycle remains unresolved; this report does not authorize live/paper exit execution or represent target touches as P&L. Any lifecycle change still requires owner review and separate specification/versioning before it is used operationally.

**Next research:** secure provenance-verifiable historical 5-minute NIFTY underlying plus exact daily options for a genuinely independent period, preferably the unavailable 2025 H2 if a compliant source can provide it; pre-register a new chronological evaluation before candidate review. In parallel, review the Ekalayava candidate loss paths and execution assumptions with an owner, then approve or reject an explicitly versioned lifecycle before any observer can use it. Do not repeat this grid absent new data or a specified research question.

## 6. Reproducibility and safety

This work used the saved baseline ledger and cached exact option candles; it did not download data, call Groww, start an observer, or place orders. No canonical strategy definition or production strategy code was changed. Experimental exit code is isolated in [`app/research_ekalayava_exits.py`](../app/research_ekalayava_exits.py) and [`tools/run_ekalayava_exit_research.py`](../tools/run_ekalayava_exit_research.py). `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`.

### Main machine-readable outputs

- Coverage and gaps: [`multi_year_final_scope_coverage.json`](multi_year_final_scope_coverage.json), [`multi_year_data_coverage.json`](multi_year_data_coverage.json), [`multi_year_research_config.json`](multi_year_research_config.json).
- Canonical baseline, period and candidate evidence: [`multi_year_baseline_metrics.csv`](multi_year_baseline_metrics.csv), [`multi_year_period_metrics.csv`](multi_year_period_metrics.csv), [`multi_year_candidate_selection.json`](multi_year_candidate_selection.json).
- L2L entry quality and stop forensics: [`multi_year_l2l_entry_quality.csv`](multi_year_l2l_entry_quality.csv), [`multi_year_l2l_entry_quality_summary.csv`](multi_year_l2l_entry_quality_summary.csv), [`multi_year_l2l_stop_loss_forensics.csv`](multi_year_l2l_stop_loss_forensics.csv), [`multi_year_l2l_stop_loss_summary.csv`](multi_year_l2l_stop_loss_summary.csv).
- L2L policy matrices: `multi_year_l2l_stop_policy_{trades,summary}.csv`, `multi_year_l2l_target_policy_{trades,summary}.csv`, `multi_year_l2l_combined_sl_tp_{trades,summary}.csv`.
- Ekalayava entry observations: `multi_year_ekalayava_{observations,summary}.csv`.
- Ekalayava exit policies, trade outcomes and period selection: [`ekalayava_exit_policy_trades.csv`](ekalayava_exit_policy_trades.csv), [`ekalayava_exit_policy_summary.csv`](ekalayava_exit_policy_summary.csv), [`ekalayava_exit_candidate_selection.json`](ekalayava_exit_candidate_selection.json).
- Prior full L2L policy and validation narrative remains in [`MULTI_YEAR_STRATEGY_OPTIMIZATION_FINAL.md`](MULTI_YEAR_STRATEGY_OPTIMIZATION_FINAL.md); this report adds the executed Ekalayava lifecycle grid and corrected entry-quality analysis without replacing it.
