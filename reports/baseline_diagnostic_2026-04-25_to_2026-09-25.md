# Baseline Diagnostic Report — 2026-04-25 to 2026-09-25

**Source of truth:** existing `data/reports/baseline_v1_requested_period.json` (baseline_v1). No market data was downloaded, no strategy code or rules were changed, and no backtest was rerun. This diagnostic preserves that baseline and summarizes its recorded events and completeness metadata.

**Interpretation boundary:** reported points are the existing outcome points, with open and skipped setups carrying no realized points. Group breakdowns below are descriptive aggregations of the source events. “Average/median points” use point-bearing TARGET/SL outcomes only; winners use TARGET points and losers use SL points. MFE/MAE and holding-time means use only rows where the source provides those fields. Group drawdown/streaks, where shown, are descriptive calculations from point-bearing events in the original `trade_events` ledger order; the overall values are copied from the baseline report.

## 1. Data coverage

- Requested period: **2026-04-25 through 2026-09-25 inclusive**. The source has 106 requested trading sessions, from 2026-04-27 through 2026-09-25.
- Underlying: **8,895 5-minute candles**, all 106/106 requested sessions complete; 0 missing underlying session intervals.
- Option contract-days: **406/424 available (95.75%)**; **381 complete (89.86% of expected), 25 partial, 18 missing**. Complete requires all 75 session timestamps per contract-day.
- Missing option candle intervals: **2,328**. Option candles present: 29,472.
- Day usability in source report: **91 fully usable**, **5 partially usable**, **10 unusable**. Fully usable coverage: 85.85% of requested sessions.

By selected contract group:

| Group | Available days | Complete days | Expected days |
|---|---:|---:|---:|
| CE_ITM2 | 102 | 96 | 106 |
| CE_ITM3 | 100 | 92 | 106 |
| PE_ITM2 | 102 | 98 | 106 |
| PE_ITM3 | 102 | 95 | 106 |

The source identifies missing contract-days on **July 1, 2, 3, and 6** for four selected contracts (CE ITM2, CE ITM3, PE ITM2, PE ITM3; expiry July 7), plus **July 15 and 16** for CE ITM3 (expiry July 21): 18 contract-days total. Another 25 contract-days are partial. The source recorded 2,328 missing session intervals across missing and partial option data. No missing candle was filled.

The 10 unusable and five partially usable dates mean the aggregate event set may omit signals or have truncated price paths on those dates. The source does not quantify counterfactual setups that would have appeared with complete option data; those cannot be inferred from this report.

## 2. Overall results

| Setups | Valid | Skipped | Open | Targets | Stop-losses | Points | Avg points / resolved trade | Median points / resolved trade | Avg winner | Avg loser | Mean MFE | Mean MAE | Mean holding min | Max drawdown | Max consecutive wins | Max consecutive losses |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 417 | 326 | 91 | 88 | 131 | 107 | 4,077.00 | 17.13 | 9.85 | 38.45 | -8.98 | 21.79 | -22.38 | 53.51 | 99.75 | 10 | 10 |

The baseline has 238 point-bearing outcomes (131 targets + 107 stop-losses), 88 unresolved opens, and 91 skipped setups. The reported average and median points are over resolved outcomes; they do not assign a mark-to-market value to OPEN events. Average winners/losers are direct means of recorded TARGET/SL point values.

## 3. Level-to-Level

| Setups | Valid | Skipped | Open | Targets | Stop-losses | Points | Avg points / resolved trade | Median points / resolved trade | Avg winner | Avg loser | Mean MFE | Mean MAE | Mean holding min | Ledger-ordered max DD* | Max consecutive wins* | Max consecutive losses* |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 247 | 156 | 91 | 0 | 49 | 107 | 502.40 | 3.22 | -4.00 | 29.86 | -8.98 | 11.48 | -7.53 | 25.90 | 219.75 | 6 | 21 |

Level-to-Level source win rate on resolved target/SL outcomes: **31.4%** (49/156). Source strategy-specific average holding time: 25.90 minutes; source strategy MFE/MAE are reproduced in the table by event aggregation.

## 4. Ekalayava

| Setups | Valid | Skipped | Open | Targets | Stop-losses | Points | Avg points / resolved trade | Median points / resolved trade | Avg winner | Avg loser | Mean MFE | Mean MAE | Mean holding min | Ledger-ordered max DD* | Max consecutive wins* | Max consecutive losses* |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 170 | 170 | 0 | 88 | 82 | 0 | 3,574.60 | 43.59 | 34.97 | 43.59 | n/a | 36.76 | -43.95 | 106.04 | 0.00 | 82 | 0 |

The canonical output defines no Ekalayava stop-loss, so average loser and win rate are **not defined**. Its 88 OPEN entries have no recorded exit price, realized points, or `time_to_exit_minutes`; they are not counted as winners or losers. Group ledger-ordered streak and drawdown are partial diagnostics over its 82 point-bearing target events only and must not be interpreted as full strategy risk statistics.

## 5. Breakdowns

The following tables aggregate source event rows. Points/average/median use only point-bearing outcomes. Skips and open outcomes remain separately visible.

### CE vs PE

| Group | Setups | Valid | Skipped | Open | Targets | SL | Points | Avg resolved pts | Mean MFE | Mean MAE | Mean hold min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CE | 203 | 156 | 47 | 37 | 65 | 54 | 2,072.75 | 17.42 | 22.62 | -21.92 | 59.37 |
| PE | 214 | 170 | 44 | 51 | 66 | 53 | 2,004.25 | 16.84 | 21.00 | -22.81 | 47.65 |

