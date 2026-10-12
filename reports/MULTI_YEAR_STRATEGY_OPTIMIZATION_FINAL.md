# Multi-Year NIFTY L2L + Ekalayava Research and Policy Validation

**Run date:** 2026-10-13  
**Scope:** offline historical research using saved Groww-derived 5-minute data; no new market data was downloaded.  
**Recommendation:** **NO RELIABLE WINNER — MORE EVIDENCE REQUIRED.** Operationally retain the canonical baseline. No production rules or observer settings were changed.

## Executive summary

The repository contains suitable 5-minute market data only for 2026, from 2026-01-01 through 2026-09-29. There is no local 2022–2025 dataset. Groww's official historical-data documentation says 5-minute history is available for the last three months and limits a 5-minute request to 15 days, so those older years could not be retrieved within the supported documented path. No alternate provider or substitute contract was used. Thus this is a 2026-only bounded validation, not multi-year evidence.

The corrected L2L baseline was reproduced exactly: 361 setups; 57 target, 145 stop, 1 ambiguous, and 158 skipped; +237.45 gross premium points. The baseline result is highly dispersed: May contributed +298 points while March, April, and June were negative. The Jan–Jun training candidate rule selected SL2 independently, TP50 independently, and SL4+TP50 in the combined matrix. All three failed the predeclared Jul–Aug validation screen on gross points per setup; the stop-only candidate also failed the drawdown screen. September is an incomplete chronological check, not an untouched holdout, and it does not rescue a candidate.

All 253 Ekalayava entries remain unresolved under the canonical specification. The opening-high reference was touched in 109/253 observations (43.1%), but target touches are not wins or realized P&L. Mean/median MFE was +57.35/+31.05 points and MAE −53.27/−45.60. An approved stop anchor, buffer, and full exit lifecycle are still missing.

## 1. Data and periods actually tested

### Inventory and provenance

The authoritative cache is `data/derived/final_jan_sep_2026/assembled`: one NIFTY underlying file and 525 exact option-symbol files. A local snapshot inspected 1,755 CSVs across duplicate caches; the timestamp range was 2026-01-01 to 2026-09-29, and all local timestamped rows belonged to 2026. The duplicate-cache row count is not unique coverage. The run reused the saved corrected event ledger `data/derived/final_jan_sep_2026/final_baseline.json` (614 events: 361 L2L and 253 Ekalayava), and its existing validated selection/coverage artifacts.

No missing bars were filled and no neighboring strike/expiry was substituted. The saved universe is based on the exact daily catalog-first CE/PE ITM2/ITM3 contract selection. All results are gross premium points with equal-unit event sequencing; fees, spread, slippage, sizing, capital, and rupee returns are not modeled.

### Coverage

| Period | Expected sessions | Underlying coverage | Expected option contract-days | Complete | Partial | Missing/unselectable | Option bars |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022 | unavailable | no local data | — | — | — | — | — |
| 2023 | unavailable | no local data | — | — | — | — | — |
| 2024 | unavailable | no local data | — | — | — | — | — |
| 2025 | unavailable | no local data | — | — | — | — | — |
| 2026-01-01–2026-09-30 | 185 | 184 sessions; 13,783/13,875 bars (99.3%) | 740 | 561 | 1 | 178 | 42,149/55,500 (75.94%) |

There were 112 fully usable, 55 partially usable, and 18 unusable days; 13,351 expected option candle intervals are absent. The one partial contract-day is 2026-02-03 PE ITM3 (74/75). September's underlying is available through Sep 29 only; Sep 29 is missing 17 late bars (14:05–15:25), and Sep 30 has no underlying bars. September has 33/84 option slots complete, 51 missing/unselectable, and only 20/21 underlying sessions. The exact missing-slot manifest and month-level coverage are in `multi_year_data_coverage.json`.

