# Ekalayava Final Validation — Jan–Sep 2026

**Requested period:** 2026-01-01 through 2026-09-30 inclusive. Source data ends Sep 29; Sep 30 is missing. Ekalayava remains observational. Opening-high touches are **not wins** or realized P&L, and this report does not invent an SL or exit lifecycle.

## Canonical entry and implementation audit

The tested entry follows the current causal code: the first option candle sets opening high/low; a later premium candle breaks below Opening Low; a causal left=2/right=0 swing high forms; a later completed candle breaks and closes above that reference while still below Opening High; entry is the completed breakout candle close. No future candle defines the entry, and no indicator was added.

The current canonical source does not specify an executable structural stop or complete Ekalayava lifecycle. Code contains no Ekalayava SL, opposite-signal exit, forced EOD close, expiry close, or end-of-data mark rule. The provided examples establish the *structural* concept but do not pin down the exact anchor candle/low or numerical buffer. No stop price or SL-hit statistic is inferred.

## Full-period post-entry behavior

- **253 entries:** 109 opening-high target touches (43.1%); 144 with no target touch in the observed same-day path.
- **All 253 lifecycle outcomes remain unresolved**, including entries that touched the reference target. The reporting schema stores `TARGET_TOUCH`, `target_touch_time`, and `time_to_target_minutes`; it leaves `exit_price`, `exit_time`, holding duration, and realized points empty.
- Post-entry observation continues through 15:25, even after an opening-high touch. All 253 event paths contain the expected number of post-entry 5-minute bars to session end.
- Mean / median MFE: **+57.35 / +31.05** points. Mean / median MAE: **−53.27 / −45.60** points.
- Mean / median time to MFE: **113.99 / 85** minutes. Mean / median time to MAE: **179.05 / 195** minutes.
- For the 109 touch observations, mean / median time to opening-high touch: **93.72 / 65** minutes. Average / median target distance from entry: **61.10 / 54.80** points.
- Among touch entries, mean MFE was +103.27; among no-touch entries it was +22.58. This describes observed paths only, not exits or return outcomes.

## Structural interaction measurement

A causal **measurement proxy**, not a stop rule, is recorded as the minimum premium low from the first Opening-Low-break candle through the completed breakout entry candle. This uses only information available by entry. After entry:

| Pre-entry reference | Revisited | Share |
|---|---:|---:|
| Observed reversal-structure-low candidate | 187/253 | 73.9% |
| Breakout candle low | 223/253 | 88.1% |
| Opening candle low | 249/253 | 98.4% |

This candidate-low definition is made explicit for descriptive analysis only. The strategy owner still needs to decide the precise structural anchor, numerical buffer, and trigger convention before it can become an executable stop.

## Chronological train / validation / final OOS

| Period | Entries | Target touches | No-touch observations | Mean MFE | Mean MAE | Mean target-touch time |
|---|---:|---:|---:|---:|---:|---:|
| Jan–Mar | 94 | 42 | 52 | +71.24 | −58.92 | 76.31 min |
| Apr–Jun | 97 | 41 | 56 | +61.23 | −57.26 | 105.00 min |
| Jul–Sep | 62 | 26 | 36 | +30.20 | −38.49 | 104.04 min |
| Train Jan–Jun | 191 | 83 | 108 | +66.16 | −58.07 | 90.48 min |
| Validation Jul–Aug | 47 | 22 | 25 | +33.18 | −34.71 | 95.23 min |
| Final OOS Sep* | 15 | 4 | 11 | +20.88 | −50.34 | 152.50 min |

*September has data only through Sep 29; 33/84 option contract-days are complete. These touch fractions are conditional on available exact contracts.

## Monthly behavior

| Month | Entries | Target touches | No-touch | Mean MFE | Mean MAE | Mean touch time |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 35 | 20 | 15 | +65.64 | −59.69 | 89.8 min |
| Feb | 38 | 14 | 24 | +69.05 | −43.23 | 73.2 min |
| Mar | 21 | 8 | 13 | +84.50 | −86.01 | 48.1 min |
| Apr | 27 | 5 | 22 | +43.06 | −43.26 | 166.0 min |
| May | 34 | 19 | 15 | +77.96 | −62.19 | 108.4 min |
| Jun | 36 | 17 | 19 | +59.06 | −63.10 | 83.2 min |
| Jul | 21 | 11 | 10 | +37.73 | −37.63 | 119.6 min |
| Aug | 26 | 11 | 15 | +29.51 | −32.35 | 70.9 min |
| Sep* | 15 | 4 | 11 | +20.88 | −50.34 | 152.5 min |

Touch times are averaged only among observed touches. A blank/low count is not treated as a loss.

## CE/PE and ITM rank

| Side / rank | Entries | Touches | Touch fraction | Mean MFE | Mean MAE |
|---|---:|---:|---:|---:|---:|
| CE ITM2 | 64 | 27 | 42.2% | +50.70 | −46.88 |
| CE ITM3 | 62 | 28 | 45.2% | +54.62 | −59.08 |
| PE ITM2 | 64 | 26 | 40.6% | +58.94 | −50.93 |
| PE ITM3 | 63 | 28 | 44.4% | +65.16 | −56.43 |

Combined CE was 55/126 touches (43.7%); PE was 54/127 (42.5%). ITM2 was 53/128 (41.4%); ITM3 was 56/125 (44.8%). These are descriptive fractions, not win rates.

## Entry time and weekday

| Entry time IST | Entries | Touches (fraction) | Mean MFE | Mean MAE |
|---|---:|---:|---:|---:|
| 09:15–09:59 | 62 | 38 (61.3%) | +45.78 | −75.17 |
| 10:00–10:59 | 114 | 42 (36.8%) | +48.52 | −58.50 |
| 11:00–12:59 | 64 | 29 (45.3%) | +87.61 | −29.25 |
| 13:00–15:15 | 13 | 0 (0.0%) | +40.90 | −21.31 |

| Weekday | Entries | Touches | Mean MFE | Mean MAE |
|---|---:|---:|---:|---:|
| Monday | 55 | 23 | +65.62 | −50.34 |
| Tuesday | 51 | 23 | +47.16 | −69.05 |
| Wednesday | 47 | 18 | +59.11 | −42.27 |
| Thursday | 52 | 21 | +43.17 | −60.72 |
| Friday | 46 | 22 | +48.01 | −42.08 |
| Sunday (Feb 1 special session) | 2 | 2 | +631.20 | −54.30 |

The two Sunday observations belong to one special session and are not a recurring weekday sample.

## Missing-data impact and readiness

The expected window has 740 option slots: 174 required exact strikes are absent from Groww’s returned catalogs; four additional Sep 30 slots cannot be selected without its NIFTY 09:15 open. Of 185 sessions, 112 are fully usable, 55 partial, and 18 unusable. The 253 entries occurred on 202 fully usable and 51 partially usable days; no entries were detected on unusable days. Missing contracts may suppress entries and change all observed fractions.

**Structural SL implementation:** conceptual only; no executable Ekalayava stop exists. The pre-entry low proxy and revisit counts are diagnostic records, not stop prices or triggers. Before any Ekalayava P&L or paper trade, version a decision for the exact structural anchor, buffer/trigger, whether target touch closes a position, same-candle ambiguity, opposite signal, EOD, expiry, and end-of-data handling. Until then readiness stays **OBSERVATION-ONLY**.