### ITM2 vs ITM3

| Group | Setups | Valid | Skipped | Open | Targets | SL | Points | Avg resolved pts | Mean MFE | Mean MAE | Mean hold min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ITM2 | 212 | 165 | 47 | 46 | 65 | 54 | 1,864.60 | 15.67 | 20.81 | -21.11 | 52.65 |
| ITM3 | 205 | 161 | 44 | 42 | 66 | 53 | 2,212.40 | 18.59 | 22.80 | -23.69 | 54.37 |

### Entry hour (exchange local time)

| Group | Setups | Valid | Skipped | Open | Targets | SL | Points | Avg resolved pts | Mean MFE | Mean MAE | Mean hold min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 09:00–09:59 | 235 | 161 | 74 | 19 | 62 | 80 | 997.90 | 7.03 | 12.41 | -16.38 | 41.73 |
| 10:00–10:59 | 132 | 117 | 15 | 42 | 49 | 26 | 1,527.15 | 20.36 | 25.57 | -34.16 | 61.07 |
| 11:00–11:59 | 31 | 29 | 2 | 13 | 15 | 1 | 1,142.80 | 71.42 | 57.10 | -23.29 | 108.44 |
| 12:00–12:59 | 12 | 12 | 0 | 7 | 5 | 0 | 409.15 | 81.83 | 69.47 | -14.20 | 99.00 |
| 13:00–13:59 | 3 | 3 | 0 | 3 | 0 | 0 | 0.00 | n/a | 59.63 | -6.02 | n/a |
| 14:00–14:59 | 2 | 2 | 0 | 2 | 0 | 0 | 0.00 | n/a | 4.10 | -24.23 | n/a |
| 15:00–15:59 | 2 | 2 | 0 | 2 | 0 | 0 | 0.00 | n/a | 1.85 | -6.42 | n/a |

Most recorded entries were in the 09:00 hour (235/417), followed by 10:00 (132/417). These are event counts, not opportunity-adjusted rates.

### Day of week

| Group | Setups | Valid | Skipped | Open | Targets | SL | Points | Avg resolved pts | Mean MFE | Mean MAE | Mean hold min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Monday | 91 | 73 | 18 | 20 | 25 | 28 | 845.65 | 15.96 | 21.21 | -19.22 | 44.34 |
| Tuesday | 97 | 72 | 25 | 18 | 36 | 18 | 1,042.70 | 19.31 | 21.72 | -26.47 | 49.07 |
| Wednesday | 85 | 66 | 19 | 19 | 27 | 20 | 1,090.70 | 23.21 | 25.50 | -19.83 | 45.85 |
| Thursday | 79 | 58 | 21 | 19 | 22 | 17 | 680.50 | 17.45 | 21.08 | -23.03 | 60.51 |
| Friday | 65 | 57 | 8 | 12 | 21 | 24 | 417.45 | 9.28 | 18.71 | -23.22 | 71.56 |

### Month

| Group | Setups | Valid | Skipped | Open | Targets | SL | Points | Avg resolved pts | Mean MFE | Mean MAE | Mean hold min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-04 | 18 | 14 | 4 | 3 | 7 | 4 | 322.30 | 29.30 | 39.94 | -13.41 | 79.09 |
| 2026-05 | 86 | 62 | 24 | 15 | 33 | 14 | 1,361.90 | 28.98 | 30.44 | -25.52 | 63.40 |
| 2026-06 | 88 | 75 | 13 | 19 | 23 | 33 | 734.85 | 13.12 | 21.77 | -24.95 | 35.54 |
| 2026-07 | 64 | 51 | 13 | 13 | 15 | 23 | 331.05 | 8.71 | 19.14 | -19.18 | 59.21 |
| 2026-08 | 85 | 63 | 22 | 17 | 27 | 19 | 729.65 | 15.86 | 17.22 | -14.13 | 40.00 |
| 2026-09 | 76 | 61 | 15 | 21 | 26 | 14 | 597.25 | 14.93 | 15.07 | -29.88 | 70.12 |

### Fully usable vs partially usable vs unusable dates

| Group | Setups | Valid | Skipped | Open | Targets | SL | Points | Avg resolved pts | Mean MFE | Mean MAE | Mean hold min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fully usable (90 event dates) | 388 | 305 | 83 | 81 | 120 | 104 | 3,761.95 | 16.79 | 21.70 | -21.76 | 52.46 |
| Partially usable (5 event dates) | 24 | 19 | 5 | 6 | 10 | 3 | 215.15 | 16.55 | 20.15 | -29.51 | 61.92 |
| Unusable (3 event dates) | 5 | 2 | 3 | 1 | 1 | 0 | 99.90 | 99.90 | 36.43 | -36.26 | 180.00 |
| Unclassified (0 event dates) | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 | n/a | n/a | n/a | n/a |

A “fully usable” grouping means the date was classified so by the source completeness report; it does not guarantee every selected contract row was error-free beyond that report’s criterion. Partial/unusable outcome summaries are conditional on events the baseline could actually form; they are not matched performance comparisons.

## 6. Open trades (all 88)