Missing contracts and incomplete days may hide setups and may prevent classifying a later target, stop, or end-of-data path. The strategy event ledger contains only signals the existing replay could establish; absent data is not treated as a no-signal observation. September results are especially incomplete.

### Chronological split actually used

* **Development:** 2026-01-01–2026-06-30 (269 L2L setups).
* **Validation:** 2026-07-01–2026-08-31 (72 setups).
* **Chronological OOS diagnostic:** 2026-09-01–2026-09-30, underlying through Sep 29 (20 observed setups; incomplete coverage).

This is the only feasible chronological split in the available data. September was previously inspected in inherited target-policy research and is incomplete; it is not claimed as an untouched holdout. No 2022–2025 years were tested.

## 2. Canonical definitions and baseline reproduction

The L2L baseline keeps the canonical completed 5-minute opening range, completed red candle breaking Opening Low, first subsequent completed green candle close as entry, entry window through 11:00 IST, stop at Opening Low minus 4 premium points, and Opening High target. The event ledger and candle-level replay were compared. Baseline counts matched exactly with **zero outcome mismatches**.

| L2L baseline metric | Result |
|---|---:|
| Setups | 361 |
| Entered | 203 |
| Targets / SL / ambiguous / skipped / unresolved | 57 / 145 / 1 / 158 / 0 |
| Resolved | 202 (55.96% of setups) |
| Target hit rate among resolved | 28.22% |
| Gross points | +237.45 |
| Mean / median points per resolved trade | +1.18 / −4.53 |
| Mean / median winner | +29.25 / +27.35 |
| Mean / median loser | −9.86 / −8.05 |
| Profit factor | 1.166 |
| Maximum equal-unit chronological drawdown | 250.05 points |
| Longest loss streak | 23 |
| Mean / median holding time | 21.66 / 10 min |
| Resolved-trade MFE mean / median | +18.22 / +12.05 |
| Resolved-trade MAE mean / median | −12.88 / −10.75 |

### Baseline distribution

Monthly gross points Jan–Sep: **+49.95, +41.60, −92.35, −65.65, +298.00, −96.70, −64.70, +146.10, +21.20**. May alone exceeded the full-period total; January, February, May, August, and incomplete September were positive, while March, April, June, and July were negative. Gross points are not net returns and this concentration limits any aggregate interpretation.

Baseline resolved target/SL by contract side: CE 26/78 (104 resolved); PE 31/67 (98). By rank: ITM2 26/75 (101); ITM3 31/70 (101). Entry-time buckets: 09:15–09:59 had 285 setups, 132 resolved, 35 target and 97 SL; 10:00–10:59 had 74 setups, 69 resolved, 22 target and 47 SL; two setups at 11:00 had one resolved SL. Detail by month, CE/PE, rank, and entry bucket is in `multi_year_baseline_metrics.csv`.

The fixed 5-minute OHLC replay excludes the entry candle from post-entry outcomes. A candle that touches both stop and target is ambiguous; a missing interval before any touch leaves a path unresolved. Target and stop timestamps are candle-resolution times, not exact intrabar event ordering.

## 3. L2L stop-loss forensics

All 145 canonical stop paths were present and contiguous up to the stop; none had a pre-stop data gap. The stop candle's intrabar ordering remains unknown, so excursion calculations use only bars strictly before the stop candle.

| Pre-stop excursion measure (n=145) | Count / distribution |
|---|---:|
| Positive favorable excursion before stop | 73 (50.3%) |
| Zero favorable excursion | 72 (49.7%) |
| MFE mean / median / p75 / p90 | 8.50 / 0.55 / 13.20 / 22.41 points |
| Fraction of original target distance: mean / median / p75 / p90 | 20.3% / 1.6% / 38.7% / 58.7% |
| At least 25% / 50% / 75% of target distance before stop | 48 / 22 / 8 |
| At least 100% before stop | 0 |
| MFE below 25% of target distance | 97 |
| First post-entry candle moved below entry | 140 |
| Stop detected in first post-entry candle | 72 |

