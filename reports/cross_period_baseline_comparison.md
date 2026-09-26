# Cross-period baseline comparison

**Period A:** 2026-04-25 → 2026-09-25. **Period B:** 2026-01-01 → 2026-04-24. The requested windows do not overlap. This compares preserved BASELINE-V1 event outputs. The canonical contract selector and strategies were used unchanged; no optimization or strategy-rule changes were made. Level-to-Level point sums are gross option-premium points and exclude costs, slippage, position sizing, and capital returns.

## A. Period A results

Source window 2026-04-27 to 2026-09-25; 106 underlying dates, 417 setups.

### Level-to-Level

| Measure | Period A |
|---|---:|
| Setups | 247.00 |
| Valid | 156.00 |
| Skipped | 91.00 |
| Targets | 49.00 |
| SL | 107.00 |
| Open / unresolved | 0.00 |
| Ambiguous | 0.00 |
| Resolved points | 502.40 |
| Mean points per resolved trade | 3.22 |
| Median points per resolved trade | -4.00 |
| Mean MFE | 11.48 |
| Mean MAE | -7.53 |
| Max drawdown (resolved L2L, timestamp then symbol) | 208.25 |

### Ekalayava

| Measure | Period A |
|---|---:|
| Setups | 170.00 |
| Valid | 170.00 |
| Skipped | 0.00 |
| Targets | 82.00 |
| SL | 0.00 |
| Open / unresolved | 88.00 |
| Ambiguous | 0.00 |
| Mean MFE | 36.76 |
| Mean MAE | -43.95 |
| Mean duration for TARGET events (minutes) | 106.04 |

## B. Period B results

Official schedule: 76 sessions after seven weekday closures and including Sunday 2026-02-01. Groww underlying matched all 76 session dates; BASELINE-V1 counted 313 setups.

### Level-to-Level

| Measure | Period B |
|---|---:|
| Setups | 181.00 |
| Valid | 92.00 |
| Skipped | 89.00 |
| Targets | 23.00 |
| SL | 68.00 |
| Open / unresolved | 0.00 |
| Ambiguous | 1.00 |
| Resolved points | -333.70 |
| Mean points per resolved trade | -3.67 |
| Median points per resolved trade | -8.35 |
| Mean MFE | 9.16 |
| Mean MAE | -8.86 |
| Max drawdown (resolved L2L, timestamp then symbol) | 432.75 |

### Ekalayava

| Measure | Period B |
|---|---:|
| Setups | 132.00 |
| Valid | 132.00 |
| Skipped | 0.00 |
| Targets | 58.00 |
| SL | 0.00 |
| Open / unresolved | 74.00 |
| Ambiguous | 0.00 |
| Mean MFE | 42.84 |
| Mean MAE | -47.91 |
| Mean duration for TARGET events (minutes) | 73.88 |

Period A Ekalayava target distance (TARGET events only): mean 43.59, median 34.97 points. Target hits are frequency observations, not realized P&L.

Period B Ekalayava target distance (TARGET events only): mean 52.11, median 38.72 points. Target hits are frequency observations, not realized P&L.

## C. Cross-period comparison

### Setup outcomes

| Strategy | Period | Setups | Valid/non-skipped | Skipped | Target | SL | Open | Ambiguous |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LEVEL_TO_LEVEL | A | 247 | 156 | 91 | 49 | 107 | 0 | 0 |
| EKALAYAVA | A | 170 | 170 | 0 | 82 | 0 | 88 | 0 |
| LEVEL_TO_LEVEL | B | 181 | 92 | 89 | 23 | 68 | 0 | 1 |
| EKALAYAVA | B | 132 | 132 | 0 | 58 | 0 | 74 | 0 |

### CE/PE, ITM2/ITM3 breakdowns

#### Level-to-Level by CE/PE
| Category | A setups | A target/SL/open | A L2L points | B setups | B target/SL/open | B L2L points |
|---|---:|---:|---:|---:|---:|---:|
| CE | 124 | 23/54/0 | 181.35 | 93 | 9/41/0 | -256.70 |
| PE | 123 | 26/53/0 | 321.05 | 88 | 14/27/0 | -77.00 |

#### Level-to-Level by ITM rank
| Category | A setups | A target/SL/open | A L2L points | B setups | B target/SL/open | B L2L points |
|---|---:|---:|---:|---:|---:|---:|
| 2 | 125 | 24/54/0 | 187.85 | 93 | 12/38/0 | -306.05 |
| 3 | 122 | 25/53/0 | 314.55 | 88 | 11/30/0 | -27.65 |

#### Ekalayava by CE/PE (no P&L)
| Category | A setups | A target/SL/open | A L2L points | B setups | B target/SL/open | B L2L points |
|---|---:|---:|---:|---:|---:|---:|
| CE | 79 | 42/0/37 | 1891.40 | 72 | 31/0/41 | 1607.40 |
| PE | 91 | 40/0/51 | 1683.20 | 60 | 27/0/33 | 1415.15 |

#### Ekalayava by ITM rank (no P&L)
| Category | A setups | A target/SL/open | A L2L points | B setups | B target/SL/open | B L2L points |
|---|---:|---:|---:|---:|---:|---:|
| 2 | 87 | 41/0/46 | 1676.75 | 69 | 29/0/40 | 1473.30 |
| 3 | 83 | 41/0/42 | 1897.85 | 63 | 29/0/34 | 1549.25 |

### Entry-hour distribution (IST)