All 88 open entries are Ekalayava. At the requested period end, the source still labels them OPEN. The source has no exit timestamp/price, realized points, or holding duration for any of them; therefore duration-to-end is **not reported** and no end-of-data mark-to-market is inferred. MFE/MAE below are the source values.

| # | Strategy | Instrument | Side | ITM | Entry date/time IST | Entry price | End status | Holding min | MFE | MAE |
|---:|---|---|---|---:|---|---:|---|---:|---:|---:|
| 1 | EKALAYAVA | NSE-NIFTY-28Apr26-24050-PE (strike 24050) | PE | ITM2 | 2026-04-27 10:10 | 91.50 | OPEN at period end 2026-09-25 | n/a | 54.05 | -36.15 |
| 2 | EKALAYAVA | NSE-NIFTY-05May26-24200-PE (strike 24200) | PE | ITM2 | 2026-04-29 13:20 | 128.90 | OPEN at period end 2026-09-25 | n/a | 80.35 | -2.65 |
| 3 | EKALAYAVA | NSE-NIFTY-05May26-24250-PE (strike 24250) | PE | ITM3 | 2026-04-29 13:20 | 147.80 | OPEN at period end 2026-09-25 | n/a | 88.40 | -3.70 |
| 4 | EKALAYAVA | NSE-NIFTY-05May26-23950-CE (strike 23950) | CE | ITM2 | 2026-05-05 12:10 | 45.05 | OPEN at period end 2026-09-25 | n/a | 102.25 | -11.95 |
| 5 | EKALAYAVA | NSE-NIFTY-12May26-23850-CE (strike 23850) | CE | ITM3 | 2026-05-11 11:05 | 156.50 | OPEN at period end 2026-09-25 | n/a | 59.50 | -66.55 |
| 6 | EKALAYAVA | NSE-NIFTY-12May26-23600-CE (strike 23600) | CE | ITM3 | 2026-05-12 10:15 | 103.95 | OPEN at period end 2026-09-25 | n/a | 4.30 | -103.90 |
| 7 | EKALAYAVA | NSE-NIFTY-12May26-23650-CE (strike 23650) | CE | ITM2 | 2026-05-12 10:15 | 71.35 | OPEN at period end 2026-09-25 | n/a | 3.10 | -71.30 |
| 8 | EKALAYAVA | NSE-NIFTY-26May26-23550-PE (strike 23550) | PE | ITM2 | 2026-05-20 10:20 | 269.60 | OPEN at period end 2026-09-25 | n/a | -0.50 | -132.60 |
| 9 | EKALAYAVA | NSE-NIFTY-26May26-23600-PE (strike 23600) | PE | ITM3 | 2026-05-20 10:20 | 297.15 | OPEN at period end 2026-09-25 | n/a | 0.55 | -142.15 |
| 10 | EKALAYAVA | NSE-NIFTY-26May26-23700-CE (strike 23700) | CE | ITM3 | 2026-05-21 09:50 | 234.40 | OPEN at period end 2026-09-25 | n/a | 1.85 | -115.50 |
| 11 | EKALAYAVA | NSE-NIFTY-26May26-23750-CE (strike 23750) | CE | ITM2 | 2026-05-21 09:50 | 203.90 | OPEN at period end 2026-09-25 | n/a | 2.55 | -102.50 |
| 12 | EKALAYAVA | NSE-NIFTY-26May26-23750-PE (strike 23750) | PE | ITM2 | 2026-05-22 11:25 | 143.00 | OPEN at period end 2026-09-25 | n/a | 32.20 | -38.55 |
| 13 | EKALAYAVA | NSE-NIFTY-26May26-23800-PE (strike 23800) | PE | ITM3 | 2026-05-22 11:25 | 166.75 | OPEN at period end 2026-09-25 | n/a | 39.85 | -41.40 |
| 14 | EKALAYAVA | NSE-NIFTY-26May26-24000-PE (strike 24000) | PE | ITM2 | 2026-05-25 09:35 | 130.25 | OPEN at period end 2026-09-25 | n/a | 8.25 | -91.85 |
| 15 | EKALAYAVA | NSE-NIFTY-26May26-24050-PE (strike 24050) | PE | ITM3 | 2026-05-25 09:35 | 159.50 | OPEN at period end 2026-09-25 | n/a | 9.45 | -105.40 |
| 16 | EKALAYAVA | NSE-NIFTY-02Jun26-23950-PE (strike 23950) | PE | ITM2 | 2026-05-27 11:35 | 141.90 | OPEN at period end 2026-09-25 | n/a | 50.30 | -11.35 |
| 17 | EKALAYAVA | NSE-NIFTY-02Jun26-24000-PE (strike 24000) | PE | ITM3 | 2026-05-27 11:35 | 166.35 | OPEN at period end 2026-09-25 | n/a | 56.30 | -11.50 |
| 18 | EKALAYAVA | NSE-NIFTY-02Jun26-23850-CE (strike 23850) | CE | ITM2 | 2026-05-29 10:05 | 220.95 | OPEN at period end 2026-09-25 | n/a | 10.90 | -142.20 |
| 19 | EKALAYAVA | NSE-NIFTY-02Jun26-23550-CE (strike 23550) | CE | ITM3 | 2026-06-01 10:45 | 133.00 | OPEN at period end 2026-09-25 | n/a | 36.45 | -98.50 |
| 20 | EKALAYAVA | NSE-NIFTY-02Jun26-23600-CE (strike 23600) | CE | ITM2 | 2026-06-01 10:45 | 105.60 | OPEN at period end 2026-09-25 | n/a | 31.05 | -80.10 |
| 21 | EKALAYAVA | NSE-NIFTY-02Jun26-23350-PE (strike 23350) | PE | ITM2 | 2026-06-02 10:10 | 87.00 | OPEN at period end 2026-09-25 | n/a | 15.20 | -86.95 |
| 22 | EKALAYAVA | NSE-NIFTY-02Jun26-23400-PE (strike 23400) | PE | ITM3 | 2026-06-02 10:10 | 126.85 | OPEN at period end 2026-09-25 | n/a | 16.55 | -126.80 |
| 23 | EKALAYAVA | NSE-NIFTY-09Jun26-23350-PE (strike 23350) | PE | ITM2 | 2026-06-04 10:35 | 140.85 | OPEN at period end 2026-09-25 | n/a | 36.25 | -55.55 |
| 24 | EKALAYAVA | NSE-NIFTY-09Jun26-23400-PE (strike 23400) | PE | ITM3 | 2026-06-04 10:35 | 163.15 | OPEN at period end 2026-09-25 | n/a | 41.30 | -60.40 |
| 25 | EKALAYAVA | NSE-NIFTY-09Jun26-23150-PE (strike 23150) | PE | ITM2 | 2026-06-08 11:15 | 99.05 | OPEN at period end 2026-09-25 | n/a | 21.85 | -39.80 |
| 26 | EKALAYAVA | NSE-NIFTY-09Jun26-23200-PE (strike 23200) | PE | ITM3 | 2026-06-08 11:15 | 122.30 | OPEN at period end 2026-09-25 | n/a | 27.70 | -47.30 |
| 27 | EKALAYAVA | NSE-NIFTY-16Jun26-23300-PE (strike 23300) | PE | ITM2 | 2026-06-10 10:05 | 159.00 | OPEN at period end 2026-09-25 | n/a | 62.50 | -41.45 |
| 28 | EKALAYAVA | NSE-NIFTY-16Jun26-23200-PE (strike 23200) | PE | ITM2 | 2026-06-11 10:00 | 208.00 | OPEN at period end 2026-09-25 | n/a | 2.70 | -105.25 |
| 29 | EKALAYAVA | NSE-NIFTY-16Jun26-23250-PE (strike 23250) | PE | ITM3 | 2026-06-11 10:00 | 239.00 | OPEN at period end 2026-09-25 | n/a | 2.35 | -118.80 |
| 30 | EKALAYAVA | NSE-NIFTY-16Jun26-24000-PE (strike 24000) | PE | ITM2 | 2026-06-16 10:00 | 110.00 | OPEN at period end 2026-09-25 | n/a | 9.40 | -100.75 |
| 31 | EKALAYAVA | NSE-NIFTY-16Jun26-24050-PE (strike 24050) | PE | ITM3 | 2026-06-16 10:00 | 151.00 | OPEN at period end 2026-09-25 | n/a | 11.75 | -99.20 |
| 32 | EKALAYAVA | NSE-NIFTY-23Jun26-24200-PE (strike 24200) | PE | ITM2 | 2026-06-22 09:40 | 132.25 | OPEN at period end 2026-09-25 | n/a | 1.80 | -43.45 |
| 33 | EKALAYAVA | NSE-NIFTY-23Jun26-24250-PE (strike 24250) | PE | ITM3 | 2026-06-22 09:40 | 168.00 | OPEN at period end 2026-09-25 | n/a | 2.65 | -45.60 |
| 34 | EKALAYAVA | NSE-NIFTY-30Jun26-23850-PE (strike 23850) | PE | ITM2 | 2026-06-24 09:45 | 170.50 | OPEN at period end 2026-09-25 | n/a | 5.90 | -112.80 |
| 35 | EKALAYAVA | NSE-NIFTY-30Jun26-23900-PE (strike 23900) | PE | ITM3 | 2026-06-24 09:45 | 197.55 | OPEN at period end 2026-09-25 | n/a | 6.60 | -127.80 |
| 36 | EKALAYAVA | NSE-NIFTY-30Jun26-23850-CE (strike 23850) | CE | ITM3 | 2026-06-30 10:00 | 106.30 | OPEN at period end 2026-09-25 | n/a | 67.45 | -101.80 |
| 37 | EKALAYAVA | NSE-NIFTY-30Jun26-23900-CE (strike 23900) | CE | ITM2 | 2026-06-30 10:00 | 74.20 | OPEN at period end 2026-09-25 | n/a | 55.80 | -74.15 |
| 38 | EKALAYAVA | NSE-NIFTY-14Jul26-24000-PE (strike 24000) | PE | ITM2 | 2026-07-09 12:30 | 113.65 | OPEN at period end 2026-09-25 | n/a | 71.35 | -15.60 |
| 39 | EKALAYAVA | NSE-NIFTY-14Jul26-24050-PE (strike 24050) | PE | ITM3 | 2026-07-09 12:30 | 135.80 | OPEN at period end 2026-09-25 | n/a | 79.40 | -18.15 |
| 40 | EKALAYAVA | NSE-NIFTY-14Jul26-24200-PE (strike 24200) | PE | ITM2 | 2026-07-10 10:25 | 116.20 | OPEN at period end 2026-09-25 | n/a | 13.70 | -34.30 |
| 41 | EKALAYAVA | NSE-NIFTY-14Jul26-24250-PE (strike 24250) | PE | ITM3 | 2026-07-10 10:25 | 142.00 | OPEN at period end 2026-09-25 | n/a | 17.65 | -38.00 |
| 42 | EKALAYAVA | NSE-NIFTY-14Jul26-24100-PE (strike 24100) | PE | ITM2 | 2026-07-13 11:40 | 88.95 | OPEN at period end 2026-09-25 | n/a | -0.20 | -51.20 |
| 43 | EKALAYAVA | NSE-NIFTY-14Jul26-24150-PE (strike 24150) | PE | ITM3 | 2026-07-13 11:40 | 114.15 | OPEN at period end 2026-09-25 | n/a | 0.10 | -64.95 |
| 44 | EKALAYAVA | NSE-NIFTY-21Jul26-24650-PE (strike 24650) | PE | ITM2 | 2026-07-17 10:00 | 475.85 | OPEN at period end 2026-09-25 | n/a | 13.05 | -150.85 |
| 45 | EKALAYAVA | NSE-NIFTY-28Jul26-24000-CE (strike 24000) | CE | ITM3 | 2026-07-22 10:50 | 160.25 | OPEN at period end 2026-09-25 | n/a | 13.15 | -25.55 |
| 46 | EKALAYAVA | NSE-NIFTY-28Jul26-24050-CE (strike 24050) | CE | ITM2 | 2026-07-22 10:50 | 135.55 | OPEN at period end 2026-09-25 | n/a | 11.45 | -23.20 |
| 47 | EKALAYAVA | NSE-NIFTY-04Aug26-24300-PE (strike 24300) | PE | ITM2 | 2026-07-29 09:55 | 191.10 | OPEN at period end 2026-09-25 | n/a | 0.30 | -45.60 |
| 48 | EKALAYAVA | NSE-NIFTY-04Aug26-24400-PE (strike 24400) | PE | ITM3 | 2026-07-29 09:55 | 255.55 | OPEN at period end 2026-09-25 | n/a | 1.45 | -53.90 |
| 49 | EKALAYAVA | NSE-NIFTY-04Aug26-24400-PE (strike 24400) | PE | ITM2 | 2026-07-30 09:40 | 214.95 | OPEN at period end 2026-09-25 | n/a | 22.45 | -64.05 |
| 50 | EKALAYAVA | NSE-NIFTY-04Aug26-24450-PE (strike 24450) | PE | ITM3 | 2026-07-30 09:40 | 252.30 | OPEN at period end 2026-09-25 | n/a | 24.55 | -71.90 |
| 51 | EKALAYAVA | NSE-NIFTY-04Aug26-24650-PE (strike 24650) | PE | ITM2 | 2026-08-03 12:35 | 99.75 | OPEN at period end 2026-09-25 | n/a | 17.60 | -17.35 |
| 52 | EKALAYAVA | NSE-NIFTY-04Aug26-24750-PE (strike 24750) | PE | ITM3 | 2026-08-03 12:35 | 178.50 | OPEN at period end 2026-09-25 | n/a | 21.40 | -17.35 |
| 53 | EKALAYAVA | NSE-NIFTY-04Aug26-24450-CE (strike 24450) | CE | ITM3 | 2026-08-04 09:45 | 180.65 | OPEN at period end 2026-09-25 | n/a | 10.35 | -144.15 |
| 54 | EKALAYAVA | NSE-NIFTY-11Aug26-24400-CE (strike 24400) | CE | ITM3 | 2026-08-11 12:40 | 80.85 | OPEN at period end 2026-09-25 | n/a | 22.15 | -37.75 |
| 55 | EKALAYAVA | NSE-NIFTY-11Aug26-24450-CE (strike 24450) | CE | ITM2 | 2026-08-11 12:40 | 49.30 | OPEN at period end 2026-09-25 | n/a | 12.10 | -39.45 |
| 56 | EKALAYAVA | NSE-NIFTY-18Aug26-24200-CE (strike 24200) | CE | ITM3 | 2026-08-12 10:30 | 285.30 | OPEN at period end 2026-09-25 | n/a | 20.20 | -72.85 |
| 57 | EKALAYAVA | NSE-NIFTY-18Aug26-24300-CE (strike 24300) | CE | ITM2 | 2026-08-12 10:30 | 212.80 | OPEN at period end 2026-09-25 | n/a | 17.80 | -62.15 |
| 58 | EKALAYAVA | NSE-NIFTY-25Aug26-24050-CE (strike 24050) | CE | ITM3 | 2026-08-19 09:50 | 176.35 | OPEN at period end 2026-09-25 | n/a | 5.95 | -36.60 |
| 59 | EKALAYAVA | NSE-NIFTY-25Aug26-24100-CE (strike 24100) | CE | ITM2 | 2026-08-19 09:50 | 146.55 | OPEN at period end 2026-09-25 | n/a | 5.05 | -33.10 |
| 60 | EKALAYAVA | NSE-NIFTY-25Aug26-24300-PE (strike 24300) | PE | ITM2 | 2026-08-20 10:35 | 114.95 | OPEN at period end 2026-09-25 | n/a | 4.50 | -39.25 |
| 61 | EKALAYAVA | NSE-NIFTY-25Aug26-24350-PE (strike 24350) | PE | ITM3 | 2026-08-20 10:35 | 144.60 | OPEN at period end 2026-09-25 | n/a | 5.40 | -48.10 |
| 62 | EKALAYAVA | NSE-NIFTY-25Aug26-24150-CE (strike 24150) | CE | ITM3 | 2026-08-21 10:20 | 176.65 | OPEN at period end 2026-09-25 | n/a | 14.65 | -14.15 |
| 63 | EKALAYAVA | NSE-NIFTY-25Aug26-24200-CE (strike 24200) | CE | ITM2 | 2026-08-21 10:20 | 140.45 | OPEN at period end 2026-09-25 | n/a | 12.55 | -13.45 |
| 64 | EKALAYAVA | NSE-NIFTY-25Aug26-24150-CE (strike 24150) | CE | ITM3 | 2026-08-24 13:25 | 86.40 | OPEN at period end 2026-09-25 | n/a | 10.15 | -11.70 |
| 65 | EKALAYAVA | NSE-NIFTY-25Aug26-24200-CE (strike 24200) | CE | ITM2 | 2026-08-24 14:30 | 62.70 | OPEN at period end 2026-09-25 | n/a | 3.20 | -5.45 |
| 66 | EKALAYAVA | NSE-NIFTY-01Sep26-24200-CE (strike 24200) | CE | ITM2 | 2026-08-27 11:50 | 114.05 | OPEN at period end 2026-09-25 | n/a | 25.70 | -27.20 |
| 67 | EKALAYAVA | NSE-NIFTY-01Sep26-24150-CE (strike 24150) | CE | ITM3 | 2026-08-27 11:55 | 145.00 | OPEN at period end 2026-09-25 | n/a | 28.00 | -34.20 |
| 68 | EKALAYAVA | NSE-NIFTY-08Sep26-24000-PE (strike 24000) | PE | ITM2 | 2026-09-04 10:10 | 109.55 | OPEN at period end 2026-09-25 | n/a | 7.45 | -24.55 |
| 69 | EKALAYAVA | NSE-NIFTY-08Sep26-24050-PE (strike 24050) | PE | ITM3 | 2026-09-04 10:10 | 137.00 | OPEN at period end 2026-09-25 | n/a | 10.45 | -28.85 |
| 70 | EKALAYAVA | NSE-NIFTY-08Sep26-23750-CE (strike 23750) | CE | ITM3 | 2026-09-07 11:40 | 115.05 | OPEN at period end 2026-09-25 | n/a | 11.50 | -36.55 |
| 71 | EKALAYAVA | NSE-NIFTY-08Sep26-23800-CE (strike 23800) | CE | ITM2 | 2026-09-07 11:40 | 85.30 | OPEN at period end 2026-09-25 | n/a | 7.15 | -31.55 |
| 72 | EKALAYAVA | NSE-NIFTY-08Sep26-23550-CE (strike 23550) | CE | ITM3 | 2026-09-08 10:10 | 179.05 | OPEN at period end 2026-09-25 | n/a | 6.60 | -157.50 |
| 73 | EKALAYAVA | NSE-NIFTY-08Sep26-23600-CE (strike 23600) | CE | ITM2 | 2026-09-08 10:10 | 132.80 | OPEN at period end 2026-09-25 | n/a | 7.40 | -130.30 |
| 74 | EKALAYAVA | NSE-NIFTY-15Sep26-23100-CE (strike 23100) | CE | ITM2 | 2026-09-10 14:45 | 383.00 | OPEN at period end 2026-09-25 | n/a | 5.00 | -43.00 |
| 75 | EKALAYAVA | NSE-NIFTY-15Sep26-23500-PE (strike 23500) | PE | ITM2 | 2026-09-11 10:55 | 238.85 | OPEN at period end 2026-09-25 | n/a | 0.50 | -129.80 |
| 76 | EKALAYAVA | NSE-NIFTY-15Sep26-23550-PE (strike 23550) | PE | ITM3 | 2026-09-11 10:55 | 280.55 | OPEN at period end 2026-09-25 | n/a | -0.55 | -141.75 |
| 77 | EKALAYAVA | NSE-NIFTY-15Sep26-23350-CE (strike 23350) | CE | ITM3 | 2026-09-15 15:10 | 9.25 | OPEN at period end 2026-09-25 | n/a | 2.45 | -9.20 |
| 78 | EKALAYAVA | NSE-NIFTY-15Sep26-23450-CE (strike 23450) | CE | ITM2 | 2026-09-15 15:10 | 3.70 | OPEN at period end 2026-09-25 | n/a | 1.25 | -3.65 |
| 79 | EKALAYAVA | NSE-NIFTY-22Sep26-23450-PE (strike 23450) | PE | ITM2 | 2026-09-17 10:30 | 215.75 | OPEN at period end 2026-09-25 | n/a | 58.25 | -61.50 |
| 80 | EKALAYAVA | NSE-NIFTY-22Sep26-23500-PE (strike 23500) | PE | ITM3 | 2026-09-17 10:30 | 250.55 | OPEN at period end 2026-09-25 | n/a | 62.65 | -67.55 |
| 81 | EKALAYAVA | NSE-NIFTY-22Sep26-23500-PE (strike 23500) | PE | ITM2 | 2026-09-21 10:00 | 147.35 | OPEN at period end 2026-09-25 | n/a | 12.35 | -63.20 |
| 82 | EKALAYAVA | NSE-NIFTY-22Sep26-23600-PE (strike 23600) | PE | ITM3 | 2026-09-21 10:00 | 231.30 | OPEN at period end 2026-09-25 | n/a | 14.70 | -78.15 |
| 83 | EKALAYAVA | NSE-NIFTY-22Sep26-23000-CE (strike 23000) | CE | ITM3 | 2026-09-22 09:40 | 458.90 | OPEN at period end 2026-09-25 | n/a | 9.95 | -178.65 |
| 84 | EKALAYAVA | NSE-NIFTY-22Sep26-23250-CE (strike 23250) | CE | ITM2 | 2026-09-22 09:40 | 211.85 | OPEN at period end 2026-09-25 | n/a | 9.15 | -152.80 |
| 85 | EKALAYAVA | NSE-NIFTY-29Sep26-23450-PE (strike 23450) | PE | ITM2 | 2026-09-23 09:50 | 157.50 | OPEN at period end 2026-09-25 | n/a | 2.10 | -62.95 |
| 86 | EKALAYAVA | NSE-NIFTY-29Sep26-23500-PE (strike 23500) | PE | ITM3 | 2026-09-23 09:50 | 188.00 | OPEN at period end 2026-09-25 | n/a | 1.75 | -71.20 |
| 87 | EKALAYAVA | NSE-NIFTY-29Sep26-23100-CE (strike 23100) | CE | ITM3 | 2026-09-24 10:05 | 210.00 | OPEN at period end 2026-09-25 | n/a | 4.90 | -87.10 |
| 88 | EKALAYAVA | NSE-NIFTY-29Sep26-23150-CE (strike 23150) | CE | ITM2 | 2026-09-24 10:05 | 175.20 | OPEN at period end 2026-09-25 | n/a | 4.10 | -76.05 |

