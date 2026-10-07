# Level-to-Level Final Validation — Jan–Sep 2026

**Requested window:** 2026-01-01 through 2026-09-30 inclusive. **Data incomplete:** Sep 30 has no Groww underlying feed; 178/740 expected option slots are missing/unselectable. Results below use the corrected exact daily contract selector and canonical Level-to-Level rules. No strategy definition was changed.

## Overall observed-data results

- **361 setups:** 203 resolved (58 TARGET, 145 SL), 157 skipped because entry was already beyond the stop, 1 ambiguous, 0 open.
- **Gross resolved points:** +234.85 option-premium points; mean +1.16, median −4.45. Average winner +29.25; average loser −9.81.
- Target fraction among resolved TARGET/SL outcomes: 58/203 = **28.6%**. This is not a net return or a profitability claim.
- Mean resolved-trade MFE / MAE: +18.14 / −12.81 points; mean holding time 21.58 minutes.
- Maximum drawdown: 251.95 points in the resolved event series ordered by timestamp then symbol. This is not account/capital drawdown. Longest win/loss streak: 4 / 23.

The metrics are premium-point sums, not portfolio returns. There is no sizing, commission, slippage, spread, or capital model.

## Chronological periods

| Period | Setups | Resolved | Target | SL | Skipped | Ambiguous | Gross points | Mean / median resolved points | Mean hold (min) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Jan–Mar | 130 | 63 | 19 | 44 | 66 | 1 | −3.40 | −0.05 / −4.80 | 17.86 |
| Apr–Jun | 139 | 85 | 23 | 62 | 54 | 0 | +135.65 | +1.60 / −4.30 | 20.29 |
| Jul–Sep | 92 | 55 | 16 | 39 | 37 | 0 | +102.60 | +1.87 / −4.15 | 27.82 |
| Train Jan–Jun | 269 | 148 | 42 | 106 | 120 | 1 | +132.25 | +0.89 / −4.70 | 19.26 |
| Validation Jul–Aug | 72 | 41 | 12 | 29 | 31 | 0 | +81.40 | +1.99 / −4.00 | 28.54 |
| Final OOS Sep* | 20 | 14 | 4 | 10 | 6 | 0 | +21.20 | +1.51 / −5.45 | 25.71 |

*September ends at Sep 29 in the available data; Sep 30 and many exact option slots are absent. The OOS sample is incomplete and does not establish generalization.

## Monthly distribution

| Month | Setups | Resolved | Target | SL | Skipped | Gross points | Mean MFE | Mean MAE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Jan | 55 | 32 | 11 | 21 | 22 | +47.35 | +16.58 | −14.60 |
| Feb | 49 | 15 | 6 | 9 | 34 | +41.60 | +11.35 | −13.38 |
| Mar | 26 | 16 | 2 | 14 | 10 | −92.35 | +30.02 | −20.65 |
| Apr | 36 | 19 | 4 | 15 | 17 | −65.65 | +15.33 | −12.29 |
| May | 52 | 28 | 14 | 14 | 24 | +298.00 | +33.63 | −14.73 |
| Jun | 51 | 38 | 5 | 33 | 13 | −96.70 | +11.18 | −10.84 |
| Jul | 34 | 25 | 3 | 22 | 9 | −64.70 | +16.01 | −11.64 |
| Aug | 38 | 16 | 9 | 7 | 22 | +146.10 | +15.86 | −7.08 |
| Sep* | 20 | 14 | 4 | 10 | 6 | +21.20 | +13.61 | −10.01 |

*Partial OOS data through Sep 29 only.

## CE/PE and ITM rank

| Contract group | Setups | Resolved | Target | SL | Skipped | Gross points | Target / resolved |
|---|---:|---:|---:|---:|---:|---:|---:|
| CE ITM2 | 94 | 55 | 12 | 43 | 39 | −125.30 | 21.8% |
| CE ITM3 | 91 | 49 | 14 | 35 | 41 | +108.70 | 28.6% |
| PE ITM2 | 89 | 47 | 15 | 32 | 42 | +58.85 | 31.9% |
| PE ITM3 | 87 | 52 | 17 | 35 | 35 | +192.60 | 32.7% |

Totals by side: CE 185 setups / −16.60 gross points; PE 176 / +251.45. Totals by rank: ITM2 183 / −66.45; ITM3 178 / +301.30. These comparisons are affected by missing exact contracts and should be read as observed distributions only.

## Entry-time and weekday distributions

| Entry time (IST) | Setups | Target | SL | Gross points |
|---|---:|---:|---:|---:|
| 09:15–09:59 | 285 | 40 | 114 | −20.90 |
| 10:00–10:59 | 74 | 18 | 30 | +255.90 |
| 11:00 | 2 | 0 | 1 | −0.15 |

One remaining 11:00 setup was ambiguous. The canonical window ends at 11:00.

| Weekday | Setups | Target | SL | Gross points |
|---|---:|---:|---:|---:|
| Monday | 78 | 15 | 31 | +62.55 |
| Tuesday | 80 | 17 | 21 | +275.25 |
| Wednesday | 72 | 14 | 26 | +180.70 |
| Thursday | 67 | 5 | 32 | −135.05 |
| Friday | 63 | 7 | 34 | −132.75 |
| Sunday (Feb 1 special session) | 1 | 0 | 1 | −15.85 |

## Concentration and buffer sensitivity

There were 33 positive and 70 negative days among dates with resolved L2L points. May netted +298.00 points; the remaining eight months together netted −63.15. The top five daily contributions were +168.65 (Mar 16), +120.45 (May 19), +90.90 (Aug 25), +89.75 (May 5), and +75.65 (May 14), totaling +545.40. All positive-day contributions summed to +1,397.80 before negative days. The combined total is therefore concentrated and does not describe consistency across months.

The repository already allows the L2L buffer as a parameter. A descriptive 3-point comparison on the same selected contract data yielded 51 target / 137 SL / 172 skipped / 1 ambiguous and +78.20 points (mean +0.42; median −4.70). The canonical 4-point run yielded 58 / 145 / 157 / 1 and +234.85. The default was not changed; this is not a parameter search or selection.

## Data quality and impact

Correct selection resolved 562 exact contract symbols across observed dates; 561 contract-days are 75/75, one is 74/75, and 174 selected strikes are absent from the returned catalogs. Sep 30 adds four unselectable expected slots due to no underlying opening candle. Overall option coverage is 42,149/55,500 candles (75.9%). L2L generated 290 setups on fully usable days and 71 on partially usable days; no event was generated on the 18 unusable dates. Missing contracts can suppress signals and outcomes; zero observed events on an unusable day is not evidence that no setup occurred.

## Canonical rule and readiness

The tested rule remains: use the opening candle levels; a completed red candle breaks below Opening Low; enter at the close of the first later completed green candle, within 09:15–11:00 IST; stop is Opening Low minus the configured buffer (default 4); target is Opening High. A same-candle SL/target collision is marked ambiguous.

Historical rules are deterministic. The live listener still tests the current candle for low-below-opening-low and green close without requiring the preceding-red/first-subsequent-green sequence or confirming the bar is closed. Combined with data gaps, this leaves L2L **NOT READY** for controlled live paper signals. No live session was started and no order functionality was enabled.