| Period | Strategy | Bucket | Setups | Target | SL | Open | L2L resolved points |
|---|---|---|---|---:|---:|---:|---:|
| A | LEVEL_TO_LEVEL | 09:00 | 187 | 33 | 80 | 0 | 210.45 |
| A | LEVEL_TO_LEVEL | 10:00 | 57 | 16 | 26 | 0 | 292.10 |
| A | LEVEL_TO_LEVEL | 11:00 | 3 | 0 | 1 | 0 | -0.15 |
| A | LEVEL_TO_LEVEL | 12:00 | 0 | 0 | 0 | 0 | n/a |
| A | LEVEL_TO_LEVEL | 13:00 | 0 | 0 | 0 | 0 | n/a |
| A | LEVEL_TO_LEVEL | 14:00 | 0 | 0 | 0 | 0 | n/a |
| A | LEVEL_TO_LEVEL | 15:00 | 0 | 0 | 0 | 0 | n/a |
| A | EKALAYAVA | 09:00 | 48 | 29 | 0 | 19 | n/a |
| A | EKALAYAVA | 10:00 | 75 | 33 | 0 | 42 | n/a |
| A | EKALAYAVA | 11:00 | 28 | 15 | 0 | 13 | n/a |
| A | EKALAYAVA | 12:00 | 12 | 5 | 0 | 7 | n/a |
| A | EKALAYAVA | 13:00 | 3 | 0 | 0 | 3 | n/a |
| A | EKALAYAVA | 14:00 | 2 | 0 | 0 | 2 | n/a |
| A | EKALAYAVA | 15:00 | 2 | 0 | 0 | 2 | n/a |
| B | LEVEL_TO_LEVEL | 09:00 | 148 | 18 | 56 | 0 | -282.15 |
| B | LEVEL_TO_LEVEL | 10:00 | 32 | 5 | 11 | 0 | -21.55 |
| B | LEVEL_TO_LEVEL | 11:00 | 1 | 0 | 1 | 0 | -30.00 |
| B | LEVEL_TO_LEVEL | 12:00 | 0 | 0 | 0 | 0 | n/a |
| B | LEVEL_TO_LEVEL | 13:00 | 0 | 0 | 0 | 0 | n/a |
| B | LEVEL_TO_LEVEL | 14:00 | 0 | 0 | 0 | 0 | n/a |
| B | EKALAYAVA | 09:00 | 40 | 28 | 0 | 12 | n/a |
| B | EKALAYAVA | 10:00 | 58 | 19 | 0 | 39 | n/a |
| B | EKALAYAVA | 11:00 | 21 | 8 | 0 | 13 | n/a |
| B | EKALAYAVA | 12:00 | 6 | 3 | 0 | 3 | n/a |
| B | EKALAYAVA | 13:00 | 3 | 0 | 0 | 3 | n/a |
| B | EKALAYAVA | 14:00 | 4 | 0 | 0 | 4 | n/a |

### Day-of-week distribution

| Period | Strategy | Bucket | Setups | Target | SL | Open | L2L resolved points |
|---|---|---|---|---:|---:|---:|---:|
| A | LEVEL_TO_LEVEL | Friday | 38 | 6 | 24 | 0 | -5.60 |
| A | LEVEL_TO_LEVEL | Monday | 56 | 10 | 28 | 0 | -48.50 |
| A | LEVEL_TO_LEVEL | Thursday | 43 | 5 | 17 | 0 | 36.60 |
| A | LEVEL_TO_LEVEL | Tuesday | 59 | 16 | 18 | 0 | 240.25 |
| A | LEVEL_TO_LEVEL | Wednesday | 51 | 12 | 20 | 0 | 279.65 |
| A | EKALAYAVA | Friday | 27 | 15 | 0 | 12 | n/a |
| A | EKALAYAVA | Monday | 35 | 15 | 0 | 20 | n/a |
| A | EKALAYAVA | Thursday | 36 | 17 | 0 | 19 | n/a |
| A | EKALAYAVA | Tuesday | 38 | 20 | 0 | 18 | n/a |
| A | EKALAYAVA | Wednesday | 34 | 15 | 0 | 19 | n/a |
| B | LEVEL_TO_LEVEL | Friday | 37 | 4 | 16 | 0 | -136.45 |
| B | LEVEL_TO_LEVEL | Monday | 37 | 7 | 10 | 0 | 36.85 |
| B | LEVEL_TO_LEVEL | Sunday | 1 | 0 | 1 | 0 | -15.85 |
| B | LEVEL_TO_LEVEL | Thursday | 35 | 3 | 17 | 0 | -135.80 |
| B | LEVEL_TO_LEVEL | Tuesday | 35 | 3 | 9 | 0 | -42.80 |
| B | LEVEL_TO_LEVEL | Wednesday | 36 | 6 | 15 | 0 | -39.65 |
| B | EKALAYAVA | Friday | 28 | 11 | 0 | 17 | n/a |
| B | EKALAYAVA | Monday | 31 | 17 | 0 | 14 | n/a |
| B | EKALAYAVA | Sunday | 2 | 2 | 0 | 0 | n/a |
| B | EKALAYAVA | Thursday | 25 | 9 | 0 | 16 | n/a |
| B | EKALAYAVA | Tuesday | 22 | 8 | 0 | 14 | n/a |
| B | EKALAYAVA | Wednesday | 24 | 11 | 0 | 13 | n/a |

### Monthly distribution