## 7. Profit concentration

- Net reported points are **4,077.00**. Gross positive points from TARGET outcomes are **5,037.50**; the ten largest target trades contribute **1,045.50 (20.8%)** of those gross positive points.
- Largest target trade: **136.45 points** on 2026-05-18 (EKALAYAVA, CE ITM3); 2.7% of gross positive points.
- Largest positive net day: **2026-05-05 (261.60 points)**, 6.4% of total net points. Top five positive net days sum to 1,081.25 points (26.5% of net points).
- Largest positive net month: **2026-05 (1,361.90 points)**, 33.4% of total net points. Month-level net points are: 2026-04: 322.30; 2026-05: 1,361.90; 2026-06: 734.85; 2026-07: 331.05; 2026-08: 729.65; 2026-09: 597.25.

Concentration ratios can exceed 100% when other trades/days/months subtract points. They describe this finite sample and are not evidence of persistence.

## 8. Data-quality impact

- Missing/partial option coverage is specifically on selected CE/PE ITM2/ITM3 contract-days; underlying coverage has no missing requested-session candles in the source report.
- On a missing contract-day there are no candles for the selected contract, hence entries and outcome paths on that contract-day could not be evaluated. On partial days, absent intervals may omit signals or hide the order of target/stop touches; the source does not identify a measurable counterfactual for these effects.
- Ten dates marked unusable and five marked partially usable are the exact date groups from baseline metadata. Counts and metrics elsewhere in this diagnostic remain the baseline’s observed values, not completeness-adjusted estimates.
- The 88 OPEN Ekalayava events remain unresolved in the baseline. Missing/partial data is not used to synthesize their exit, holding duration, or end mark.
- Full missing/partial interval timestamps and per-contract quality details remain in the referenced JSON source. No data was rewritten by this diagnostic.