Start-to-start entry-candle/stop-candle distance had median 10 min, mean 18.76, p75 20, p90 43. Because entry is at the completed entry candle close, the stop-touch elapsed bound is 0–5 minutes for the first post-entry bar; across all 145, median lower/upper bounds are 5/10 minutes. Precise stop time is not observable from 5-minute OHLC. After a stop, 67 paths later touched Opening High, while 78 complete observed paths did not; post-stop recovery is not a valid recovery of the stopped trade.

Excursions differed by month and are fully tabulated in `multi_year_l2l_stop_loss_summary.csv`. Examples: 11/14 May stop paths had positive pre-stop MFE, compared with 3/14 in February and 6/21 in January. Those small monthly groups and one-year coverage are descriptive only. The excursion evidence motivates controlled stop research but does not imply that a wider stop is preferable.

## 4. Independent L2L stop comparison

The entry signals and Opening High target were fixed. Candidate stops are Opening Low minus 2, 4, or 6 premium points. No SL3 price-action/volatility policy was added: the current saved research specification did not establish a single validated causal formula for one, and adding an arbitrary rule would violate the bounded experiment.

| Stop | Target / SL / ambiguous / skipped | Target rate resolved | Gross points | Mean points/setup | PF | Max DD | Loss streak | Median hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SL2 | 46 / 132 / 1 / 182 | 25.84% | +7.80 | +0.02 | 1.007 | 215.90 | 18 | 10 min |
| SL4 canonical | 57 / 145 / 1 / 158 | 28.22% | +237.45 | +0.66 | 1.166 | 250.05 | 23 | 10 min |
| SL6 | 61 / 174 / 1 / 125 | 25.96% | +76.75 | +0.21 | 1.044 | 375.60 | 28 | 10 min |

The narrower stop lowers drawdown and loss streak in the aggregate but also produces fewer resolved setups and nearly flat total gross points. The wider stop has the largest maximum drawdown and longest loss streak. Across development/validation/incomplete September, the all-period total obscures instability: SL2 gross +48.30 / +22.80 / −63.30; SL4 +134.85 / +81.40 / +21.20; SL6 −52.30 / +130.95 / −1.90. SL2 was selected from alternatives using Jan–Jun only, then rejected in Jul–Aug: its +0.317 gross points/setup did not exceed baseline +1.131, and DD 80.80 exceeded baseline 74.50. No independent stop candidate survives the predeclared screen.

Year/month, CE/PE, rank and time breakdowns for all stop candidates are included in `multi_year_l2l_stop_policy_summary.csv` and `multi_year_period_metrics.csv`.

## 5. Independent L2L target comparison

The canonical 4-point stop and entries were fixed. Alternative thresholds were computed as `entry + fraction × (Opening High − entry)` for 75%, 50%, and 25%; invalid already-passed targets remain skipped. The table reports resolved target/SL/ambiguous/skipped counts, gross points, and the all-setup denominator for expectancy.

| Target | Target / SL / ambiguous / skipped | Target rate resolved | Gross points | Mean points/setup | PF | Max DD | Loss streak | Median hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Opening High (baseline) | 57 / 145 / 1 / 158 | 28.22% | +237.45 | +0.66 | 1.166 | 250.05 | 23 | 10 min |
| 75% distance | 65 / 136 / 2 / 158 | 32.34% | +152.75 | +0.42 | 1.115 | 259.18 | 17 | 10 min |
| 50% distance | 79 / 122 / 2 / 158 | 39.30% | +254.65 | +0.71 | 1.237 | 250.43 | 17 | 5 min |
| 25% distance | 105 / 85 / 13 / 158 | 55.26% | +205.68 | +0.57 | 1.299 | 132.93 | 7 | 5 min |