| Month | Period | L2L setups | Targets / SL | Resolved points | Ekal setups | Targets / open |
|---|---|---:|---:|---:|---:|---:|
| 2026-01 | A | 0 | 0 / 0 | n/a | 0 | 0 / 0 |
| 2026-01 | B | 55 | 11 / 21 | 47.35 | 35 | 20 / 15 |
| 2026-02 | A | 0 | 0 / 0 | n/a | 0 | 0 / 0 |
| 2026-02 | B | 49 | 6 / 9 | 41.60 | 38 | 14 / 24 |
| 2026-03 | A | 0 | 0 / 0 | n/a | 0 | 0 / 0 |
| 2026-03 | B | 41 | 3 / 21 | -229.55 | 32 | 18 / 14 |
| 2026-04 | A | 10 | 2 / 4 | -6.60 | 8 | 5 / 3 |
| 2026-04 | B | 36 | 3 / 17 | -193.10 | 27 | 6 / 21 |
| 2026-05 | A | 52 | 14 / 14 | 298.00 | 34 | 19 / 15 |
| 2026-05 | B | 0 | 0 / 0 | n/a | 0 | 0 / 0 |
| 2026-06 | A | 52 | 6 / 33 | -62.10 | 36 | 17 / 19 |
| 2026-06 | B | 0 | 0 / 0 | n/a | 0 | 0 / 0 |
| 2026-07 | A | 39 | 3 / 23 | -69.25 | 25 | 12 / 13 |
| 2026-07 | B | 0 | 0 / 0 | n/a | 0 | 0 / 0 |
| 2026-08 | A | 51 | 10 / 19 | 31.95 | 34 | 17 / 17 |
| 2026-08 | B | 0 | 0 / 0 | n/a | 0 | 0 / 0 |
| 2026-09 | A | 43 | 14 / 14 | 310.40 | 33 | 12 / 21 |
| 2026-09 | B | 0 | 0 / 0 | n/a | 0 | 0 / 0 |

### MFE, MAE, and observed holding time

| Strategy | Period | Setups | MFE mean / median | MAE mean / median | Hold minutes mean / median, when exit exists |
|---|---|---:|---:|---:|---:|
| LEVEL_TO_LEVEL | A | 247 | 11.48 / 3.90 | -7.53 / -3.80 | 25.90 / 10.00 |
| LEVEL_TO_LEVEL | B | 181 | 9.16 / 0.00 | -8.86 / 0.00 | 15.92 / 5.00 |
| EKALAYAVA | A | 170 | 36.76 / 23.73 | -43.95 / -36.08 | 106.04 / 85.00 |
| EKALAYAVA | B | 132 | 42.84 / 29.35 | -47.91 / -36.80 | 73.88 / 45.00 |

OPEN Ekalayava rows have MFE/MAE through available data but no exit time, exit price, or holding duration.

### Results by data-usability class

| Period | Day class | Days | L2L setups | Target / SL | L2L resolved points | Ekal setups | Target / open |
|---|---|---:|---:|---:|---:|---:|---:|
| A | fully usable | 91 | 233 | 46 / 104 | 431.10 | 155 | 74 / 81 |
| A | partially usable | 5 | 11 | 3 / 3 | 71.30 | 13 | 7 / 6 |
| A | unusable | 10 | 3 | 0 / 0 | n/a | 2 | 1 / 1 |
| B | fully usable | 58 | 149 | 20 / 54 | -102.05 | 107 | 46 / 61 |
| B | partially usable | 14 | 29 | 3 / 11 | -203.40 | 22 | 10 / 12 |
| B | unusable | 4 | 3 | 0 / 3 | -28.25 | 3 | 2 / 1 |

### Level-to-Level point concentration (resolved TARGET/SL events only)

| Period | Resolved | Winners / losers | Gross gains | Gross losses | Top-five winner share of gross gains | Top-five positive-day share |
|---|---:|---:|---:|---:|---:|---:|
| A | 156 | 49 / 107 | 1462.90 | -960.50 | 22.4% | 45.7% |
| B | 91 | 22 / 69 | 625.20 | -958.90 | 46.5% | 72.1% |

This excludes Ekalayava target points, open trades, and skipped entries. It describes concentration, not an overall strategy ranking.

## Supplement: daily and weekly results

Level-to-Level resolved points include TARGET and SL events only; skipped and ambiguous events are not counted as realized points. Ekalayava columns report setup and target/open counts only, not P&L.

### Daily