### Exact contract-day interval inventory

The baseline’s interval inventory has 43 affected contract-days: 18 with all 75 session intervals missing and 25 partial. This table lists each affected date, selected contract, and missing-bar count (the timestamps themselves remain in the source JSON).

| Date | Option | ITM | Contract | Missing intervals |
|---|---|---:|---|---:|
| 2026-07-01 | CE | 2 | NSE-NIFTY-07Jul26-22550-CE | 75 |
| 2026-07-01 | CE | 3 | NSE-NIFTY-07Jul26-22400-CE | 75 |
| 2026-07-01 | PE | 2 | NSE-NIFTY-07Jul26-25900-PE | 75 |
| 2026-07-01 | PE | 3 | NSE-NIFTY-07Jul26-25950-PE | 75 |
| 2026-07-02 | CE | 2 | NSE-NIFTY-07Jul26-22550-CE | 75 |
| 2026-07-02 | CE | 3 | NSE-NIFTY-07Jul26-22400-CE | 75 |
| 2026-07-02 | PE | 2 | NSE-NIFTY-07Jul26-25900-PE | 75 |
| 2026-07-02 | PE | 3 | NSE-NIFTY-07Jul26-25950-PE | 75 |
| 2026-07-03 | CE | 2 | NSE-NIFTY-07Jul26-22550-CE | 75 |
| 2026-07-03 | CE | 3 | NSE-NIFTY-07Jul26-22400-CE | 75 |
| 2026-07-03 | PE | 2 | NSE-NIFTY-07Jul26-25900-PE | 75 |
| 2026-07-03 | PE | 3 | NSE-NIFTY-07Jul26-25950-PE | 75 |
| 2026-07-06 | CE | 2 | NSE-NIFTY-07Jul26-22550-CE | 75 |
| 2026-07-06 | CE | 3 | NSE-NIFTY-07Jul26-22400-CE | 75 |
| 2026-07-06 | PE | 2 | NSE-NIFTY-07Jul26-25900-PE | 75 |
| 2026-07-06 | PE | 3 | NSE-NIFTY-07Jul26-25950-PE | 75 |
| 2026-07-07 | CE | 2 | NSE-NIFTY-07Jul26-22550-CE | 74 |
| 2026-07-07 | CE | 3 | NSE-NIFTY-07Jul26-22400-CE | 74 |
| 2026-07-07 | PE | 2 | NSE-NIFTY-07Jul26-25900-PE | 74 |
| 2026-07-07 | PE | 3 | NSE-NIFTY-07Jul26-25950-PE | 74 |
| 2026-07-15 | CE | 2 | NSE-NIFTY-21Jul26-22500-CE | 64 |
| 2026-07-15 | CE | 3 | NSE-NIFTY-21Jul26-22000-CE | 75 |
| 2026-07-15 | PE | 2 | NSE-NIFTY-21Jul26-24650-PE | 4 |
| 2026-07-15 | PE | 3 | NSE-NIFTY-21Jul26-24850-PE | 41 |
| 2026-07-16 | CE | 2 | NSE-NIFTY-21Jul26-22500-CE | 65 |
| 2026-07-16 | CE | 3 | NSE-NIFTY-21Jul26-22000-CE | 75 |
| 2026-07-16 | PE | 2 | NSE-NIFTY-21Jul26-24650-PE | 1 |
| 2026-07-16 | PE | 3 | NSE-NIFTY-21Jul26-24850-PE | 40 |
| 2026-07-17 | CE | 2 | NSE-NIFTY-21Jul26-22500-CE | 66 |
| 2026-07-17 | CE | 3 | NSE-NIFTY-21Jul26-22000-CE | 74 |
| 2026-07-17 | PE | 3 | NSE-NIFTY-21Jul26-24850-PE | 6 |
| 2026-07-20 | CE | 2 | NSE-NIFTY-21Jul26-22500-CE | 53 |
| 2026-07-20 | CE | 3 | NSE-NIFTY-21Jul26-22000-CE | 67 |
| 2026-07-20 | PE | 3 | NSE-NIFTY-21Jul26-24850-PE | 13 |
| 2026-07-21 | CE | 2 | NSE-NIFTY-21Jul26-22500-CE | 65 |
| 2026-07-21 | CE | 3 | NSE-NIFTY-21Jul26-22000-CE | 67 |
| 2026-07-21 | PE | 3 | NSE-NIFTY-21Jul26-24850-PE | 35 |
| 2026-08-04 | PE | 2 | NSE-NIFTY-04Aug26-25050-PE | 2 |
| 2026-08-04 | PE | 3 | NSE-NIFTY-04Aug26-25100-PE | 3 |
| 2026-09-10 | CE | 3 | NSE-NIFTY-15Sep26-23050-CE | 1 |
| 2026-09-16 | CE | 3 | NSE-NIFTY-22Sep26-22750-CE | 6 |
| 2026-09-17 | CE | 3 | NSE-NIFTY-22Sep26-22750-CE | 6 |
| 2026-09-21 | CE | 3 | NSE-NIFTY-22Sep26-22950-CE | 3 |