The 25% target has the highest hit rate and lower drawdown, but 13 same-bar ambiguous outcomes and a lower gross total than the 50% candidate; higher hit rate alone does not settle the comparison. TP50 was selected on Jan–Jun only, where it produced +221.63 and +0.824 points/setup. In validation it produced +35.65, +0.495/setup versus baseline +1.131/setup, so it was rejected. In incomplete September it was −2.63 points. TP25 validation was +34.85 (+0.484/setup), below baseline; incomplete September was −20.76. Target results are gross and do not account for costs.

## 6. Combined stop/target matrix

All 12 predefined combinations were evaluated on the same saved entry signals, with each candidate's own stop and target replayed in chronological completed bars. Counts below are full-period; DD is on the equal-unit sequence of resolved outcomes. `TP100` is Opening High; TP75/50/25 are fractions of entry-to-Opening-High distance.

| Policy | Target / SL / ambiguous / skipped | Target rate resolved | Gross points | Mean/setup | PF | Max DD | Loss streak | Median hold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SL2 + TP100 | 46 / 132 / 1 / 182 | 25.84% | +7.80 | +0.02 | 1.007 | 215.90 | 18 | 10m |
| SL2 + TP75 | 54 / 123 / 2 / 182 | 30.51% | +21.70 | +0.06 | 1.020 | 223.31 | 14 | 10m |
| SL2 + TP50 | 68 / 108 / 3 / 182 | 38.64% | +192.50 | +0.53 | 1.212 | 237.58 | 14 | 5m |
| SL2 + TP25 | 89 / 69 / 21 / 182 | 56.33% | +175.14 | +0.49 | 1.310 | 107.03 | 10 | 5m |
| SL4 + TP100 baseline | 57 / 145 / 1 / 158 | 28.22% | +237.45 | +0.66 | 1.166 | 250.05 | 23 | 10m |
| SL4 + TP75 | 65 / 136 / 2 / 158 | 32.34% | +152.75 | +0.42 | 1.115 | 259.18 | 17 | 10m |
| SL4 + TP50 | 79 / 122 / 2 / 158 | 39.30% | +254.65 | +0.71 | 1.237 | 250.43 | 17 | 5m |
| SL4 + TP25 | 105 / 85 / 13 / 158 | 55.26% | +205.68 | +0.57 | 1.299 | 132.93 | 7 | 5m |
| SL6 + TP100 | 61 / 174 / 1 / 125 | 25.96% | +76.75 | +0.21 | 1.044 | 375.60 | 28 | 10m |
| SL6 + TP75 | 69 / 165 / 2 / 125 | 29.49% | −25.55 | −0.07 | 0.984 | 378.73 | 18 | 10m |
| SL6 + TP50 | 87 / 147 / 2 / 125 | 37.18% | +190.95 | +0.53 | 1.148 | 314.48 | 12 | 5m |
| SL6 + TP25 | 116 / 104 / 16 / 125 | 52.73% | +218.69 | +0.61 | 1.266 | 161.13 | 8 | 5m |

For all 12 policies, average/median winner, average/median loser, and mean/median holding time are listed here (points, minutes):

| Policy | Avg win / median win | Avg loss / median loss | Mean / median hold |
|---|---:|---:|---:|
| SL2 + TP100 | +26.11 / +22.53 | −9.04 / −7.03 | 18.96 / 10 |
| SL2 + TP75 | +20.93 / +17.49 | −9.01 / −6.35 | 14.80 / 10 |
| SL2 + TP50 | +16.16 / +13.68 | −8.39 / −5.95 | 10.45 / 5 |
| SL2 + TP25 | +8.32 / +7.30 | −8.19 / −4.80 | 6.93 / 5 |
| SL4 + TP100 | +29.25 / +27.35 | −9.86 / −8.05 | 21.66 / 10 |
| SL4 + TP75 | +22.77 / +20.51 | −9.76 / −7.72 | 16.32 / 10 |
| SL4 + TP50 | +16.83 / +14.60 | −8.81 / −6.47 | 11.42 / 5 |
| SL4 + TP25 | +8.52 / +7.89 | −8.10 / −5.75 | 7.13 / 5 |
| SL6 + TP100 | +29.67 / +27.35 | −9.96 / −7.85 | 22.96 / 10 |
| SL6 + TP75 | +23.00 / +20.51 | −9.77 / −7.65 | 17.31 / 10 |
| SL6 + TP50 | +17.02 / +15.88 | −8.77 / −6.45 | 12.35 / 5 |
| SL6 + TP25 | +8.96 / +8.26 | −7.89 / −4.45 | 7.75 / 5 |