| Period | Date | L2L setups | Target | SL | Skipped | Ambiguous | L2L resolved points | Ekal setups | Ekal target / open |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 2026-04-27 | 4 | 2 | 2 | 0 | 0 | 5.15 | 2 | 1 / 1 |
| A | 2026-04-28 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-04-29 | 2 | 0 | 2 | 0 | 0 | -11.75 | 2 | 0 / 2 |
| A | 2026-04-30 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-05-04 | 4 | 0 | 2 | 2 | 0 | -79.50 | 2 | 2 / 0 |
| A | 2026-05-05 | 4 | 1 | 1 | 2 | 0 | 89.75 | 4 | 3 / 1 |
| A | 2026-05-06 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-05-07 | 2 | 0 | 2 | 0 | 0 | -17.45 | 2 | 2 / 0 |
| A | 2026-05-08 | 2 | 1 | 1 | 0 | 0 | 16.10 | 1 | 1 / 0 |
| A | 2026-05-11 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 1 / 1 |
| A | 2026-05-12 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-05-13 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-05-14 | 4 | 2 | 0 | 2 | 0 | 75.65 | 0 | 0 / 0 |
| A | 2026-05-15 | 2 | 0 | 2 | 0 | 0 | -10.95 | 2 | 2 / 0 |
| A | 2026-05-18 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-05-19 | 4 | 4 | 0 | 0 | 0 | 120.45 | 0 | 0 / 0 |
| A | 2026-05-20 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-05-21 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-05-22 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-05-25 | 4 | 2 | 2 | 0 | 0 | 26.95 | 2 | 0 / 2 |
| A | 2026-05-26 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-05-27 | 4 | 2 | 2 | 0 | 0 | 30.00 | 2 | 0 / 2 |
| A | 2026-05-29 | 4 | 2 | 2 | 0 | 0 | 47.00 | 1 | 0 / 1 |
| A | 2026-06-01 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-06-02 | 2 | 0 | 1 | 1 | 0 | -0.70 | 2 | 0 / 2 |
| A | 2026-06-03 | 2 | 0 | 1 | 1 | 0 | -0.50 | 2 | 2 / 0 |
| A | 2026-06-04 | 2 | 0 | 2 | 0 | 0 | -26.15 | 2 | 0 / 2 |
| A | 2026-06-05 | 2 | 0 | 2 | 0 | 0 | -19.15 | 0 | 0 / 0 |
| A | 2026-06-08 | 2 | 0 | 2 | 0 | 0 | -12.50 | 2 | 0 / 2 |
| A | 2026-06-09 | 4 | 0 | 4 | 0 | 0 | -49.70 | 2 | 2 / 0 |
| A | 2026-06-10 | 2 | 0 | 2 | 0 | 0 | -0.90 | 2 | 1 / 1 |
| A | 2026-06-11 | 2 | 0 | 2 | 0 | 0 | -35.95 | 2 | 0 / 2 |
| A | 2026-06-12 | 2 | 0 | 2 | 0 | 0 | -8.05 | 0 | 0 / 0 |
| A | 2026-06-15 | 4 | 0 | 3 | 1 | 0 | -24.50 | 2 | 2 / 0 |
| A | 2026-06-16 | 3 | 1 | 2 | 0 | 0 | 19.20 | 2 | 0 / 2 |
| A | 2026-06-17 | 4 | 2 | 0 | 2 | 0 | 19.70 | 0 | 0 / 0 |
| A | 2026-06-18 | 4 | 1 | 2 | 1 | 0 | 43.85 | 4 | 4 / 0 |
| A | 2026-06-19 | 1 | 0 | 1 | 0 | 0 | -12.40 | 2 | 2 / 0 |
| A | 2026-06-22 | 2 | 0 | 2 | 0 | 0 | -7.95 | 2 | 0 / 2 |
| A | 2026-06-23 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-06-24 | 2 | 0 | 2 | 0 | 0 | -5.15 | 2 | 0 / 2 |
| A | 2026-06-25 | 2 | 0 | 2 | 0 | 0 | -7.45 | 2 | 2 / 0 |
| A | 2026-06-29 | 4 | 2 | 1 | 1 | 0 | 66.20 | 0 | 0 / 0 |
| A | 2026-06-30 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-07-08 | 4 | 0 | 4 | 0 | 0 | -27.70 | 0 | 0 / 0 |
| A | 2026-07-09 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-07-10 | 2 | 0 | 2 | 0 | 0 | -5.40 | 2 | 0 / 2 |
| A | 2026-07-13 | 4 | 0 | 2 | 2 | 0 | -12.65 | 2 | 0 / 2 |
| A | 2026-07-14 | 4 | 1 | 1 | 2 | 0 | 45.80 | 2 | 2 / 0 |
| A | 2026-07-15 | 1 | 0 | 0 | 1 | 0 | 0.00 | 1 | 1 / 0 |
| A | 2026-07-16 | 1 | 0 | 0 | 1 | 0 | 0.00 | 0 | 0 / 0 |
| A | 2026-07-17 | 1 | 0 | 0 | 1 | 0 | 0.00 | 1 | 0 / 1 |
| A | 2026-07-22 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-07-23 | 2 | 0 | 2 | 0 | 0 | -8.15 | 2 | 2 / 0 |
| A | 2026-07-24 | 2 | 0 | 2 | 0 | 0 | -20.10 | 0 | 0 / 0 |
| A | 2026-07-27 | 4 | 2 | 2 | 0 | 0 | 20.40 | 3 | 3 / 0 |
| A | 2026-07-28 | 4 | 0 | 3 | 1 | 0 | -26.00 | 2 | 2 / 0 |
| A | 2026-07-29 | 2 | 0 | 2 | 0 | 0 | -13.30 | 2 | 0 / 2 |
| A | 2026-07-30 | 2 | 0 | 1 | 1 | 0 | -11.90 | 2 | 0 / 2 |
| A | 2026-07-31 | 2 | 0 | 2 | 0 | 0 | -10.25 | 2 | 2 / 0 |
| A | 2026-08-03 | 2 | 0 | 2 | 0 | 0 | -10.25 | 2 | 0 / 2 |
| A | 2026-08-04 | 4 | 2 | 2 | 0 | 0 | 1.10 | 3 | 2 / 1 |
| A | 2026-08-05 | 1 | 0 | 1 | 0 | 0 | -27.40 | 1 | 1 / 0 |
| A | 2026-08-06 | 2 | 2 | 0 | 0 | 0 | 39.05 | 0 | 0 / 0 |
| A | 2026-08-10 | 4 | 0 | 2 | 2 | 0 | -14.40 | 0 | 0 / 0 |
| A | 2026-08-11 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-08-12 | 2 | 0 | 2 | 0 | 0 | -0.85 | 2 | 0 / 2 |
| A | 2026-08-13 | 2 | 0 | 1 | 1 | 0 | -1.40 | 2 | 2 / 0 |
| A | 2026-08-14 | 2 | 0 | 2 | 0 | 0 | -21.25 | 2 | 2 / 0 |
| A | 2026-08-17 | 2 | 0 | 2 | 0 | 0 | -11.85 | 2 | 2 / 0 |
| A | 2026-08-18 | 4 | 2 | 2 | 0 | 0 | -28.95 | 0 | 0 / 0 |
| A | 2026-08-19 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-08-20 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-08-21 | 2 | 0 | 1 | 1 | 0 | -0.70 | 2 | 0 / 2 |
| A | 2026-08-24 | 4 | 2 | 0 | 2 | 0 | 21.70 | 2 | 0 / 2 |
| A | 2026-08-25 | 4 | 2 | 0 | 2 | 0 | 90.90 | 2 | 2 / 0 |
| A | 2026-08-26 | 4 | 0 | 0 | 4 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-08-27 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-08-28 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| A | 2026-08-31 | 2 | 0 | 2 | 0 | 0 | -3.75 | 2 | 2 / 0 |
| A | 2026-09-01 | 4 | 3 | 1 | 0 | 0 | -5.80 | 1 | 1 / 0 |
| A | 2026-09-02 | 2 | 2 | 0 | 0 | 0 | 74.75 | 0 | 0 / 0 |
| A | 2026-09-03 | 3 | 0 | 1 | 2 | 0 | -6.25 | 0 | 0 / 0 |
| A | 2026-09-04 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-09-07 | 2 | 0 | 2 | 0 | 0 | -11.55 | 2 | 0 / 2 |
| A | 2026-09-08 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-09-09 | 4 | 4 | 0 | 0 | 0 | 153.50 | 2 | 2 / 0 |
| A | 2026-09-10 | 1 | 0 | 1 | 0 | 0 | -7.05 | 4 | 3 / 1 |
| A | 2026-09-11 | 3 | 1 | 2 | 0 | 0 | -40.05 | 2 | 0 / 2 |
| A | 2026-09-15 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-09-16 | 2 | 1 | 0 | 1 | 0 | 77.25 | 2 | 2 / 0 |
| A | 2026-09-17 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-09-18 | 2 | 0 | 2 | 0 | 0 | -6.15 | 2 | 2 / 0 |
| A | 2026-09-21 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| A | 2026-09-22 | 2 | 0 | 1 | 1 | 0 | -15.80 | 2 | 0 / 2 |
| A | 2026-09-23 | 3 | 1 | 2 | 0 | 0 | 12.00 | 2 | 0 / 2 |
| A | 2026-09-24 | 2 | 0 | 1 | 1 | 0 | -0.20 | 2 | 0 / 2 |
| A | 2026-09-25 | 3 | 2 | 1 | 0 | 0 | 85.75 | 2 | 2 / 0 |
| B | 2026-01-01 | 3 | 1 | 2 | 0 | 0 | -28.55 | 2 | 0 / 2 |
| B | 2026-01-02 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-01-05 | 4 | 2 | 0 | 2 | 0 | 66.75 | 2 | 1 / 1 |
| B | 2026-01-06 | 4 | 2 | 2 | 0 | 0 | 58.95 | 2 | 2 / 0 |
| B | 2026-01-07 | 2 | 0 | 2 | 0 | 0 | -16.05 | 0 | 0 / 0 |
| B | 2026-01-08 | 2 | 0 | 2 | 0 | 0 | -19.20 | 2 | 0 / 2 |
| B | 2026-01-09 | 2 | 0 | 2 | 0 | 0 | -49.30 | 2 | 0 / 2 |
| B | 2026-01-12 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| B | 2026-01-13 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-01-14 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| B | 2026-01-16 | 4 | 2 | 0 | 2 | 0 | 36.25 | 4 | 4 / 0 |
| B | 2026-01-19 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-01-20 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-01-21 | 4 | 2 | 1 | 1 | 0 | 41.55 | 2 | 2 / 0 |
| B | 2026-01-22 | 4 | 0 | 1 | 2 | 1 | -12.10 | 2 | 2 / 0 |
| B | 2026-01-23 | 2 | 0 | 2 | 0 | 0 | -20.05 | 0 | 0 / 0 |
| B | 2026-01-27 | 4 | 0 | 2 | 2 | 0 | -16.00 | 2 | 2 / 0 |
| B | 2026-01-28 | 4 | 2 | 1 | 1 | 0 | 47.70 | 0 | 0 / 0 |
| B | 2026-01-29 | 2 | 0 | 2 | 0 | 0 | -32.95 | 2 | 2 / 0 |
| B | 2026-01-30 | 2 | 0 | 2 | 0 | 0 | -9.65 | 1 | 1 / 0 |
| B | 2026-02-01 | 1 | 0 | 1 | 0 | 0 | -15.85 | 2 | 2 / 0 |
| B | 2026-02-02 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-02-03 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-02-04 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-02-05 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-02-06 | 2 | 0 | 1 | 1 | 0 | -0.45 | 2 | 2 / 0 |
| B | 2026-02-09 | 3 | 1 | 2 | 0 | 0 | 4.60 | 3 | 1 / 2 |
| B | 2026-02-10 | 3 | 1 | 0 | 2 | 0 | 12.50 | 2 | 0 / 2 |
| B | 2026-02-11 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-02-12 | 2 | 0 | 1 | 1 | 0 | -0.55 | 2 | 0 / 2 |
| B | 2026-02-13 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-02-16 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-02-17 | 4 | 0 | 0 | 4 | 0 | 0.00 | 1 | 1 / 0 |
| B | 2026-02-18 | 4 | 2 | 2 | 0 | 0 | 26.05 | 2 | 2 / 0 |
| B | 2026-02-19 | 2 | 0 | 0 | 2 | 0 | 0.00 | 0 | 0 / 0 |
| B | 2026-02-20 | 4 | 2 | 0 | 2 | 0 | 17.60 | 0 | 0 / 0 |
| B | 2026-02-23 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| B | 2026-02-24 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-02-25 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| B | 2026-02-26 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| B | 2026-02-27 | 2 | 0 | 2 | 0 | 0 | -2.30 | 2 | 0 / 2 |
| B | 2026-03-02 | 4 | 0 | 3 | 1 | 0 | -109.75 | 4 | 2 / 2 |
| B | 2026-03-05 | 3 | 1 | 0 | 2 | 0 | 15.60 | 2 | 0 / 2 |
| B | 2026-03-06 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| B | 2026-03-09 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 2 / 0 |
| B | 2026-03-10 | 4 | 0 | 3 | 1 | 0 | -78.35 | 2 | 2 / 0 |
| B | 2026-03-11 | 1 | 0 | 0 | 1 | 0 | 0.00 | 0 | 0 / 0 |
| B | 2026-03-12 | 2 | 0 | 2 | 0 | 0 | -22.65 | 3 | 0 / 3 |
| B | 2026-03-13 | 3 | 0 | 2 | 1 | 0 | -46.70 | 1 | 0 / 1 |
| B | 2026-03-16 | 4 | 2 | 2 | 0 | 0 | 129.15 | 4 | 4 / 0 |
| B | 2026-03-17 | 4 | 0 | 2 | 2 | 0 | -19.90 | 1 | 1 / 0 |
| B | 2026-03-18 | 2 | 0 | 2 | 0 | 0 | -33.90 | 2 | 1 / 1 |
| B | 2026-03-19 | 1 | 0 | 1 | 0 | 0 | -1.95 | 1 | 0 / 1 |
| B | 2026-03-20 | 2 | 0 | 2 | 0 | 0 | -26.30 | 2 | 2 / 0 |
| B | 2026-03-25 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-03-27 | 2 | 0 | 1 | 1 | 0 | -4.80 | 2 | 0 / 2 |
| B | 2026-03-30 | 3 | 0 | 1 | 2 | 0 | -30.00 | 2 | 2 / 0 |
| B | 2026-04-01 | 3 | 0 | 3 | 0 | 0 | -64.10 | 2 | 2 / 0 |
| B | 2026-04-02 | 0 | 0 | 0 | 0 | 0 | 0.00 | 1 | 1 / 0 |
| B | 2026-04-06 | 3 | 2 | 1 | 0 | 0 | -11.25 | 1 | 1 / 0 |
| B | 2026-04-07 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-04-08 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-04-09 | 4 | 0 | 3 | 1 | 0 | -51.75 | 2 | 2 / 0 |
| B | 2026-04-10 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-04-13 | 2 | 0 | 1 | 1 | 0 | -12.65 | 1 | 0 / 1 |
| B | 2026-04-15 | 2 | 0 | 2 | 0 | 0 | -23.45 | 2 | 0 / 2 |
| B | 2026-04-16 | 4 | 1 | 2 | 1 | 0 | 20.50 | 0 | 0 / 0 |
| B | 2026-04-17 | 2 | 0 | 2 | 0 | 0 | -30.75 | 2 | 0 / 2 |
| B | 2026-04-20 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-04-21 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |
| B | 2026-04-22 | 2 | 0 | 2 | 0 | 0 | -17.45 | 2 | 0 / 2 |
| B | 2026-04-23 | 2 | 0 | 1 | 1 | 0 | -2.20 | 2 | 0 / 2 |
| B | 2026-04-24 | 2 | 0 | 0 | 2 | 0 | 0.00 | 2 | 0 / 2 |