## 9. Descriptive interpretation

- The event ledger records 417 setups over 98 dates with setups; the defined requested window has 106 sessions.
- Recorded resolved points are uneven across months: largest month 2026-05 contributes 1,361.90 net points, while some months have materially smaller totals. The sample’s aggregate should therefore be read with the concentration and data-completeness caveats above.
- The recorded outcome mix contains 131 TARGET, 107 SL, 88 OPEN and 91 skipped entries. OPEN points are unmarked, while skipped cases are not trades with realized P&L.
- Average MFE (21.79) and average MAE (-22.38) are excursion summaries, not realized return estimates; mean hold (53.51 min) reflects only observations for which the canonical source recorded holding duration.
- The source itself states “INSUFFICIENT OUT-OF-SAMPLE DATA; no strategy changes evaluated.” Nothing here ranks the strategies or establishes that either will generalize.

## 10. Next experiments (questions only; preserve baseline rules)

1. After obtaining a separately verified complete data set, how do event counts and outcome summaries change for the dates/contracts currently marked missing or partial, without changing strategy rules?
2. For the 88 Ekalayava OPEN records, what is the canonical intended exit/marking convention in the existing strategy specification, and how would reporting unresolved events separately from realized outcomes affect summaries? Do not invent that convention in this baseline.
3. Are the concentration observations robust across additional non-overlapping historical windows, with the same locked rules and reporting definitions?
4. Do CE/PE, ITM2/ITM3, entry-hour, weekday, or month differences persist on fully usable days in a larger out-of-sample sample, after controlling for differing event counts?
5. How sensitive are descriptive results to missing-data exclusions when comparing only dates with all four selected contracts complete, while leaving the strategy itself unchanged?
6. Can the source data validator independently confirm the 75-candle session requirement and missing-interval inventory against raw files, without filling gaps?

## Provenance and safety

- Source report: `data/reports/baseline_v1_requested_period.json` (baseline ID BASELINE-V1, strategy version baseline-v1).
- Source validation status: INSUFFICIENT OUT-OF-SAMPLE DATA; no strategy changes evaluated.
- Source safety flags: `EXECUTION_ALLOWED=False`, `PAPER_ONLY=True`, order placement/modification called=`False`.
- This document was generated from local existing report values only. It contains no credentials, API keys, or tokens.