Each combination's year/month, CE/PE, ITM rank, entry-time, MFE/MAE, holding, and period metrics are preserved in machine-readable summaries. The trade-level output contains every policy/setup result. A closer target raises target-hit frequency but can also increase same-bar ambiguity; a wider stop changes loss size and exposure. The 12-policy sample does not support a stable joint winner.

## 7. Development selection and validation

Selection rule fixed in the run configuration: within each experiment family choose the alternative with highest Jan–Jun gross resolved points divided by all baseline setups; tie-break by lower equal-unit drawdown, then shorter loss streak. Validation rejection rule: reject if validation points/setup does not exceed baseline, or candidate drawdown or loss streak exceeds baseline. No replacement candidate was chosen from validation or September.

| Experiment | Jan–Jun candidate selected using training only | Training points/setup | Jul–Aug candidate vs baseline points/setup | Validation DD vs baseline | Decision |
|---|---|---:|---:|---:|---|
| Independent stop | SL2 | +0.180 (48.30 points) | +0.317 vs +1.131 | 80.80 vs 74.50 | Reject |
| Independent target | TP50 | +0.824 (221.63 points) | +0.495 vs +1.131 | 63.45 vs 74.50 | Reject |
| Combined | SL4 + TP50 | +0.824 (221.63 points) | +0.495 vs +1.131 | 63.45 vs 74.50 | Reject |

In the validation period, SL2 had 9 targets/27 stops and +22.80 points; TP50 and SL4+TP50 had 15 targets/26 stops/0 ambiguous and +35.65 points; baseline had 12 targets/29 stops and +81.40 points. September incomplete check: baseline +21.20, SL2 −63.30, TP50/SL4+TP50 −2.63. September candidate values are shown only as diagnostic results, not as an untouched holdout. No candidate passed validation; there is no surviving holdout evaluation and no robust improvement claim.

## 8. Ekalayava descriptive analysis (not P&L)

Canonical entry observations are unchanged: opening range, premium breakdown, recovery/base, causally identified swing high, then entry on canonical swing-high breakout while still below Opening High. The specification has no approved numerical structural-stop buffer or full exit lifecycle. Consequently **all 253 remain unresolved**; do not interpret any target touches or excursion points as wins, realized P&L, or a win rate.

| Measure | Result |
|---|---:|
| Entries / opening-high touches / no-touch paths | 253 / 109 (43.1%) / 144 |
| Canonical lifecycle-resolved / unresolved | 0 / 253 |
| MFE mean / median / p25 / p75 / p90 | +57.35 / +31.05 / +10.90 / +77.25 / +136.15 |
| MAE mean / median / p25 / p75 / p90 | −53.27 / −45.60 / −72.35 / −21.80 / −10.45 |
| Target distance mean / median | 61.10 / 54.80 |
| Time to MFE mean / median | 113.99 / 85 min |
| Time to MAE mean / median | 179.05 / 195 min |
| Target-touch time, touch cases only, mean / median | 93.72 / 65 min |
| MFE occurred before maximum MAE in observation ordering | 151/253 |