### Weekly

| Period | ISO week | L2L setups | Target | SL | Skipped | Ambiguous | L2L resolved points | Ekal setups | Ekal target / open |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 2026-W18 | 10 | 2 | 4 | 4 | 0 | -6.60 | 8 | 5 / 3 |
| A | 2026-W19 | 14 | 2 | 6 | 6 | 0 | 8.90 | 11 | 10 / 1 |
| A | 2026-W20 | 12 | 2 | 2 | 8 | 0 | 64.70 | 8 | 5 / 3 |
| A | 2026-W21 | 12 | 4 | 0 | 8 | 0 | 120.45 | 8 | 2 / 6 |
| A | 2026-W22 | 14 | 6 | 6 | 2 | 0 | 103.95 | 7 | 2 / 5 |
| A | 2026-W23 | 10 | 0 | 6 | 4 | 0 | -46.50 | 8 | 2 / 6 |
| A | 2026-W24 | 12 | 0 | 12 | 0 | 0 | -107.10 | 8 | 3 / 5 |
| A | 2026-W25 | 16 | 4 | 8 | 4 | 0 | 45.85 | 10 | 8 / 2 |
| A | 2026-W26 | 8 | 0 | 6 | 2 | 0 | -20.55 | 8 | 4 / 4 |
| A | 2026-W27 | 6 | 2 | 1 | 3 | 0 | 66.20 | 2 | 0 / 2 |
| A | 2026-W28 | 8 | 0 | 6 | 2 | 0 | -33.10 | 4 | 0 / 4 |
| A | 2026-W29 | 11 | 1 | 3 | 7 | 0 | 33.15 | 6 | 3 / 3 |
| A | 2026-W30 | 6 | 0 | 4 | 2 | 0 | -28.25 | 4 | 2 / 2 |
| A | 2026-W31 | 14 | 2 | 10 | 2 | 0 | -41.05 | 11 | 7 / 4 |
| A | 2026-W32 | 9 | 4 | 5 | 0 | 0 | 2.50 | 6 | 3 / 3 |
| A | 2026-W33 | 12 | 0 | 7 | 5 | 0 | -37.90 | 8 | 4 / 4 |
| A | 2026-W34 | 12 | 2 | 5 | 5 | 0 | -41.50 | 8 | 2 / 6 |
| A | 2026-W35 | 16 | 4 | 0 | 12 | 0 | 112.60 | 10 | 6 / 4 |
| A | 2026-W36 | 13 | 5 | 4 | 4 | 0 | 58.95 | 5 | 3 / 2 |
| A | 2026-W37 | 12 | 5 | 5 | 2 | 0 | 94.85 | 12 | 5 / 7 |
| A | 2026-W38 | 8 | 1 | 2 | 5 | 0 | 71.10 | 8 | 4 / 4 |
| A | 2026-W39 | 12 | 3 | 5 | 4 | 0 | 81.75 | 10 | 2 / 8 |
| B | 2026-W01 | 5 | 1 | 2 | 2 | 0 | -28.55 | 4 | 0 / 4 |
| B | 2026-W02 | 14 | 4 | 8 | 2 | 0 | 41.15 | 8 | 3 / 5 |
| B | 2026-W03 | 10 | 2 | 0 | 8 | 0 | 36.25 | 10 | 8 / 2 |
| B | 2026-W04 | 14 | 2 | 4 | 7 | 1 | 9.40 | 8 | 4 / 4 |
| B | 2026-W05 | 13 | 2 | 8 | 3 | 0 | -26.75 | 7 | 7 / 0 |
| B | 2026-W06 | 10 | 0 | 1 | 9 | 0 | -0.45 | 10 | 2 / 8 |
| B | 2026-W07 | 12 | 2 | 3 | 7 | 0 | 16.55 | 11 | 1 / 10 |
| B | 2026-W08 | 16 | 4 | 2 | 10 | 0 | 43.65 | 5 | 3 / 2 |
| B | 2026-W09 | 10 | 0 | 2 | 8 | 0 | -2.30 | 10 | 6 / 4 |
| B | 2026-W10 | 9 | 1 | 3 | 5 | 0 | -94.15 | 8 | 4 / 4 |
| B | 2026-W11 | 12 | 0 | 7 | 5 | 0 | -147.70 | 8 | 4 / 4 |
| B | 2026-W12 | 13 | 2 | 9 | 2 | 0 | 47.10 | 10 | 8 / 2 |
| B | 2026-W13 | 4 | 0 | 1 | 3 | 0 | -4.80 | 4 | 0 / 4 |
| B | 2026-W14 | 6 | 0 | 4 | 2 | 0 | -94.10 | 5 | 5 / 0 |
| B | 2026-W15 | 13 | 2 | 4 | 7 | 0 | -63.00 | 9 | 3 / 6 |
| B | 2026-W16 | 10 | 1 | 7 | 2 | 0 | -46.35 | 5 | 0 / 5 |
| B | 2026-W17 | 10 | 0 | 3 | 7 | 0 | -19.65 | 10 | 0 / 10 |

