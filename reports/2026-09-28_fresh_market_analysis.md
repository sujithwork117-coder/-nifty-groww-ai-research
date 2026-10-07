# Fresh Market Analysis — 2026-09-28

**Scope:** NIFTY 5-minute regular session, 2026-09-28, Asia/Kolkata. Existing canonical Level-to-Level and Ekalayava implementations only. No historical periods were rerun, strategy rules were not changed, and no orders were placed. Groww read-only authentication succeeded with the newly supplied local credentials; no credential values are included here.

## Data obtained and validation

- **Underlying:** Groww returned 84 NIFTY candles from 09:00 through 15:55 IST. The canonical regular session has 75 expected timestamps (09:15–15:25); all 75 are present, with no duplicates or invalid OHLC. The extra pre/post-session timestamps were excluded from strategy analysis.
- **Session context:** opening bar O/H/L = 23079.75 / 23079.75 / 22946.95; 15:25 close = 22780.25; session high/low = 23079.75 / 22762.25. Change from opening price to 15:25 close: -299.50 points; high-low range: 317.50 points.
- **Contract selection:** Groww expiry queries showed 2026-09-29 as the nearest expiry on Sep 28. The existing selector ranked the 63 contracts returned for that expiry using the 09:15 underlying open (23079.75), CE strikes below spot and PE strikes above spot. Selected contracts:

| Side/rank | Contract | Regular-session candles | Missing of 75 | 09:15 opening bar |
|---|---|---:|---:|---|
| CE ITM2 | `NSE-NIFTY-29Sep26-22350-CE` | 61 | 14 | Missing |
| PE ITM2 | `NSE-NIFTY-29Sep26-23950-PE` | 52 | 23 | Missing |
| CE ITM3 | `NSE-NIFTY-29Sep26-22300-CE` | 72 | 3 | Missing |
| PE ITM3 | `NSE-NIFTY-29Sep26-24050-PE` | 43 | 32 | Present |

All four option files passed OHLC validation, but **0/4 contract-days are complete**. Exact missing regular-session timestamps:

- CE ITM2: 09:15, 09:20, 09:25, 09:30, 09:35, 09:50, 09:55, 10:00, 10:30, 10:50, 11:35, 12:15, 13:50, 13:55.
- PE ITM2: 09:15, 10:05, 10:50, 11:00, 11:40, 11:45, 12:05, 12:10, 12:15, 12:20, 12:30, 12:45, 12:55, 13:40, 13:50, 13:55, 14:05, 14:10, 14:15, 14:20, 14:25, 14:30, 14:35.
- CE ITM3: 09:15, 09:55, 12:35.
- PE ITM3: 09:55, 10:00, 10:05, 10:45, 10:50, 11:00, 11:10, 11:35, 11:40, 11:45, 11:55, 12:05, 12:20, 12:25, 12:40, 12:50, 12:55, 13:05, 13:10, 13:15, 13:30, 13:35, 13:40, 14:00, 14:05, 14:10, 14:15, 14:30, 14:40, 14:55, 15:00, 15:05.

Raw retrieved files are under ignored `data/derived/fresh_2026-09-28/`. The analysis used only 09:15–15:25 bars. Missing option bars were not filled or inferred.

## Strategy results and journal

The existing implementations were run on the one selected contract with the required 09:15 opening candle (PE ITM3). The other three contracts were **not run** because without the first candle the current opening-level code would incorrectly treat a later candle as the opening range. PE ITM3 has 32 missing session intervals, so even its zero observed setup count is not evidence that no setup occurred in the complete market record.

| Strategy | Observed setups/entries | TARGET | SL | Resolved points | MFE/MAE |
|---|---:|---:|---:|---:|---|
| Level-to-Level | 0 (of 1/4 contracts run) | 0 | 0 | 0 observed | Not applicable; no entry |
| Ekalayava | 0 (of 1/4 contracts run) | 0 | Not defined | Not applicable | Not applicable; no entry |

No signal rows were observed on the eligible PE ITM3 file. Thus there is no chronological trade journal row, entry reason, trade-level opening range, swing reference, target/SL time, or close status to report. The other three contract outcomes are unavailable, not zero. MFE/MAE are N/A because no entries were detected. Ekalayava’s exit/SL lifecycle remains undefined; no exit rule was added.

## Context vs prior research

This session cannot support a valid comparison of trade behavior with Period A or B because only one of four selected option contracts had its canonical opening candle and that file had substantial intraday gaps. The underlying itself opened at its session high and closed 299.50 points below its open, a 317.50-point high-low range. That describes the underlying tape only; it does not establish how either strategy behaved across the four contracts.

The main unusual condition for this analysis is option-data incompleteness: 72 of 300 expected option timestamps are absent, including the opening candle for three contracts. Potential repeated trade behavior, target rates, and outcomes remain unmeasured. No old baseline experiments were rerun.

## Safety and status

Groww access was read-only. `EXECUTION_ALLOWED=false` and `PAPER_ONLY=true` remain in force. No order endpoint was invoked. Existing tests passed: 57 passed.

**Conclusion:** the required day-specific data was obtained, but its option coverage is insufficient for a complete four-contract fresh-market analysis. The measured result is zero observed setups on the only contract with a valid opening bar; full-day strategy behavior remains inconclusive.