Side distribution: CE 55/126 target touches (43.7%), PE 54/127 (42.5%). Rank: ITM2 53/128 (41.4%), ITM3 56/125 (44.8%). Entry bucket: 09:15–09:59 38/62 (61.3%), 10:00–10:59 42/114 (36.8%), after 11:00 29/77 (37.7%). The early bucket's target distance was smaller (mean/median 24.17/23.58 points) than the full sample; this is descriptive and not an entry filter proposal. Monthly/year breakdowns and observation-level excursions are in `multi_year_ekalayava_summary.csv` and `multi_year_ekalayava_observations.csv`.

No new experimental Ekalayava stop simulation was run in this task. Earlier hypothetical anchor/buffer studies remain explicitly noncanonical, with no approved buffer and no realized P&L. The missing decision is an approved structural anchor, numeric buffer, triggering convention, and complete exit treatment (including end-of-day/expiry/end-of-data) before any valid lifecycle P&L comparison.

## 9. Robustness, limitations, and final decision

* **No multi-year validation:** 2022–2025 5-minute NIFTY and exact option contract bars are absent locally. Groww's documented 5-minute history is limited to the most recent three months; no replacement source was used. Official docs: [Groww Historical Data API](https://groww.in/trade-api/docs/python-sdk/historical-data) and [Groww cURL Historical Data](https://groww.in/trade-api/docs/curl/historical-data).
* **Incomplete 2026 data:** option coverage is 75.94%, and September is substantially incomplete. Missing contracts can hide both signals and outcomes. Reported backtest populations therefore describe only events recoverable from the saved event ledger and available bars.
* **Only one calendar year:** train and validation are adjacent segments of the same year; month effects and market regime variation are not independent yearly replication.
* **Selection overfit risk:** fixed small candidate sets and train-only selection bound the experiment, but the TP alternatives had already been examined in prior research, and September is not untouched.
* **OHLC limitations:** a 5-minute candle cannot establish within-bar event ordering or exact touch time. Same-bar stop/target collisions are ambiguous.
* **Gross-only results:** no supported transaction cost or fill assumptions are included; results are not rupee P&L or evidence of profitability.
* **Ekalayava lifecycle:** unresolved entries cannot be ranked by canonical win rate or P&L until an exit specification is approved.

**Final decision: NO RELIABLE WINNER — MORE EVIDENCE REQUIRED.** Keep the canonical SL4/Opening High baseline unchanged. No alternative is robust enough to merit a strategy change or paper-observer promotion. Do not start the observer based on this historical study. The exact next research step is to acquire a licensed, provenance-verifiable 2022–2025 5-minute NIFTY underlying plus exact daily CE/PE ITM2/ITM3 option data (or explicitly decide to limit scope to 2026); then pre-register a fresh chronological evaluation before any new selection. Separately, obtain an explicit Ekalayava exit/stop specification before P&L testing.

## 10. Reproducibility artifacts and safety

The offline calculation entrypoint is `tools/run_multi_year_research.py`; policy primitives are `app/research_target_policies.py`. Key outputs:

* `multi_year_baseline_metrics.csv`
* `multi_year_l2l_stop_policy_trades.csv` and `multi_year_l2l_stop_policy_summary.csv`
* `multi_year_l2l_target_policy_trades.csv` and `multi_year_l2l_target_policy_summary.csv`
* `multi_year_l2l_combined_sl_tp_trades.csv` and `multi_year_l2l_combined_sl_tp_summary.csv`
* `multi_year_l2l_stop_loss_forensics.csv` and `multi_year_l2l_stop_loss_summary.csv`
* `multi_year_ekalayava_observations.csv` and `multi_year_ekalayava_summary.csv`
* `multi_year_period_metrics.csv`, `multi_year_data_coverage.json`, `multi_year_candidate_selection.json`, and `multi_year_research_config.json`

These machine-readable files contain summaries and event-level replay outcomes only; raw market datasets remain ignored/unpublished. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`. This run made no Groww API calls, started no observer, and placed no orders. Policy candidates are offline research only; canonical strategy definitions and production behavior were not changed.