## D. Data-quality differences

Period B calendar references: [NSE 2026 F&O holidays](https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf), [Jan 15 additional closure](https://nsearchives.nseindia.com/content/circulars/FAOP72262.pdf), [Feb 1 special session](https://nsearchives.nseindia.com/content/circulars/FAOP72352.pdf).

| Coverage measure | Period A | Period B |
|---|---:|---:|
| Exchange sessions / underlying dates | 106 / 106 | 76 / 76 |
| Underlying regular session (75 slots) | 106/106 days | 76/76 days, 75 bars each |
| Expected option contract-days | 424 | 304 |
| Complete / partial / missing contract-days | 381 / 25 / 18 (89.86% complete) | 276 / 22 / 6 (90.79% complete) |
| Any-data contract-days | 406/424 (95.75%) | 298/304 (98.03%) |
| Missing expected 5-min intervals | 2328 | 1278/22800 (5.61% missing) |
| Fully usable / partially usable / unusable days | 91 / 5 / 10 | 58 / 14 / 4 |

Period B availability: 298/304 (98.03%) of selected contract-days had some candles, 276/304 (90.79%) had all 75 session slots, and 94.39% of required candle slots were present. The 6 absent contract-days and 22 partial contract-days appear below. No bars were filled or fabricated.

| Date | Option | ITM rank | Missing intervals | Status | Contract |
|---|---|---:|---:|---|---|
| 2026-02-03 | PE | 2 | 1 | partial | `NSE-NIFTY-03Feb26-26350-PE` |
| 2026-03-04 | CE | 3 | 59 | partial | `NSE-NIFTY-10Mar26-23550-CE` |
| 2026-03-04 | CE | 2 | 13 | partial | `NSE-NIFTY-10Mar26-23600-CE` |
| 2026-03-05 | CE | 3 | 65 | partial | `NSE-NIFTY-10Mar26-23550-CE` |
| 2026-03-05 | CE | 2 | 31 | partial | `NSE-NIFTY-10Mar26-23600-CE` |
| 2026-03-06 | CE | 3 | 65 | partial | `NSE-NIFTY-10Mar26-23550-CE` |
| 2026-03-06 | CE | 2 | 37 | partial | `NSE-NIFTY-10Mar26-23600-CE` |
| 2026-03-10 | CE | 3 | 5 | partial | `NSE-NIFTY-10Mar26-23550-CE` |
| 2026-03-11 | CE | 2 | 54 | partial | `NSE-NIFTY-17Mar26-23050-CE` |
| 2026-03-11 | PE | 3 | 4 | partial | `NSE-NIFTY-17Mar26-24750-PE` |
| 2026-03-12 | CE | 3 | 39 | partial | `NSE-NIFTY-17Mar26-22950-CE` |
| 2026-03-19 | CE | 3 | 75 | missing | `NSE-NIFTY-24Mar26-21400-CE` |
| 2026-03-19 | CE | 2 | 11 | partial | `NSE-NIFTY-24Mar26-22000-CE` |
| 2026-03-20 | CE | 3 | 75 | missing | `NSE-NIFTY-24Mar26-21400-CE` |
| 2026-03-20 | CE | 2 | 1 | partial | `NSE-NIFTY-24Mar26-22000-CE` |
| 2026-03-23 | CE | 3 | 75 | missing | `NSE-NIFTY-24Mar26-21350-CE` |
| 2026-03-23 | CE | 2 | 75 | missing | `NSE-NIFTY-24Mar26-21400-CE` |
| 2026-03-24 | CE | 3 | 75 | missing | `NSE-NIFTY-24Mar26-21350-CE` |
| 2026-03-24 | CE | 2 | 75 | missing | `NSE-NIFTY-24Mar26-21400-CE` |
| 2026-03-30 | CE | 3 | 48 | partial | `NSE-NIFTY-30Mar26-21400-CE` |
| 2026-04-01 | CE | 3 | 68 | partial | `NSE-NIFTY-07Apr26-21400-CE` |
| 2026-04-02 | CE | 3 | 43 | partial | `NSE-NIFTY-07Apr26-21300-CE` |
| 2026-04-02 | CE | 2 | 64 | partial | `NSE-NIFTY-07Apr26-21350-CE` |
| 2026-04-06 | CE | 3 | 55 | partial | `NSE-NIFTY-07Apr26-21400-CE` |
| 2026-04-07 | CE | 3 | 69 | partial | `NSE-NIFTY-07Apr26-21400-CE` |
| 2026-04-08 | CE | 3 | 9 | partial | `NSE-NIFTY-13Apr26-22850-CE` |
| 2026-04-13 | CE | 3 | 55 | partial | `NSE-NIFTY-13Apr26-22550-CE` |
| 2026-04-13 | CE | 2 | 32 | partial | `NSE-NIFTY-13Apr26-22850-CE` |

Period A's saved diagnostic has 381 complete, 25 partial, and 18 missing contract-days out of 424; 2328 missing option intervals; 91/5/10 fully usable/partial/unusable dates. Missing/partial option bars may hide or alter setups, entries, and resolution. These observed samples cannot measure what the strategy would have done with the missing candles.

## E. Ekalayava specification limitation

The canonical Ekalayava specification does not define a complete SL/exit lifecycle (see `reports/ekalayava_spec_implementation_audit.md`). TARGET counts measure target-hit frequency only. OPEN trades remain unresolved with no exit price or holding duration; the baseline Ekalayava points are not realized P&L. This report excludes them from realized point comparisons and does not invent an exit.

## F. Observations measured in both periods

- CE/PE aggregate mix is near balanced in both: A 203/214 (48.7% CE); B 165/148 (52.7% CE).
- ITM2/ITM3 counts are close in both: A 212/205; B 162/151.
- Entries occur across morning and later hours in both windows; see the separate hourly frequencies.
- Both periods contain unresolved Ekalayava trades and incomplete option contract-days, so the observed trade distributions are conditional on data availability and Ekalayava target observations are not returns.

## G. Period-specific measured observations

- L2L outcomes differ: A 49 targets/107 SL; B 23 targets/68 SL and 1 ambiguous. Resolved points: 502.40 vs -333.70.
- Ekalayava target hits/open: A 82/88 of 170; B 58/74 of 132. Target distance and MFE/MAE are reported above.
- Monthly/weekday result distributions, MFE/MAE, and observed holding duration vary between the windows. No market-regime categories were specified; this report does not assign a regime or causal explanation.

## H. Questions to test next

1. After a canonical Ekalayava exit/SL lifecycle is decided, how do its resolved distributions compare across the same periods?
2. Do L2L distributions persist on fully usable days, and how sensitive are they to partial or missing contract-days?
3. Are CE/PE, ITM rank, entry-hour, weekday, and month distributions similar when comparing matched data-coverage classes?
4. What independently specified, non-lookahead market-condition labels would be appropriate to test before interpreting period differences?
5. Can missing/partial option contract-days be recovered from another approved historical source?

No strategy rules or parameters were changed.

