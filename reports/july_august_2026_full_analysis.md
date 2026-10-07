# NIFTY July–August 2026 Full Research and Contract Audit

**Requested period:** 2026-07-01 through 2026-08-31 inclusive. **Status: INCOMPLETE** because Groww’s expiry catalogs did not return exact required strikes for 65 of 176 expected contract-days. The full period is retained; missing slots are unavailable, not substituted. Read-only Groww authentication succeeded. No order endpoints were called. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`.

## 1. Scope and canonical rules
The existing canonical definitions in `NIFTY_Strategy_Definitions_Level_to_Level_Ekalavya.md` were not changed. Both strategies use NIFTY option premium bars at 5-minute resolution in Asia/Kolkata. The daily contract reference is the underlying NIFTY 09:15 bar open. Each option contract’s 09:15 bar defines its own opening high/low. The strategy engines use option timestamps and OHLC; volume/OI are present in source rows but not used by strategy rules. Underlying OHLC is used for daily strike selection, not as the option-premium series.

July–August is not shortened. No candle was fabricated, interpolated, or filled. Ekalayava target touches remain observations, not wins or realized P&L; its exit lifecycle is still undefined.

## 2. Contract-selection audit and correction
**The prior period selector was incorrect for a complete historical audit.** It inferred the universe from local option CSVs, selected the nearest expiry with files separately by CE/PE, and ranked available strikes. Missing files could shift ITM ranks and CE/PE could resolve to different expiries. The general selector helper also ranked only returned contracts. These infrastructure defects were corrected without changing either strategy.

The corrected period runner requires an expiry-to-contract catalog from Groww and fails closed without one. For every date it reads the unique NIFTY 09:15 open; chooses the earliest Groww expiry on or after that date (same-day expiry included); uses the minimum observed strike interval in that catalog (50 points for all nine returned expiries); then selects only exact CE/PE ITM2/ITM3 ladder contracts. Missing exact symbols remain unavailable; no farther strike is promoted. The runner maps each exact symbol to its same-date CSV and clips strategy input to 09:15–15:25 IST.

The canonical definition specifies ITM2/ITM3 but no strike-step formula. The observed 50-point grid is an explicit implementation convention, not a new strategy rule. No absent symbol or strike was constructed. Historical listing dates for catalog-omitted strikes are unavailable, so those slots remain unresolved.

| Expiry | Groww contracts returned | Observed minimum interval | Symbol expiry check |
| --- | --- | --- | --- |
| 2026-07-07 | 10 | 50 points | all match |
| 2026-07-14 | 166 | 50 points | all match |
| 2026-07-21 | 22 | 50 points | all match |
| 2026-07-28 | 205 | 50 points | all match |
| 2026-08-04 | 120 | 50 points | all match |
| 2026-08-11 | 103 | 50 points | all match |
| 2026-08-18 | 89 | 50 points | all match |
| 2026-08-25 | 181 | 50 points | all match |
| 2026-09-01 | 80 | 50 points | all match |

The 07-Jul and 21-Jul chains returned only 10 and 22 contracts; each lacks the exact near-spot ladder for five corresponding sessions, leaving 20 slots unavailable per expiry. Other expiry catalogs account for 25 additional unavailable slots.

| Audit item | Finding |
| --- | --- |
| Daily strike recalculation | YES — daily NIFTY 09:15 open. |
| CE/PE independently selected | YES — side-specific exact ladder contracts. |
| ITM2/ITM3 | Exact when present in the Groww catalog; absent slots are not substituted. |
| Expiry | Earliest returned expiry on/after the trading date. |
| Rollover | Correct in the revised mapping; next session after expiry selects the next listed expiry. |
| Fixed contract reuse | NO in the revised daily selector. |
| Lookahead | No later price candles used; catalog historical listing completeness remains unknown for absent slots. |

## 3. Expiry rollover examples
Dates below are Groww `get_expiries` results. `N/A` means the exact slot was absent from the catalog.
| Expiry | Role | Session | Selected expiry | CE ITM2 | CE ITM3 | PE ITM2 | PE ITM3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-07 | Before | 2026-07-06 | 2026-07-07 | N/A | N/A | N/A | N/A |
| 2026-07-07 | Expiry | 2026-07-07 | 2026-07-07 | N/A | N/A | N/A | N/A |
| 2026-07-07 | After | 2026-07-08 | 2026-07-14 | NSE-NIFTY-14Jul26-24150-CE | NSE-NIFTY-14Jul26-24100-CE | NSE-NIFTY-14Jul26-24300-PE | NSE-NIFTY-14Jul26-24350-PE |
| 2026-07-14 | Before | 2026-07-13 | 2026-07-14 | NSE-NIFTY-14Jul26-23950-CE | NSE-NIFTY-14Jul26-23900-CE | NSE-NIFTY-14Jul26-24100-PE | NSE-NIFTY-14Jul26-24150-PE |
| 2026-07-14 | Expiry | 2026-07-14 | 2026-07-14 | NSE-NIFTY-14Jul26-24000-CE | NSE-NIFTY-14Jul26-23950-CE | NSE-NIFTY-14Jul26-24150-PE | NSE-NIFTY-14Jul26-24200-PE |
| 2026-07-14 | After | 2026-07-15 | 2026-07-21 | N/A | N/A | N/A | N/A |
| 2026-07-21 | Before | 2026-07-20 | 2026-07-21 | N/A | N/A | N/A | N/A |
| 2026-07-21 | Expiry | 2026-07-21 | 2026-07-21 | N/A | N/A | N/A | N/A |
| 2026-07-21 | After | 2026-07-22 | 2026-07-28 | NSE-NIFTY-28Jul26-24050-CE | NSE-NIFTY-28Jul26-24000-CE | NSE-NIFTY-28Jul26-24200-PE | NSE-NIFTY-28Jul26-24250-PE |
| 2026-07-28 | Before | 2026-07-27 | 2026-07-28 | NSE-NIFTY-28Jul26-23850-CE | NSE-NIFTY-28Jul26-23800-CE | NSE-NIFTY-28Jul26-24000-PE | NSE-NIFTY-28Jul26-24050-PE |
| 2026-07-28 | Expiry | 2026-07-28 | 2026-07-28 | NSE-NIFTY-28Jul26-23900-CE | NSE-NIFTY-28Jul26-23850-CE | NSE-NIFTY-28Jul26-24050-PE | NSE-NIFTY-28Jul26-24100-PE |
| 2026-07-28 | After | 2026-07-29 | 2026-08-04 | NSE-NIFTY-04Aug26-24100-CE | N/A | N/A | NSE-NIFTY-04Aug26-24300-PE |
| 2026-08-04 | Before | 2026-08-03 | 2026-08-04 | NSE-NIFTY-04Aug26-24500-CE | NSE-NIFTY-04Aug26-24450-CE | NSE-NIFTY-04Aug26-24650-PE | N/A |
| 2026-08-04 | Expiry | 2026-08-04 | 2026-08-04 | N/A | NSE-NIFTY-04Aug26-24550-CE | NSE-NIFTY-04Aug26-24750-PE | N/A |
| 2026-08-04 | After | 2026-08-05 | 2026-08-11 | N/A | NSE-NIFTY-11Aug26-24500-CE | N/A | NSE-NIFTY-11Aug26-24750-PE |
| 2026-08-11 | Before | 2026-08-10 | 2026-08-11 | NSE-NIFTY-11Aug26-24500-CE | NSE-NIFTY-11Aug26-24450-CE | N/A | N/A |
| 2026-08-11 | Expiry | 2026-08-11 | 2026-08-11 | NSE-NIFTY-11Aug26-24500-CE | NSE-NIFTY-11Aug26-24450-CE | N/A | N/A |
| 2026-08-11 | After | 2026-08-12 | 2026-08-18 | NSE-NIFTY-18Aug26-24400-CE | N/A | NSE-NIFTY-18Aug26-24550-PE | NSE-NIFTY-18Aug26-24600-PE |
| 2026-08-18 | Before | 2026-08-17 | 2026-08-18 | NSE-NIFTY-18Aug26-24300-CE | N/A | NSE-NIFTY-18Aug26-24450-PE | NSE-NIFTY-18Aug26-24500-PE |
| 2026-08-18 | Expiry | 2026-08-18 | 2026-08-18 | N/A | N/A | NSE-NIFTY-18Aug26-24300-PE | NSE-NIFTY-18Aug26-24350-PE |
| 2026-08-18 | After | 2026-08-19 | 2026-08-25 | NSE-NIFTY-25Aug26-24100-CE | NSE-NIFTY-25Aug26-24050-CE | NSE-NIFTY-25Aug26-24250-PE | NSE-NIFTY-25Aug26-24300-PE |
| 2026-08-25 | Before | 2026-08-24 | 2026-08-25 | NSE-NIFTY-25Aug26-24200-CE | NSE-NIFTY-25Aug26-24150-CE | NSE-NIFTY-25Aug26-24350-PE | NSE-NIFTY-25Aug26-24400-PE |
| 2026-08-25 | Expiry | 2026-08-25 | 2026-08-25 | NSE-NIFTY-25Aug26-24100-CE | NSE-NIFTY-25Aug26-24050-CE | NSE-NIFTY-25Aug26-24250-PE | NSE-NIFTY-25Aug26-24300-PE |
| 2026-08-25 | After | 2026-08-26 | 2026-09-01 | NSE-NIFTY-01Sep26-24250-CE | NSE-NIFTY-01Sep26-24200-CE | NSE-NIFTY-01Sep26-24400-PE | NSE-NIFTY-01Sep26-24450-PE |

## 4. Raw data schema and path into the engine
- Underlying: `data/derived/requested_period_2026-04-25_2026-09-25/nifty_5m.csv`, 8,895 source rows across 2026-04-27–2026-09-25. The July–August subset has 3,696 raw rows and 3,300 regular-session bars (75/day).
- Option inputs: 305 existing Period A option CSVs + 20 weekly-run CSVs + 35 raw option CSVs (360 source files) merged to 305 unique symbol files. Exact timestamp duplicates were deduplicated; no conflicting OHLC duplicates; no interpolation.
- Row fields are `timestamp, open, high, low, close, volume, oi`. Historical requests use Groww `5minute`; adapter parses timestamp/OHLC and optional volume/OI; candle validation checks OHLC, rejects duplicates, and sorts chronologically. Naive source timestamps are interpreted as Asia/Kolkata; saved timestamps are timezone-aware.
- The inspected Groww contract catalog contains symbols but no numeric token field. Exact symbols and the corresponding individual CSV files are the instrument identifiers actually used.
- Data path: Groww expiry list → per-expiry contract catalog → daily NIFTY 09:15 open → exact side/rank symbol → symbol CSV filtered to date → regular-session 09:15–15:25 candles → unchanged L2L/Ekalayava engine. Underlying candles do not replace option premiums.
- For the 111 selected contract-days, all 8,325 regular option timestamps match the underlying session grid. All selected session rows have non-null volume/OI. Strategies use timestamp/OHLC only.
- Some files contain out-of-session rows (including 15:30+). The previous runner passed them to same-day exit horizon. This run clips input to 09:15–15:25; strategy entry/target/stop definitions were not changed.

**Trace 2026-07-14:** NIFTY 09:15 open 24,092.75; expiry 2026-07-14.
| Slot | Groww symbol | File | Raw rows | Raw first → last | Engine bars |
| --- | --- | --- | --- | --- | --- |
| CE ITM2 | NSE-NIFTY-14Jul26-24000-CE | assembled/options/NSE-NIFTY-14Jul26-24000-CE.csv | 76 | 2026-07-14T09:15:00+05:30 → 2026-07-14T15:30:00+05:30 | 75/75 (09:15–15:25) |
| CE ITM3 | NSE-NIFTY-14Jul26-23950-CE | assembled/options/NSE-NIFTY-14Jul26-23950-CE.csv | 76 | 2026-07-14T09:15:00+05:30 → 2026-07-14T15:30:00+05:30 | 75/75 (09:15–15:25) |
| PE ITM2 | NSE-NIFTY-14Jul26-24150-PE | assembled/options/NSE-NIFTY-14Jul26-24150-PE.csv | 76 | 2026-07-14T09:15:00+05:30 → 2026-07-14T15:30:00+05:30 | 75/75 (09:15–15:25) |
| PE ITM3 | NSE-NIFTY-14Jul26-24200-PE | assembled/options/NSE-NIFTY-14Jul26-24200-PE.csv | 76 | 2026-07-14T09:15:00+05:30 → 2026-07-14T15:30:00+05:30 | 75/75 (09:15–15:25) |
| Actual CE ITM2 timestamp IST | Open | High | Low | Close | Volume | OI |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07-14T09:15:00+05:30 | 108.40 | 133.75 | 90.30 | 123.85 | 15,021,435 | 498,040 |
| 2026-07-14T09:20:00+05:30 | 123.55 | 159.80 | 122.30 | 154.45 | 12,342,395 | 598,183 |
| 2026-07-14T09:25:00+05:30 | 153.50 | 164.00 | 148.60 | 150.55 | 5,437,315 | 557,107 |

**Trace 2026-07-28:** NIFTY 09:15 open 23,973.00; expiry 2026-07-28.
| Slot | Groww symbol | File | Raw rows | Raw first → last | Engine bars |
| --- | --- | --- | --- | --- | --- |
| CE ITM2 | NSE-NIFTY-28Jul26-23900-CE | assembled/options/NSE-NIFTY-28Jul26-23900-CE.csv | 76 | 2026-07-28T09:15:00+05:30 → 2026-07-28T15:30:00+05:30 | 75/75 (09:15–15:25) |
| CE ITM3 | NSE-NIFTY-28Jul26-23850-CE | assembled/options/NSE-NIFTY-28Jul26-23850-CE.csv | 76 | 2026-07-28T09:15:00+05:30 → 2026-07-28T15:30:00+05:30 | 75/75 (09:15–15:25) |
| PE ITM2 | NSE-NIFTY-28Jul26-24050-PE | assembled/options/NSE-NIFTY-28Jul26-24050-PE.csv | 76 | 2026-07-28T09:15:00+05:30 → 2026-07-28T15:30:00+05:30 | 75/75 (09:15–15:25) |
| PE ITM3 | NSE-NIFTY-28Jul26-24100-PE | assembled/options/NSE-NIFTY-28Jul26-24100-PE.csv | 76 | 2026-07-28T09:15:00+05:30 → 2026-07-28T15:30:00+05:30 | 75/75 (09:15–15:25) |
| Actual CE ITM2 timestamp IST | Open | High | Low | Close | Volume | OI |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07-28T09:15:00+05:30 | 85.60 | 146.80 | 85.60 | 141.35 | 11,500,060 | 209,386 |
| 2026-07-28T09:20:00+05:30 | 141.60 | 147.20 | 122.25 | 127.60 | 5,247,515 | 229,218 |
| 2026-07-28T09:25:00+05:30 | 126.00 | 126.85 | 109.05 | 118.60 | 5,684,445 | 261,743 |

**Trace 2026-08-25:** NIFTY 09:15 open 24,182.45; expiry 2026-08-25.
| Slot | Groww symbol | File | Raw rows | Raw first → last | Engine bars |
| --- | --- | --- | --- | --- | --- |
| CE ITM2 | NSE-NIFTY-25Aug26-24100-CE | assembled/options/NSE-NIFTY-25Aug26-24100-CE.csv | 78 | 2026-08-25T09:15:00+05:30 → 2026-08-25T15:40:00+05:30 | 75/75 (09:15–15:25) |
| CE ITM3 | NSE-NIFTY-25Aug26-24050-CE | assembled/options/NSE-NIFTY-25Aug26-24050-CE.csv | 77 | 2026-08-25T09:15:00+05:30 → 2026-08-25T15:35:00+05:30 | 75/75 (09:15–15:25) |
| PE ITM2 | NSE-NIFTY-25Aug26-24250-PE | assembled/options/NSE-NIFTY-25Aug26-24250-PE.csv | 78 | 2026-08-25T09:15:00+05:30 → 2026-08-25T15:40:00+05:30 | 75/75 (09:15–15:25) |
| PE ITM3 | NSE-NIFTY-25Aug26-24300-PE | assembled/options/NSE-NIFTY-25Aug26-24300-PE.csv | 77 | 2026-08-25T09:15:00+05:30 → 2026-08-25T15:35:00+05:30 | 75/75 (09:15–15:25) |
| Actual CE ITM2 timestamp IST | Open | High | Low | Close | Volume | OI |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-08-25T09:15:00+05:30 | 95.00 | 101.90 | 62.85 | 99.15 | 16,394,365 | 271,372 |
| 2026-08-25T09:20:00+05:30 | 98.15 | 119.80 | 97.50 | 98.90 | 10,088,000 | 289,043 |
| 2026-08-25T09:25:00+05:30 | 98.00 | 113.35 | 96.25 | 106.80 | 5,638,815 | 324,238 |

## 5. Daily contract selection and candle trace (176 expected slots)
Each row is one expected trading-date × CE/PE × ITM2/ITM3 slot. `Raw first/last` are file endpoints; `regular bars` are exactly the bars passed to strategy functions. No symbol/strike/token/file is assigned to absent catalog slots.
| Date | NIFTY 09:15 open | Expiry | Slot | Symbol | CSV file | Session bars | Raw rows | Raw first | Raw last | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-01 | 23,908.55 | 2026-07-07 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-01 | 23,908.55 | 2026-07-07 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-01 | 23,908.55 | 2026-07-07 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-01 | 23,908.55 | 2026-07-07 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-02 | 24,072.85 | 2026-07-07 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-02 | 24,072.85 | 2026-07-07 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-02 | 24,072.85 | 2026-07-07 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-02 | 24,072.85 | 2026-07-07 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-03 | 24,368.00 | 2026-07-07 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-03 | 24,368.00 | 2026-07-07 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-03 | 24,368.00 | 2026-07-07 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-03 | 24,368.00 | 2026-07-07 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-06 | 24,306.85 | 2026-07-07 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-06 | 24,306.85 | 2026-07-07 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-06 | 24,306.85 | 2026-07-07 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-06 | 24,306.85 | 2026-07-07 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-07 | 24,464.45 | 2026-07-07 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-07 | 24,464.45 | 2026-07-07 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-07 | 24,464.45 | 2026-07-07 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-07 | 24,464.45 | 2026-07-07 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-08 | 24,247.15 | 2026-07-14 | CE ITM2 | NSE-NIFTY-14Jul26-24150-CE | assembled/options/NSE-NIFTY-14Jul26-24150-CE.csv | 75/75 | 76 | 2026-07-08T09:15:00+05:30 | 2026-07-08T15:30:00+05:30 | COMPLETE |
| 2026-07-08 | 24,247.15 | 2026-07-14 | CE ITM3 | NSE-NIFTY-14Jul26-24100-CE | assembled/options/NSE-NIFTY-14Jul26-24100-CE.csv | 75/75 | 76 | 2026-07-08T09:15:00+05:30 | 2026-07-08T15:30:00+05:30 | COMPLETE |
| 2026-07-08 | 24,247.15 | 2026-07-14 | PE ITM2 | NSE-NIFTY-14Jul26-24300-PE | assembled/options/NSE-NIFTY-14Jul26-24300-PE.csv | 75/75 | 76 | 2026-07-08T09:15:00+05:30 | 2026-07-08T15:30:00+05:30 | COMPLETE |
| 2026-07-08 | 24,247.15 | 2026-07-14 | PE ITM3 | NSE-NIFTY-14Jul26-24350-PE | assembled/options/NSE-NIFTY-14Jul26-24350-PE.csv | 75/75 | 75 | 2026-07-08T09:15:00+05:30 | 2026-07-08T15:25:00+05:30 | COMPLETE |
| 2026-07-09 | 23,930.05 | 2026-07-14 | CE ITM2 | NSE-NIFTY-14Jul26-23850-CE | assembled/options/NSE-NIFTY-14Jul26-23850-CE.csv | 75/75 | 76 | 2026-07-09T09:15:00+05:30 | 2026-07-09T15:30:00+05:30 | COMPLETE |
| 2026-07-09 | 23,930.05 | 2026-07-14 | CE ITM3 | NSE-NIFTY-14Jul26-23800-CE | assembled/options/NSE-NIFTY-14Jul26-23800-CE.csv | 75/75 | 76 | 2026-07-09T09:15:00+05:30 | 2026-07-09T15:30:00+05:30 | COMPLETE |
| 2026-07-09 | 23,930.05 | 2026-07-14 | PE ITM2 | NSE-NIFTY-14Jul26-24000-PE | assembled/options/NSE-NIFTY-14Jul26-24000-PE.csv | 75/75 | 76 | 2026-07-09T09:15:00+05:30 | 2026-07-09T15:30:00+05:30 | COMPLETE |
| 2026-07-09 | 23,930.05 | 2026-07-14 | PE ITM3 | NSE-NIFTY-14Jul26-24050-PE | assembled/options/NSE-NIFTY-14Jul26-24050-PE.csv | 75/75 | 76 | 2026-07-09T09:15:00+05:30 | 2026-07-09T15:30:00+05:30 | COMPLETE |
| 2026-07-10 | 24,146.05 | 2026-07-14 | CE ITM2 | NSE-NIFTY-14Jul26-24050-CE | assembled/options/NSE-NIFTY-14Jul26-24050-CE.csv | 75/75 | 76 | 2026-07-10T09:15:00+05:30 | 2026-07-10T15:30:00+05:30 | COMPLETE |
| 2026-07-10 | 24,146.05 | 2026-07-14 | CE ITM3 | NSE-NIFTY-14Jul26-24000-CE | assembled/options/NSE-NIFTY-14Jul26-24000-CE.csv | 75/75 | 75 | 2026-07-10T09:15:00+05:30 | 2026-07-10T15:25:00+05:30 | COMPLETE |
| 2026-07-10 | 24,146.05 | 2026-07-14 | PE ITM2 | NSE-NIFTY-14Jul26-24200-PE | assembled/options/NSE-NIFTY-14Jul26-24200-PE.csv | 75/75 | 76 | 2026-07-10T09:15:00+05:30 | 2026-07-10T15:30:00+05:30 | COMPLETE |
| 2026-07-10 | 24,146.05 | 2026-07-14 | PE ITM3 | NSE-NIFTY-14Jul26-24250-PE | assembled/options/NSE-NIFTY-14Jul26-24250-PE.csv | 75/75 | 76 | 2026-07-10T09:15:00+05:30 | 2026-07-10T15:30:00+05:30 | COMPLETE |
| 2026-07-13 | 24,032.25 | 2026-07-14 | CE ITM2 | NSE-NIFTY-14Jul26-23950-CE | assembled/options/NSE-NIFTY-14Jul26-23950-CE.csv | 75/75 | 75 | 2026-07-13T09:15:00+05:30 | 2026-07-13T15:25:00+05:30 | COMPLETE |
| 2026-07-13 | 24,032.25 | 2026-07-14 | CE ITM3 | NSE-NIFTY-14Jul26-23900-CE | assembled/options/NSE-NIFTY-14Jul26-23900-CE.csv | 75/75 | 75 | 2026-07-13T09:15:00+05:30 | 2026-07-13T15:25:00+05:30 | COMPLETE |
| 2026-07-13 | 24,032.25 | 2026-07-14 | PE ITM2 | NSE-NIFTY-14Jul26-24100-PE | assembled/options/NSE-NIFTY-14Jul26-24100-PE.csv | 75/75 | 76 | 2026-07-13T09:15:00+05:30 | 2026-07-13T15:30:00+05:30 | COMPLETE |
| 2026-07-13 | 24,032.25 | 2026-07-14 | PE ITM3 | NSE-NIFTY-14Jul26-24150-PE | assembled/options/NSE-NIFTY-14Jul26-24150-PE.csv | 75/75 | 76 | 2026-07-13T09:15:00+05:30 | 2026-07-13T15:30:00+05:30 | COMPLETE |
| 2026-07-14 | 24,092.75 | 2026-07-14 | CE ITM2 | NSE-NIFTY-14Jul26-24000-CE | assembled/options/NSE-NIFTY-14Jul26-24000-CE.csv | 75/75 | 76 | 2026-07-14T09:15:00+05:30 | 2026-07-14T15:30:00+05:30 | COMPLETE |
| 2026-07-14 | 24,092.75 | 2026-07-14 | CE ITM3 | NSE-NIFTY-14Jul26-23950-CE | assembled/options/NSE-NIFTY-14Jul26-23950-CE.csv | 75/75 | 76 | 2026-07-14T09:15:00+05:30 | 2026-07-14T15:30:00+05:30 | COMPLETE |
| 2026-07-14 | 24,092.75 | 2026-07-14 | PE ITM2 | NSE-NIFTY-14Jul26-24150-PE | assembled/options/NSE-NIFTY-14Jul26-24150-PE.csv | 75/75 | 76 | 2026-07-14T09:15:00+05:30 | 2026-07-14T15:30:00+05:30 | COMPLETE |
| 2026-07-14 | 24,092.75 | 2026-07-14 | PE ITM3 | NSE-NIFTY-14Jul26-24200-PE | assembled/options/NSE-NIFTY-14Jul26-24200-PE.csv | 75/75 | 76 | 2026-07-14T09:15:00+05:30 | 2026-07-14T15:30:00+05:30 | COMPLETE |
| 2026-07-15 | 24,082.45 | 2026-07-21 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-15 | 24,082.45 | 2026-07-21 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-15 | 24,082.45 | 2026-07-21 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-15 | 24,082.45 | 2026-07-21 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-16 | 24,140.70 | 2026-07-21 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-16 | 24,140.70 | 2026-07-21 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-16 | 24,140.70 | 2026-07-21 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-16 | 24,140.70 | 2026-07-21 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-17 | 24,128.10 | 2026-07-21 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-17 | 24,128.10 | 2026-07-21 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-17 | 24,128.10 | 2026-07-21 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-17 | 24,128.10 | 2026-07-21 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-20 | 24,190.05 | 2026-07-21 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-20 | 24,190.05 | 2026-07-21 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-20 | 24,190.05 | 2026-07-21 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-20 | 24,190.05 | 2026-07-21 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-21 | 24,215.95 | 2026-07-21 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-21 | 24,215.95 | 2026-07-21 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-21 | 24,215.95 | 2026-07-21 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-21 | 24,215.95 | 2026-07-21 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-22 | 24,146.90 | 2026-07-28 | CE ITM2 | NSE-NIFTY-28Jul26-24050-CE | assembled/options/NSE-NIFTY-28Jul26-24050-CE.csv | 75/75 | 76 | 2026-07-22T09:15:00+05:30 | 2026-07-22T15:30:00+05:30 | COMPLETE |
| 2026-07-22 | 24,146.90 | 2026-07-28 | CE ITM3 | NSE-NIFTY-28Jul26-24000-CE | assembled/options/NSE-NIFTY-28Jul26-24000-CE.csv | 75/75 | 76 | 2026-07-22T09:15:00+05:30 | 2026-07-22T15:30:00+05:30 | COMPLETE |
| 2026-07-22 | 24,146.90 | 2026-07-28 | PE ITM2 | NSE-NIFTY-28Jul26-24200-PE | assembled/options/NSE-NIFTY-28Jul26-24200-PE.csv | 75/75 | 76 | 2026-07-22T09:15:00+05:30 | 2026-07-22T15:30:00+05:30 | COMPLETE |
| 2026-07-22 | 24,146.90 | 2026-07-28 | PE ITM3 | NSE-NIFTY-28Jul26-24250-PE | assembled/options/NSE-NIFTY-28Jul26-24250-PE.csv | 75/75 | 75 | 2026-07-22T09:15:00+05:30 | 2026-07-22T15:25:00+05:30 | COMPLETE |
| 2026-07-23 | 23,907.45 | 2026-07-28 | CE ITM2 | NSE-NIFTY-28Jul26-23850-CE | assembled/options/NSE-NIFTY-28Jul26-23850-CE.csv | 75/75 | 76 | 2026-07-23T09:15:00+05:30 | 2026-07-23T15:30:00+05:30 | COMPLETE |
| 2026-07-23 | 23,907.45 | 2026-07-28 | CE ITM3 | NSE-NIFTY-28Jul26-23800-CE | assembled/options/NSE-NIFTY-28Jul26-23800-CE.csv | 75/75 | 76 | 2026-07-23T09:15:00+05:30 | 2026-07-23T15:30:00+05:30 | COMPLETE |
| 2026-07-23 | 23,907.45 | 2026-07-28 | PE ITM2 | NSE-NIFTY-28Jul26-24000-PE | assembled/options/NSE-NIFTY-28Jul26-24000-PE.csv | 75/75 | 76 | 2026-07-23T09:15:00+05:30 | 2026-07-23T15:30:00+05:30 | COMPLETE |
| 2026-07-23 | 23,907.45 | 2026-07-28 | PE ITM3 | NSE-NIFTY-28Jul26-24050-PE | assembled/options/NSE-NIFTY-28Jul26-24050-PE.csv | 75/75 | 76 | 2026-07-23T09:15:00+05:30 | 2026-07-23T15:30:00+05:30 | COMPLETE |
| 2026-07-24 | 23,674.40 | 2026-07-28 | CE ITM2 | NSE-NIFTY-28Jul26-23600-CE | assembled/options/NSE-NIFTY-28Jul26-23600-CE.csv | 75/75 | 76 | 2026-07-24T09:15:00+05:30 | 2026-07-24T15:30:00+05:30 | COMPLETE |
| 2026-07-24 | 23,674.40 | 2026-07-28 | CE ITM3 | NSE-NIFTY-28Jul26-23550-CE | assembled/options/NSE-NIFTY-28Jul26-23550-CE.csv | 75/75 | 75 | 2026-07-24T09:15:00+05:30 | 2026-07-24T15:25:00+05:30 | COMPLETE |
| 2026-07-24 | 23,674.40 | 2026-07-28 | PE ITM2 | NSE-NIFTY-28Jul26-23750-PE | assembled/options/NSE-NIFTY-28Jul26-23750-PE.csv | 75/75 | 76 | 2026-07-24T09:15:00+05:30 | 2026-07-24T15:30:00+05:30 | COMPLETE |
| 2026-07-24 | 23,674.40 | 2026-07-28 | PE ITM3 | NSE-NIFTY-28Jul26-23800-PE | assembled/options/NSE-NIFTY-28Jul26-23800-PE.csv | 75/75 | 76 | 2026-07-24T09:15:00+05:30 | 2026-07-24T15:30:00+05:30 | COMPLETE |
| 2026-07-27 | 23,929.50 | 2026-07-28 | CE ITM2 | NSE-NIFTY-28Jul26-23850-CE | assembled/options/NSE-NIFTY-28Jul26-23850-CE.csv | 75/75 | 76 | 2026-07-27T09:15:00+05:30 | 2026-07-27T15:30:00+05:30 | COMPLETE |
| 2026-07-27 | 23,929.50 | 2026-07-28 | CE ITM3 | NSE-NIFTY-28Jul26-23800-CE | assembled/options/NSE-NIFTY-28Jul26-23800-CE.csv | 75/75 | 76 | 2026-07-27T09:15:00+05:30 | 2026-07-27T15:30:00+05:30 | COMPLETE |
| 2026-07-27 | 23,929.50 | 2026-07-28 | PE ITM2 | NSE-NIFTY-28Jul26-24000-PE | assembled/options/NSE-NIFTY-28Jul26-24000-PE.csv | 75/75 | 76 | 2026-07-27T09:15:00+05:30 | 2026-07-27T15:30:00+05:30 | COMPLETE |
| 2026-07-27 | 23,929.50 | 2026-07-28 | PE ITM3 | NSE-NIFTY-28Jul26-24050-PE | assembled/options/NSE-NIFTY-28Jul26-24050-PE.csv | 75/75 | 76 | 2026-07-27T09:15:00+05:30 | 2026-07-27T15:30:00+05:30 | COMPLETE |
| 2026-07-28 | 23,973.00 | 2026-07-28 | CE ITM2 | NSE-NIFTY-28Jul26-23900-CE | assembled/options/NSE-NIFTY-28Jul26-23900-CE.csv | 75/75 | 76 | 2026-07-28T09:15:00+05:30 | 2026-07-28T15:30:00+05:30 | COMPLETE |
| 2026-07-28 | 23,973.00 | 2026-07-28 | CE ITM3 | NSE-NIFTY-28Jul26-23850-CE | assembled/options/NSE-NIFTY-28Jul26-23850-CE.csv | 75/75 | 76 | 2026-07-28T09:15:00+05:30 | 2026-07-28T15:30:00+05:30 | COMPLETE |
| 2026-07-28 | 23,973.00 | 2026-07-28 | PE ITM2 | NSE-NIFTY-28Jul26-24050-PE | assembled/options/NSE-NIFTY-28Jul26-24050-PE.csv | 75/75 | 76 | 2026-07-28T09:15:00+05:30 | 2026-07-28T15:30:00+05:30 | COMPLETE |
| 2026-07-28 | 23,973.00 | 2026-07-28 | PE ITM3 | NSE-NIFTY-28Jul26-24100-PE | assembled/options/NSE-NIFTY-28Jul26-24100-PE.csv | 75/75 | 76 | 2026-07-28T09:15:00+05:30 | 2026-07-28T15:30:00+05:30 | COMPLETE |
| 2026-07-29 | 24,176.65 | 2026-08-04 | CE ITM2 | NSE-NIFTY-04Aug26-24100-CE | assembled/options/NSE-NIFTY-04Aug26-24100-CE.csv | 75/75 | 76 | 2026-07-29T09:15:00+05:30 | 2026-07-29T15:30:00+05:30 | COMPLETE |
| 2026-07-29 | 24,176.65 | 2026-08-04 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-29 | 24,176.65 | 2026-08-04 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-29 | 24,176.65 | 2026-08-04 | PE ITM3 | NSE-NIFTY-04Aug26-24300-PE | assembled/options/NSE-NIFTY-04Aug26-24300-PE.csv | 75/75 | 76 | 2026-07-29T09:15:00+05:30 | 2026-07-29T15:30:00+05:30 | COMPLETE |
| 2026-07-30 | 24,250.40 | 2026-08-04 | CE ITM2 | NSE-NIFTY-04Aug26-24200-CE | assembled/options/NSE-NIFTY-04Aug26-24200-CE.csv | 75/75 | 75 | 2026-07-30T09:15:00+05:30 | 2026-07-30T15:25:00+05:30 | COMPLETE |
| 2026-07-30 | 24,250.40 | 2026-08-04 | CE ITM3 | NSE-NIFTY-04Aug26-24150-CE | assembled/options/NSE-NIFTY-04Aug26-24150-CE.csv | 75/75 | 76 | 2026-07-30T09:15:00+05:30 | 2026-07-30T15:30:00+05:30 | COMPLETE |
| 2026-07-30 | 24,250.40 | 2026-08-04 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-07-30 | 24,250.40 | 2026-08-04 | PE ITM3 | NSE-NIFTY-04Aug26-24400-PE | assembled/options/NSE-NIFTY-04Aug26-24400-PE.csv | 75/75 | 76 | 2026-07-30T09:15:00+05:30 | 2026-07-30T15:30:00+05:30 | COMPLETE |
| 2026-07-31 | 24,359.80 | 2026-08-04 | CE ITM2 | NSE-NIFTY-04Aug26-24300-CE | assembled/options/NSE-NIFTY-04Aug26-24300-CE.csv | 75/75 | 76 | 2026-07-31T09:15:00+05:30 | 2026-07-31T15:30:00+05:30 | COMPLETE |
| 2026-07-31 | 24,359.80 | 2026-08-04 | CE ITM3 | NSE-NIFTY-04Aug26-24250-CE | assembled/options/NSE-NIFTY-04Aug26-24250-CE.csv | 75/75 | 76 | 2026-07-31T09:15:00+05:30 | 2026-07-31T15:30:00+05:30 | COMPLETE |
| 2026-07-31 | 24,359.80 | 2026-08-04 | PE ITM2 | NSE-NIFTY-04Aug26-24450-PE | assembled/options/NSE-NIFTY-04Aug26-24450-PE.csv | 75/75 | 76 | 2026-07-31T09:15:00+05:30 | 2026-07-31T15:30:00+05:30 | COMPLETE |
| 2026-07-31 | 24,359.80 | 2026-08-04 | PE ITM3 | NSE-NIFTY-04Aug26-24500-PE | assembled/options/NSE-NIFTY-04Aug26-24500-PE.csv | 75/75 | 76 | 2026-07-31T09:15:00+05:30 | 2026-07-31T15:30:00+05:30 | COMPLETE |
| 2026-08-03 | 24,568.00 | 2026-08-04 | CE ITM2 | NSE-NIFTY-04Aug26-24500-CE | assembled/options/NSE-NIFTY-04Aug26-24500-CE.csv | 75/75 | 78 | 2026-08-03T09:15:00+05:30 | 2026-08-03T15:40:00+05:30 | COMPLETE |
| 2026-08-03 | 24,568.00 | 2026-08-04 | CE ITM3 | NSE-NIFTY-04Aug26-24450-CE | assembled/options/NSE-NIFTY-04Aug26-24450-CE.csv | 75/75 | 78 | 2026-08-03T09:15:00+05:30 | 2026-08-03T15:40:00+05:30 | COMPLETE |
| 2026-08-03 | 24,568.00 | 2026-08-04 | PE ITM2 | NSE-NIFTY-04Aug26-24650-PE | assembled/options/NSE-NIFTY-04Aug26-24650-PE.csv | 75/75 | 78 | 2026-08-03T09:15:00+05:30 | 2026-08-03T15:40:00+05:30 | COMPLETE |
| 2026-08-03 | 24,568.00 | 2026-08-04 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-04 | 24,653.00 | 2026-08-04 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-04 | 24,653.00 | 2026-08-04 | CE ITM3 | NSE-NIFTY-04Aug26-24550-CE | assembled/options/NSE-NIFTY-04Aug26-24550-CE.csv | 75/75 | 78 | 2026-08-04T09:15:00+05:30 | 2026-08-04T15:40:00+05:30 | COMPLETE |
| 2026-08-04 | 24,653.00 | 2026-08-04 | PE ITM2 | NSE-NIFTY-04Aug26-24750-PE | assembled/options/NSE-NIFTY-04Aug26-24750-PE.csv | 75/75 | 77 | 2026-08-04T09:15:00+05:30 | 2026-08-04T15:35:00+05:30 | COMPLETE |
| 2026-08-04 | 24,653.00 | 2026-08-04 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-05 | 24,646.10 | 2026-08-11 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-05 | 24,646.10 | 2026-08-11 | CE ITM3 | NSE-NIFTY-11Aug26-24500-CE | assembled/options/NSE-NIFTY-11Aug26-24500-CE.csv | 75/75 | 78 | 2026-08-05T09:15:00+05:30 | 2026-08-05T15:40:00+05:30 | COMPLETE |
| 2026-08-05 | 24,646.10 | 2026-08-11 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-05 | 24,646.10 | 2026-08-11 | PE ITM3 | NSE-NIFTY-11Aug26-24750-PE | assembled/options/NSE-NIFTY-11Aug26-24750-PE.csv | 75/75 | 78 | 2026-08-05T09:15:00+05:30 | 2026-08-05T15:40:00+05:30 | COMPLETE |
| 2026-08-06 | 24,632.70 | 2026-08-11 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-06 | 24,632.70 | 2026-08-11 | CE ITM3 | NSE-NIFTY-11Aug26-24500-CE | assembled/options/NSE-NIFTY-11Aug26-24500-CE.csv | 75/75 | 77 | 2026-08-06T09:15:00+05:30 | 2026-08-06T15:35:00+05:30 | COMPLETE |
| 2026-08-06 | 24,632.70 | 2026-08-11 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-06 | 24,632.70 | 2026-08-11 | PE ITM3 | NSE-NIFTY-11Aug26-24750-PE | assembled/options/NSE-NIFTY-11Aug26-24750-PE.csv | 75/75 | 78 | 2026-08-06T09:15:00+05:30 | 2026-08-06T15:40:00+05:30 | COMPLETE |
| 2026-08-07 | 24,535.05 | 2026-08-11 | CE ITM2 | NSE-NIFTY-11Aug26-24450-CE | assembled/options/NSE-NIFTY-11Aug26-24450-CE.csv | 75/75 | 77 | 2026-08-07T09:15:00+05:30 | 2026-08-07T15:35:00+05:30 | COMPLETE |
| 2026-08-07 | 24,535.05 | 2026-08-11 | CE ITM3 | NSE-NIFTY-11Aug26-24400-CE | assembled/options/NSE-NIFTY-11Aug26-24400-CE.csv | 75/75 | 78 | 2026-08-07T09:15:00+05:30 | 2026-08-07T15:40:00+05:30 | COMPLETE |
| 2026-08-07 | 24,535.05 | 2026-08-11 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-07 | 24,535.05 | 2026-08-11 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-10 | 24,584.05 | 2026-08-11 | CE ITM2 | NSE-NIFTY-11Aug26-24500-CE | assembled/options/NSE-NIFTY-11Aug26-24500-CE.csv | 75/75 | 78 | 2026-08-10T09:15:00+05:30 | 2026-08-10T15:40:00+05:30 | COMPLETE |
| 2026-08-10 | 24,584.05 | 2026-08-11 | CE ITM3 | NSE-NIFTY-11Aug26-24450-CE | assembled/options/NSE-NIFTY-11Aug26-24450-CE.csv | 75/75 | 77 | 2026-08-10T09:15:00+05:30 | 2026-08-10T15:35:00+05:30 | COMPLETE |
| 2026-08-10 | 24,584.05 | 2026-08-11 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-10 | 24,584.05 | 2026-08-11 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-11 | 24,575.50 | 2026-08-11 | CE ITM2 | NSE-NIFTY-11Aug26-24500-CE | assembled/options/NSE-NIFTY-11Aug26-24500-CE.csv | 75/75 | 77 | 2026-08-11T09:15:00+05:30 | 2026-08-11T15:35:00+05:30 | COMPLETE |
| 2026-08-11 | 24,575.50 | 2026-08-11 | CE ITM3 | NSE-NIFTY-11Aug26-24450-CE | assembled/options/NSE-NIFTY-11Aug26-24450-CE.csv | 75/75 | 78 | 2026-08-11T09:15:00+05:30 | 2026-08-11T15:40:00+05:30 | COMPLETE |
| 2026-08-11 | 24,575.50 | 2026-08-11 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-11 | 24,575.50 | 2026-08-11 | PE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-12 | 24,469.80 | 2026-08-18 | CE ITM2 | NSE-NIFTY-18Aug26-24400-CE | assembled/options/NSE-NIFTY-18Aug26-24400-CE.csv | 75/75 | 78 | 2026-08-12T09:15:00+05:30 | 2026-08-12T15:40:00+05:30 | COMPLETE |
| 2026-08-12 | 24,469.80 | 2026-08-18 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-12 | 24,469.80 | 2026-08-18 | PE ITM2 | NSE-NIFTY-18Aug26-24550-PE | assembled/options/NSE-NIFTY-18Aug26-24550-PE.csv | 75/75 | 78 | 2026-08-12T09:15:00+05:30 | 2026-08-12T15:40:00+05:30 | COMPLETE |
| 2026-08-12 | 24,469.80 | 2026-08-18 | PE ITM3 | NSE-NIFTY-18Aug26-24600-PE | assembled/options/NSE-NIFTY-18Aug26-24600-PE.csv | 75/75 | 78 | 2026-08-12T09:15:00+05:30 | 2026-08-12T15:40:00+05:30 | COMPLETE |
| 2026-08-13 | 24,409.20 | 2026-08-18 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-13 | 24,409.20 | 2026-08-18 | CE ITM3 | NSE-NIFTY-18Aug26-24300-CE | assembled/options/NSE-NIFTY-18Aug26-24300-CE.csv | 75/75 | 78 | 2026-08-13T09:15:00+05:30 | 2026-08-13T15:40:00+05:30 | COMPLETE |
| 2026-08-13 | 24,409.20 | 2026-08-18 | PE ITM2 | NSE-NIFTY-18Aug26-24500-PE | assembled/options/NSE-NIFTY-18Aug26-24500-PE.csv | 75/75 | 77 | 2026-08-13T09:15:00+05:30 | 2026-08-13T15:35:00+05:30 | COMPLETE |
| 2026-08-13 | 24,409.20 | 2026-08-18 | PE ITM3 | NSE-NIFTY-18Aug26-24550-PE | assembled/options/NSE-NIFTY-18Aug26-24550-PE.csv | 75/75 | 78 | 2026-08-13T09:15:00+05:30 | 2026-08-13T15:40:00+05:30 | COMPLETE |
| 2026-08-14 | 24,363.75 | 2026-08-18 | CE ITM2 | NSE-NIFTY-18Aug26-24300-CE | assembled/options/NSE-NIFTY-18Aug26-24300-CE.csv | 75/75 | 78 | 2026-08-14T09:15:00+05:30 | 2026-08-14T15:40:00+05:30 | COMPLETE |
| 2026-08-14 | 24,363.75 | 2026-08-18 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-14 | 24,363.75 | 2026-08-18 | PE ITM2 | NSE-NIFTY-18Aug26-24450-PE | assembled/options/NSE-NIFTY-18Aug26-24450-PE.csv | 75/75 | 78 | 2026-08-14T09:15:00+05:30 | 2026-08-14T15:40:00+05:30 | COMPLETE |
| 2026-08-14 | 24,363.75 | 2026-08-18 | PE ITM3 | NSE-NIFTY-18Aug26-24500-PE | assembled/options/NSE-NIFTY-18Aug26-24500-PE.csv | 75/75 | 78 | 2026-08-14T09:15:00+05:30 | 2026-08-14T15:40:00+05:30 | COMPLETE |
| 2026-08-17 | 24,350.95 | 2026-08-18 | CE ITM2 | NSE-NIFTY-18Aug26-24300-CE | assembled/options/NSE-NIFTY-18Aug26-24300-CE.csv | 75/75 | 78 | 2026-08-17T09:15:00+05:30 | 2026-08-17T15:40:00+05:30 | COMPLETE |
| 2026-08-17 | 24,350.95 | 2026-08-18 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-17 | 24,350.95 | 2026-08-18 | PE ITM2 | NSE-NIFTY-18Aug26-24450-PE | assembled/options/NSE-NIFTY-18Aug26-24450-PE.csv | 75/75 | 78 | 2026-08-17T09:15:00+05:30 | 2026-08-17T15:40:00+05:30 | COMPLETE |
| 2026-08-17 | 24,350.95 | 2026-08-18 | PE ITM3 | NSE-NIFTY-18Aug26-24500-PE | assembled/options/NSE-NIFTY-18Aug26-24500-PE.csv | 75/75 | 78 | 2026-08-17T09:15:00+05:30 | 2026-08-17T15:40:00+05:30 | COMPLETE |
| 2026-08-18 | 24,223.05 | 2026-08-18 | CE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-18 | 24,223.05 | 2026-08-18 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-18 | 24,223.05 | 2026-08-18 | PE ITM2 | NSE-NIFTY-18Aug26-24300-PE | assembled/options/NSE-NIFTY-18Aug26-24300-PE.csv | 75/75 | 78 | 2026-08-18T09:15:00+05:30 | 2026-08-18T15:40:00+05:30 | COMPLETE |
| 2026-08-18 | 24,223.05 | 2026-08-18 | PE ITM3 | NSE-NIFTY-18Aug26-24350-PE | assembled/options/NSE-NIFTY-18Aug26-24350-PE.csv | 75/75 | 77 | 2026-08-18T09:15:00+05:30 | 2026-08-18T15:35:00+05:30 | COMPLETE |
| 2026-08-19 | 24,163.05 | 2026-08-25 | CE ITM2 | NSE-NIFTY-25Aug26-24100-CE | assembled/options/NSE-NIFTY-25Aug26-24100-CE.csv | 75/75 | 78 | 2026-08-19T09:15:00+05:30 | 2026-08-19T15:40:00+05:30 | COMPLETE |
| 2026-08-19 | 24,163.05 | 2026-08-25 | CE ITM3 | NSE-NIFTY-25Aug26-24050-CE | assembled/options/NSE-NIFTY-25Aug26-24050-CE.csv | 75/75 | 78 | 2026-08-19T09:15:00+05:30 | 2026-08-19T15:40:00+05:30 | COMPLETE |
| 2026-08-19 | 24,163.05 | 2026-08-25 | PE ITM2 | NSE-NIFTY-25Aug26-24250-PE | assembled/options/NSE-NIFTY-25Aug26-24250-PE.csv | 75/75 | 78 | 2026-08-19T09:15:00+05:30 | 2026-08-19T15:40:00+05:30 | COMPLETE |
| 2026-08-19 | 24,163.05 | 2026-08-25 | PE ITM3 | NSE-NIFTY-25Aug26-24300-PE | assembled/options/NSE-NIFTY-25Aug26-24300-PE.csv | 75/75 | 77 | 2026-08-19T09:15:00+05:30 | 2026-08-19T15:35:00+05:30 | COMPLETE |
| 2026-08-20 | 24,225.20 | 2026-08-25 | CE ITM2 | NSE-NIFTY-25Aug26-24150-CE | assembled/options/NSE-NIFTY-25Aug26-24150-CE.csv | 75/75 | 77 | 2026-08-20T09:15:00+05:30 | 2026-08-20T15:35:00+05:30 | COMPLETE |
| 2026-08-20 | 24,225.20 | 2026-08-25 | CE ITM3 | NSE-NIFTY-25Aug26-24100-CE | assembled/options/NSE-NIFTY-25Aug26-24100-CE.csv | 75/75 | 77 | 2026-08-20T09:15:00+05:30 | 2026-08-20T15:35:00+05:30 | COMPLETE |
| 2026-08-20 | 24,225.20 | 2026-08-25 | PE ITM2 | NSE-NIFTY-25Aug26-24300-PE | assembled/options/NSE-NIFTY-25Aug26-24300-PE.csv | 75/75 | 78 | 2026-08-20T09:15:00+05:30 | 2026-08-20T15:40:00+05:30 | COMPLETE |
| 2026-08-20 | 24,225.20 | 2026-08-25 | PE ITM3 | NSE-NIFTY-25Aug26-24350-PE | assembled/options/NSE-NIFTY-25Aug26-24350-PE.csv | 75/75 | 78 | 2026-08-20T09:15:00+05:30 | 2026-08-20T15:40:00+05:30 | COMPLETE |
| 2026-08-21 | 24,282.00 | 2026-08-25 | CE ITM2 | NSE-NIFTY-25Aug26-24200-CE | assembled/options/NSE-NIFTY-25Aug26-24200-CE.csv | 75/75 | 78 | 2026-08-21T09:15:00+05:30 | 2026-08-21T15:40:00+05:30 | COMPLETE |
| 2026-08-21 | 24,282.00 | 2026-08-25 | CE ITM3 | NSE-NIFTY-25Aug26-24150-CE | assembled/options/NSE-NIFTY-25Aug26-24150-CE.csv | 75/75 | 78 | 2026-08-21T09:15:00+05:30 | 2026-08-21T15:40:00+05:30 | COMPLETE |
| 2026-08-21 | 24,282.00 | 2026-08-25 | PE ITM2 | NSE-NIFTY-25Aug26-24350-PE | assembled/options/NSE-NIFTY-25Aug26-24350-PE.csv | 75/75 | 78 | 2026-08-21T09:15:00+05:30 | 2026-08-21T15:40:00+05:30 | COMPLETE |
| 2026-08-21 | 24,282.00 | 2026-08-25 | PE ITM3 | NSE-NIFTY-25Aug26-24400-PE | assembled/options/NSE-NIFTY-25Aug26-24400-PE.csv | 75/75 | 78 | 2026-08-21T09:15:00+05:30 | 2026-08-21T15:40:00+05:30 | COMPLETE |
| 2026-08-24 | 24,291.05 | 2026-08-25 | CE ITM2 | NSE-NIFTY-25Aug26-24200-CE | assembled/options/NSE-NIFTY-25Aug26-24200-CE.csv | 75/75 | 78 | 2026-08-24T09:15:00+05:30 | 2026-08-24T15:40:00+05:30 | COMPLETE |
| 2026-08-24 | 24,291.05 | 2026-08-25 | CE ITM3 | NSE-NIFTY-25Aug26-24150-CE | assembled/options/NSE-NIFTY-25Aug26-24150-CE.csv | 75/75 | 78 | 2026-08-24T09:15:00+05:30 | 2026-08-24T15:40:00+05:30 | COMPLETE |
| 2026-08-24 | 24,291.05 | 2026-08-25 | PE ITM2 | NSE-NIFTY-25Aug26-24350-PE | assembled/options/NSE-NIFTY-25Aug26-24350-PE.csv | 75/75 | 78 | 2026-08-24T09:15:00+05:30 | 2026-08-24T15:40:00+05:30 | COMPLETE |
| 2026-08-24 | 24,291.05 | 2026-08-25 | PE ITM3 | NSE-NIFTY-25Aug26-24400-PE | assembled/options/NSE-NIFTY-25Aug26-24400-PE.csv | 75/75 | 77 | 2026-08-24T09:15:00+05:30 | 2026-08-24T15:35:00+05:30 | COMPLETE |
| 2026-08-25 | 24,182.45 | 2026-08-25 | CE ITM2 | NSE-NIFTY-25Aug26-24100-CE | assembled/options/NSE-NIFTY-25Aug26-24100-CE.csv | 75/75 | 78 | 2026-08-25T09:15:00+05:30 | 2026-08-25T15:40:00+05:30 | COMPLETE |
| 2026-08-25 | 24,182.45 | 2026-08-25 | CE ITM3 | NSE-NIFTY-25Aug26-24050-CE | assembled/options/NSE-NIFTY-25Aug26-24050-CE.csv | 75/75 | 77 | 2026-08-25T09:15:00+05:30 | 2026-08-25T15:35:00+05:30 | COMPLETE |
| 2026-08-25 | 24,182.45 | 2026-08-25 | PE ITM2 | NSE-NIFTY-25Aug26-24250-PE | assembled/options/NSE-NIFTY-25Aug26-24250-PE.csv | 75/75 | 78 | 2026-08-25T09:15:00+05:30 | 2026-08-25T15:40:00+05:30 | COMPLETE |
| 2026-08-25 | 24,182.45 | 2026-08-25 | PE ITM3 | NSE-NIFTY-25Aug26-24300-PE | assembled/options/NSE-NIFTY-25Aug26-24300-PE.csv | 75/75 | 77 | 2026-08-25T09:15:00+05:30 | 2026-08-25T15:35:00+05:30 | COMPLETE |
| 2026-08-26 | 24,343.05 | 2026-09-01 | CE ITM2 | NSE-NIFTY-01Sep26-24250-CE | assembled/options/NSE-NIFTY-01Sep26-24250-CE.csv | 75/75 | 78 | 2026-08-26T09:15:00+05:30 | 2026-08-26T15:40:00+05:30 | COMPLETE |
| 2026-08-26 | 24,343.05 | 2026-09-01 | CE ITM3 | NSE-NIFTY-01Sep26-24200-CE | assembled/options/NSE-NIFTY-01Sep26-24200-CE.csv | 75/75 | 78 | 2026-08-26T09:15:00+05:30 | 2026-08-26T15:40:00+05:30 | COMPLETE |
| 2026-08-26 | 24,343.05 | 2026-09-01 | PE ITM2 | NSE-NIFTY-01Sep26-24400-PE | assembled/options/NSE-NIFTY-01Sep26-24400-PE.csv | 75/75 | 78 | 2026-08-26T09:15:00+05:30 | 2026-08-26T15:40:00+05:30 | COMPLETE |
| 2026-08-26 | 24,343.05 | 2026-09-01 | PE ITM3 | NSE-NIFTY-01Sep26-24450-PE | assembled/options/NSE-NIFTY-01Sep26-24450-PE.csv | 75/75 | 78 | 2026-08-26T09:15:00+05:30 | 2026-08-26T15:40:00+05:30 | COMPLETE |
| 2026-08-27 | 24,266.85 | 2026-09-01 | CE ITM2 | NSE-NIFTY-01Sep26-24200-CE | assembled/options/NSE-NIFTY-01Sep26-24200-CE.csv | 75/75 | 78 | 2026-08-27T09:15:00+05:30 | 2026-08-27T15:40:00+05:30 | COMPLETE |
| 2026-08-27 | 24,266.85 | 2026-09-01 | CE ITM3 | NSE-NIFTY-01Sep26-24150-CE | assembled/options/NSE-NIFTY-01Sep26-24150-CE.csv | 75/75 | 78 | 2026-08-27T09:15:00+05:30 | 2026-08-27T15:40:00+05:30 | COMPLETE |
| 2026-08-27 | 24,266.85 | 2026-09-01 | PE ITM2 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-27 | 24,266.85 | 2026-09-01 | PE ITM3 | NSE-NIFTY-01Sep26-24400-PE | assembled/options/NSE-NIFTY-01Sep26-24400-PE.csv | 75/75 | 78 | 2026-08-27T09:15:00+05:30 | 2026-08-27T15:40:00+05:30 | COMPLETE |
| 2026-08-28 | 24,128.95 | 2026-09-01 | CE ITM2 | NSE-NIFTY-01Sep26-24050-CE | assembled/options/NSE-NIFTY-01Sep26-24050-CE.csv | 75/75 | 78 | 2026-08-28T09:15:00+05:30 | 2026-08-28T15:40:00+05:30 | COMPLETE |
| 2026-08-28 | 24,128.95 | 2026-09-01 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-28 | 24,128.95 | 2026-09-01 | PE ITM2 | NSE-NIFTY-01Sep26-24200-PE | assembled/options/NSE-NIFTY-01Sep26-24200-PE.csv | 75/75 | 78 | 2026-08-28T09:15:00+05:30 | 2026-08-28T15:40:00+05:30 | COMPLETE |
| 2026-08-28 | 24,128.95 | 2026-09-01 | PE ITM3 | NSE-NIFTY-01Sep26-24250-PE | assembled/options/NSE-NIFTY-01Sep26-24250-PE.csv | 75/75 | 78 | 2026-08-28T09:15:00+05:30 | 2026-08-28T15:40:00+05:30 | COMPLETE |
| 2026-08-31 | 24,117.10 | 2026-09-01 | CE ITM2 | NSE-NIFTY-01Sep26-24050-CE | assembled/options/NSE-NIFTY-01Sep26-24050-CE.csv | 75/75 | 78 | 2026-08-31T09:15:00+05:30 | 2026-08-31T15:40:00+05:30 | COMPLETE |
| 2026-08-31 | 24,117.10 | 2026-09-01 | CE ITM3 | N/A | N/A | 0/75 | 0 | — | — | CATALOG MISSING |
| 2026-08-31 | 24,117.10 | 2026-09-01 | PE ITM2 | NSE-NIFTY-01Sep26-24200-PE | assembled/options/NSE-NIFTY-01Sep26-24200-PE.csv | 75/75 | 78 | 2026-08-31T09:15:00+05:30 | 2026-08-31T15:40:00+05:30 | COMPLETE |
| 2026-08-31 | 24,117.10 | 2026-09-01 | PE ITM3 | NSE-NIFTY-01Sep26-24250-PE | assembled/options/NSE-NIFTY-01Sep26-24250-PE.csv | 75/75 | 78 | 2026-08-31T09:15:00+05:30 | 2026-08-31T15:40:00+05:30 | COMPLETE |

## 6. Data completeness

| Measure | July–August result |
| --- | --- |
| Trading days | 44: July 23; August 21 |
| Underlying expected/available | 3,300/3,300 regular bars; 100%; zero missing session intervals |
| Expected option contract-days | 176 |
| Exact Groww catalog slots available | 111/176 (63.1%) |
| Complete option contract-days | 111; each has 75/75 session bars and 09:15 opening bar |
| Partial option contract-days | 0 |
| Missing/unavailable contract-days | 65; exact contract absent from returned Groww catalog |
| Expected/available option session candles | 13,200/8,325 (63.1%) |
| Missing required candle intervals | 4,875 = 65 unavailable slots × 75 bars; zero gaps within the 111 returned contract-days |
| Fully / partially usable / unusable dates | 17 / 17 / 10 |
| Overall | INCOMPLETE; missing contracts can hide setups and outcomes. |

| Slot | Expected days | Catalog slots | Complete | Partial | Missing |
| --- | --- | --- | --- | --- | --- |
| CE ITM2 | 44 | 29 | 29 | 0 | 15 |
| CE ITM3 | 44 | 27 | 27 | 0 | 17 |
| PE ITM2 | 44 | 26 | 26 | 0 | 18 |
| PE ITM3 | 44 | 29 | 29 | 0 | 15 |
| Total | 176 | 111 | 111 | 0 | 65 |

| Month | Sessions | Available slots | Fully usable | Partially usable | Unusable |
| --- | --- | --- | --- | --- | --- |
| 2026-07 | 23 | 49/92 (53.3%) | 11 | 2 | 10 |
| 2026-08 | 21 | 62/84 (73.8%) | 6 | 15 | 0 |

**Downloaded this run:** 15 missing contract-days across 8 exact Groww symbols; 1,168 raw 5-minute rows. Every downloaded date now has 75/75 regular-session bars. These were previously known symbols with missing local data. The 65 absent catalog slots were not queried using constructed symbols.

## 7. Level-to-Level results
Only TARGET/SL points are treated as resolved gross premium points. Skipped candidates have no points. Fees, slippage, sizing, and portfolio capital are not modeled. Drawdown is the peak-to-trough cumulative sum of resolved contract points ordered by exit time (then entry and symbol), with initial equity zero; this is descriptive, not portfolio return.

| Period | Setups | Valid | Skipped | Targets | SL | Open | Ambiguous | Gross points | Avg resolved | Median | Avg winner | Avg loser | Target / resolved | MFE avg* | MAE avg* | Hold min | Max DD | Win streak | Loss streak |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07 | 34 | 25 | 9 | 3 | 22 | 0 | 0 | -64.70 | -2.59 | -6.70 | 37.10 | -8.00 | 12.0% | 16.01 | -11.64 | 30.00 | 65.30 | 2 | 9 |
| 2026-08 | 38 | 16 | 22 | 9 | 7 | 0 | 0 | 146.10 | 9.13 | 5.55 | 20.54 | -5.54 | 56.2% | 15.86 | -7.08 | 26.25 | 25.70 | 4 | 3 |
| Combined | 72 | 41 | 31 | 12 | 29 | 0 | 0 | 81.40 | 1.99 | -4.00 | 24.68 | -7.41 | 29.3% | 15.95 | -9.86 | 28.54 | 74.50 | 4 | 9 |

*MFE/MAE average over resolved TARGET/SL trades only. There were no ambiguous outcomes. July results: 3 targets/22 SL among 25 resolved, −64.70 points. August: 9 targets/7 SL among 16 resolved, +146.10 points. August’s 22–28 Aug week contributed +111.85 points; 25 Aug alone +90.90. Totals are concentrated and month distributions differ; missing data limits interpretation.

| Side/rank | Setups | Targets | SL | Skipped | Resolved points |
| --- | --- | --- | --- | --- | --- |
| CE | 39 | 5 | 17 | 17 | 64.95 |
| PE | 33 | 7 | 12 | 14 | 16.45 |
| ITM2 | 36 | 5 | 16 | 15 | -10.20 |
| ITM3 | 36 | 7 | 13 | 16 | 91.60 |

| Entry-time bucket | Setups | Targets | SL | Skipped |
| --- | --- | --- | --- | --- |
| 09:15–09:59 | 55 | 8 | 22 | 25 |
| 10:00–10:59 | 17 | 4 | 7 | 6 |

| Weekday | Setups | Targets | SL | Skipped | Resolved points |
| --- | --- | --- | --- | --- | --- |
| Monday | 17 | 4 | 7 | 6 | 14.90 |
| Tuesday | 18 | 7 | 4 | 7 | 146.45 |
| Wednesday | 15 | 1 | 6 | 8 | -0.65 |
| Thursday | 11 | 0 | 4 | 7 | -33.80 |
| Friday | 11 | 0 | 8 | 3 | -45.50 |

### L2L weekly results

| Month | Week label | Setups | Targets | SL | Skipped | Resolved points |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07 | 2026-07-04/2026-07-10 | 8 | 0 | 6 | 2 | -33.10 |
| 2026-07 | 2026-07-11/2026-07-17 | 8 | 1 | 3 | 4 | 33.15 |
| 2026-07 | 2026-07-18/2026-07-24 | 6 | 0 | 4 | 2 | -28.25 |
| 2026-07 | 2026-07-25/2026-07-31 | 12 | 2 | 9 | 1 | -36.50 |
| 2026-08 | 2026-08-01/2026-08-07 | 5 | 3 | 2 | 0 | 36.60 |
| 2026-08 | 2026-08-08/2026-08-14 | 7 | 0 | 1 | 6 | -9.05 |
| 2026-08 | 2026-08-15/2026-08-21 | 9 | 2 | 2 | 5 | 8.60 |
| 2026-08 | 2026-08-22/2026-08-28 | 16 | 4 | 1 | 11 | 111.85 |
| 2026-08 | 2026-08-29/2026-09-04 | 1 | 0 | 1 | 0 | -1.90 |

### L2L daily results

| Date | Data status | Catalog slots | Expiry | Setups | Targets | SL | Skipped | Resolved points |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07-01 | UNUSABLE | 0/4 | 2026-07-07 | 0 | 0 | 0 | 0 | — |
| 2026-07-02 | UNUSABLE | 0/4 | 2026-07-07 | 0 | 0 | 0 | 0 | — |
| 2026-07-03 | UNUSABLE | 0/4 | 2026-07-07 | 0 | 0 | 0 | 0 | — |
| 2026-07-06 | UNUSABLE | 0/4 | 2026-07-07 | 0 | 0 | 0 | 0 | — |
| 2026-07-07 | UNUSABLE | 0/4 | 2026-07-07 | 0 | 0 | 0 | 0 | — |
| 2026-07-08 | FULL | 4/4 | 2026-07-14 | 4 | 0 | 4 | 0 | -27.70 |
| 2026-07-09 | FULL | 4/4 | 2026-07-14 | 2 | 0 | 0 | 2 | 0.00 |
| 2026-07-10 | FULL | 4/4 | 2026-07-14 | 2 | 0 | 2 | 0 | -5.40 |
| 2026-07-13 | FULL | 4/4 | 2026-07-14 | 4 | 0 | 2 | 2 | -12.65 |
| 2026-07-14 | FULL | 4/4 | 2026-07-14 | 4 | 1 | 1 | 2 | 45.80 |
| 2026-07-15 | UNUSABLE | 0/4 | 2026-07-21 | 0 | 0 | 0 | 0 | — |
| 2026-07-16 | UNUSABLE | 0/4 | 2026-07-21 | 0 | 0 | 0 | 0 | — |
| 2026-07-17 | UNUSABLE | 0/4 | 2026-07-21 | 0 | 0 | 0 | 0 | — |
| 2026-07-20 | UNUSABLE | 0/4 | 2026-07-21 | 0 | 0 | 0 | 0 | — |
| 2026-07-21 | UNUSABLE | 0/4 | 2026-07-21 | 0 | 0 | 0 | 0 | — |
| 2026-07-22 | FULL | 4/4 | 2026-07-28 | 2 | 0 | 0 | 2 | 0.00 |
| 2026-07-23 | FULL | 4/4 | 2026-07-28 | 2 | 0 | 2 | 0 | -8.15 |
| 2026-07-24 | FULL | 4/4 | 2026-07-28 | 2 | 0 | 2 | 0 | -20.10 |
| 2026-07-27 | FULL | 4/4 | 2026-07-28 | 4 | 2 | 2 | 0 | 20.40 |
| 2026-07-28 | FULL | 4/4 | 2026-07-28 | 4 | 0 | 3 | 1 | -26.00 |
| 2026-07-29 | PARTIAL | 2/4 | 2026-08-04 | 1 | 0 | 1 | 0 | -8.75 |
| 2026-07-30 | PARTIAL | 3/4 | 2026-08-04 | 1 | 0 | 1 | 0 | -11.90 |
| 2026-07-31 | FULL | 4/4 | 2026-08-04 | 2 | 0 | 2 | 0 | -10.25 |
| 2026-08-03 | PARTIAL | 3/4 | 2026-08-04 | 1 | 0 | 1 | 0 | -9.75 |
| 2026-08-04 | PARTIAL | 2/4 | 2026-08-04 | 2 | 2 | 0 | 0 | 23.55 |
| 2026-08-05 | PARTIAL | 2/4 | 2026-08-11 | 1 | 1 | 0 | 0 | 36.55 |
| 2026-08-06 | PARTIAL | 2/4 | 2026-08-11 | 1 | 0 | 1 | 0 | -13.75 |
| 2026-08-07 | PARTIAL | 2/4 | 2026-08-11 | 0 | 0 | 0 | 0 | — |
| 2026-08-10 | PARTIAL | 2/4 | 2026-08-11 | 2 | 0 | 0 | 2 | 0.00 |
| 2026-08-11 | PARTIAL | 2/4 | 2026-08-11 | 2 | 0 | 0 | 2 | 0.00 |
| 2026-08-12 | PARTIAL | 3/4 | 2026-08-18 | 1 | 0 | 0 | 1 | 0.00 |
| 2026-08-13 | PARTIAL | 3/4 | 2026-08-18 | 1 | 0 | 0 | 1 | 0.00 |
| 2026-08-14 | PARTIAL | 3/4 | 2026-08-18 | 1 | 0 | 1 | 0 | -9.05 |
| 2026-08-17 | PARTIAL | 3/4 | 2026-08-18 | 1 | 0 | 1 | 0 | -2.90 |
| 2026-08-18 | PARTIAL | 2/4 | 2026-08-18 | 2 | 2 | 0 | 0 | 12.20 |
| 2026-08-19 | FULL | 4/4 | 2026-08-25 | 2 | 0 | 0 | 2 | 0.00 |
| 2026-08-20 | FULL | 4/4 | 2026-08-25 | 2 | 0 | 0 | 2 | 0.00 |
| 2026-08-21 | FULL | 4/4 | 2026-08-25 | 2 | 0 | 1 | 1 | -0.70 |
| 2026-08-24 | FULL | 4/4 | 2026-08-25 | 4 | 2 | 0 | 2 | 21.70 |
| 2026-08-25 | FULL | 4/4 | 2026-08-25 | 4 | 2 | 0 | 2 | 90.90 |
| 2026-08-26 | FULL | 4/4 | 2026-09-01 | 4 | 0 | 1 | 3 | -0.75 |
| 2026-08-27 | PARTIAL | 3/4 | 2026-09-01 | 2 | 0 | 0 | 2 | 0.00 |
| 2026-08-28 | PARTIAL | 3/4 | 2026-09-01 | 2 | 0 | 0 | 2 | 0.00 |
| 2026-08-31 | PARTIAL | 3/4 | 2026-09-01 | 1 | 0 | 1 | 0 | -1.90 |

## 8. Ekalayava entries and post-entry behavior
Canonical Ekalayava has no defined SL, opposite-signal exit, or forced EOD exit. Outcomes are therefore observed opening-high target touches or OPEN at the end of available regular-session data. Touch fraction is descriptive, not accuracy/win rate. The engine contains a diagnostic target-distance field; it is not treated as realized P&L here.

| Period | Entries | CE | PE | ITM2 | ITM3 | Touches | OPEN | Touch fraction | Mean MFE | Median MFE | Mean MAE | Median MAE | Mean target distance | Median distance | Mean time-to-touch min | Median min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-07 | 21 | 6 | 15 | 9 | 12 | 11 | 10 | 52.4% | 29.15 | 19.70 | -29.73 | -18.15 | 45.76 | 44.05 | 119.5 | 85.0 |
| 2026-08 | 26 | 16 | 10 | 14 | 12 | 11 | 15 | 42.3% | 23.92 | 17.45 | -20.44 | -14.10 | 46.90 | 33.77 | 70.9 | 55.0 |
| Combined | 47 | 22 | 25 | 23 | 24 | 22 | 25 | 46.8% | 26.25 | 17.65 | -24.59 | -15.60 | 46.39 | 35.95 | 95.2 | 65.0 |

Target-time figures apply only to target-touch paths; unresolved OPEN entries are censored at the session’s last observed bar. MFE/MAE are post-entry observed excursions through first touch or session end, not realized returns.

### Ekalayava by side

| Side | Entries | Target touches | OPEN | Touch fraction | Mean MFE | Mean MAE | Mean target distance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Side CE | 22 | 9 | 13 | 40.9% | 25.52 | -20.11 | 54.27 |
| Side PE | 25 | 13 | 12 | 52.0% | 26.90 | -28.54 | 39.46 |

### Ekalayava by itm rank

| ITM rank | Entries | Target touches | OPEN | Touch fraction | Mean MFE | Mean MAE | Mean target distance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ITM rank 2 | 23 | 11 | 12 | 47.8% | 27.84 | -21.30 | 47.77 |
| ITM rank 3 | 24 | 11 | 13 | 45.8% | 24.74 | -27.75 | 45.08 |

| Entry-time bucket | Entries | Touches | OPEN | Mean MFE | Mean MAE |
| --- | --- | --- | --- | --- | --- |
| 11:00–12:59 | 13 | 4 | 9 | 43.54 | -23.69 |
| 10:00–10:59 | 22 | 12 | 10 | 20.55 | -25.79 |
| 09:15–09:59 | 10 | 6 | 4 | 20.24 | -26.34 |
| 13:00–15:15 | 2 | 0 | 2 | 6.67 | -8.55 |

| Weekday | Entries | Touches | OPEN | Mean MFE | Mean MAE |
| --- | --- | --- | --- | --- | --- |
| Monday | 10 | 5 | 5 | 30.03 | -18.06 |
| Tuesday | 8 | 6 | 2 | 14.32 | -33.11 |
| Wednesday | 9 | 3 | 6 | 11.94 | -24.83 |
| Thursday | 11 | 3 | 8 | 42.48 | -29.35 |
| Friday | 9 | 5 | 4 | 27.15 | -18.23 |

### Ekalayava weekly results

| Month | Week label | Entries | Touches | OPEN | Mean MFE | Mean MAE |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07 | 2026-07-04/2026-07-10 | 4 | 0 | 4 | 45.52 | -26.51 |
| 2026-07 | 2026-07-11/2026-07-17 | 4 | 2 | 2 | 8.26 | -69.96 |
| 2026-07 | 2026-07-18/2026-07-24 | 4 | 2 | 2 | 48.49 | -14.29 |
| 2026-07 | 2026-07-25/2026-07-31 | 9 | 7 | 2 | 22.56 | -20.14 |
| 2026-08 | 2026-08-01/2026-08-07 | 3 | 1 | 2 | 15.40 | -19.23 |
| 2026-08 | 2026-08-08/2026-08-14 | 5 | 2 | 3 | 25.96 | -33.06 |
| 2026-08 | 2026-08-15/2026-08-21 | 7 | 1 | 6 | 16.49 | -26.64 |
| 2026-08 | 2026-08-22/2026-08-28 | 10 | 6 | 4 | 23.58 | -12.10 |
| 2026-08 | 2026-08-29/2026-09-04 | 1 | 1 | 0 | 94.65 | -1.15 |

### Ekalayava daily results

| Date | Data status | Entries | Touches | OPEN | Mean MFE | Mean MAE |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-07-01 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-02 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-03 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-06 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-07 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-08 | FULL | 0 | 0 | 0 | — | — |
| 2026-07-09 | FULL | 2 | 0 | 2 | 75.37 | -16.88 |
| 2026-07-10 | FULL | 2 | 0 | 2 | 15.68 | -36.15 |
| 2026-07-13 | FULL | 2 | 0 | 2 | -0.05 | -58.08 |
| 2026-07-14 | FULL | 2 | 2 | 0 | 16.58 | -81.85 |
| 2026-07-15 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-16 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-17 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-20 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-21 | UNUSABLE | 0 | 0 | 0 | — | — |
| 2026-07-22 | FULL | 2 | 0 | 2 | 12.30 | -24.38 |
| 2026-07-23 | FULL | 2 | 2 | 0 | 84.67 | -4.20 |
| 2026-07-24 | FULL | 0 | 0 | 0 | — | — |
| 2026-07-27 | FULL | 3 | 3 | 0 | 35.83 | -10.13 |
| 2026-07-28 | FULL | 2 | 2 | 0 | 14.57 | -6.30 |
| 2026-07-29 | PARTIAL | 1 | 0 | 1 | 0.30 | -45.60 |
| 2026-07-30 | PARTIAL | 1 | 0 | 1 | 22.45 | -64.05 |
| 2026-07-31 | FULL | 2 | 2 | 0 | 21.80 | -14.30 |
| 2026-08-03 | PARTIAL | 1 | 0 | 1 | 17.60 | -14.05 |
| 2026-08-04 | PARTIAL | 0 | 0 | 0 | — | — |
| 2026-08-05 | PARTIAL | 1 | 1 | 0 | 20.90 | -2.30 |
| 2026-08-06 | PARTIAL | 1 | 0 | 1 | 7.70 | -41.35 |
| 2026-08-07 | PARTIAL | 0 | 0 | 0 | — | — |
| 2026-08-10 | PARTIAL | 0 | 0 | 0 | — | — |
| 2026-08-11 | PARTIAL | 2 | 0 | 2 | 6.40 | -35.62 |
| 2026-08-12 | PARTIAL | 1 | 0 | 1 | 13.75 | -50.00 |
| 2026-08-13 | PARTIAL | 1 | 1 | 0 | 53.40 | -26.50 |
| 2026-08-14 | PARTIAL | 1 | 1 | 0 | 49.85 | -17.55 |
| 2026-08-17 | PARTIAL | 1 | 1 | 0 | 67.30 | -1.80 |
| 2026-08-18 | PARTIAL | 0 | 0 | 0 | — | — |
| 2026-08-19 | FULL | 2 | 0 | 2 | 5.50 | -34.85 |
| 2026-08-20 | FULL | 2 | 0 | 2 | 4.95 | -43.67 |
| 2026-08-21 | FULL | 2 | 0 | 2 | 13.60 | -13.80 |
| 2026-08-24 | FULL | 2 | 0 | 2 | 6.67 | -8.55 |
| 2026-08-25 | FULL | 2 | 2 | 0 | 19.75 | -8.65 |
| 2026-08-26 | FULL | 2 | 2 | 0 | 18.45 | -3.55 |
| 2026-08-27 | PARTIAL | 2 | 0 | 2 | 26.85 | -30.70 |
| 2026-08-28 | PARTIAL | 2 | 2 | 0 | 46.18 | -9.03 |
| 2026-08-31 | PARTIAL | 1 | 1 | 0 | 94.65 | -1.15 |

## 9. July–August comparison and data-quality impact
- L2L differed between observed months: July 3 targets/22 SL among 25 resolved (12.0% target proportion), −64.70 resolved points; August 9 targets/7 SL among 16 resolved (56.3%), +146.10. The August 22–28 week and 25 Aug contributed a large share of the August total. This is not a complete-market comparison because 65 expected contract-days are missing.
- Ekalayava had 11 opening-high touches in each month: July 21 entries/10 OPEN (52.4% observed touch fraction), August 26/15 OPEN (42.3%). Mean MFE/MAE were +29.15/−29.73 in July and +23.92/−20.44 in August. Mean time to target touch, among touch paths only, was 119.5 minutes and 70.9 minutes. Exit lifecycle remains undefined.
- Side mix shifted: July Ekalayava was 6 CE/15 PE; August 16 CE/10 PE. L2L was 16 CE/18 PE in July and 23 CE/15 PE in August. Overall ranks were balanced: L2L 36 ITM2/36 ITM3; Ekalayava 23/24. Missing data may change each observed distribution.
- Coverage differs by month: July 11 full, 2 partial, 10 unusable dates; August 6 full, 15 partial, no unusable dates. L2L event count by day status: 50 setups on full dates, 22 on partial dates; Ekalayava: 31 entries on full dates, 16 on partial dates. No strategy events came from unusable dates.

## 10. No-lookahead and execution audit
- Strike selection uses the date’s NIFTY 09:15 open; expiry is selected from Groww’s returned schedule, not later market prices. Absent historical chain slots are not inferred. Current catalog completeness as-of each historical date cannot be proven.
- L2L entry uses a completed red breakdown and the first subsequent completed green candle close. Ekalayava uses the causal `left=2/right=0` swing-high rule, then a later completed candle that breaks/closes above it before the target; it enters at that candle close.
- Future path evaluation starts after entry and stays within the same trading date and 09:15–15:25 regular-session cutoff. Simultaneous SL/target OHLC touches are marked AMBIGUOUS; none occurred. Ekalayava checks target only and otherwise stays OPEN.
- Sources were normalized to timezone-aware timestamps, OHLC-validated, sorted, and deduplicated. Strategy definitions and `app/paper.py` were unchanged. Only contract selection, completeness reporting, and regular-session input filtering were corrected.

## 11. Previously observed recent-data issue (28-Sep to 01-Oct 2026)
The preserved four-session report records 28-Sep underlying 75/75, 29-Sep 58/75, and no underlying candles returned for 30-Sep or 01-Oct. Without each day’s 09:15 underlying open, option selection cannot occur; the absent mappings are downstream of missing underlying data, not evidence of wrong strike/expiry selection. Groww date queries returned no underlying bars on the last two dates. The downloader catches generic fetch exceptions and prints warnings but does not persist raw response/error bodies, so provider-side empty/historical availability versus transient endpoint failure cannot be distinguished. IST date handling does not explain the missing underlying bars. Best-supported cause: Groww historical endpoint response/availability plus inadequate persistent error logging. Detailed evidence remains in `reports/2026-09-28_to_2026-10-01_fresh_market_analysis.md`.

## 12. Limitations and conclusion
The July–August sample is incomplete: 65/176 exact daily slots (36.9%) were missing from the Groww expiry catalogs, heavily concentrated in 01–07 Jul and 15–21 Jul. Those ten dates have no selected options; 17 more dates have only one to three of the four contract slots. Returned files were complete and exact, but the unavailable historical instrument universe prevents a complete five-month conclusion. No alternate provider, constructed contract, or synthetic candle was used.

The observed L2L month distributions diverge; Ekalayava target-touch counts are equal while side mix, excursion summaries, and touch timing differ. These are conditional observations, not a strategy ranking or profitability claim. Ekalayava has no valid realized P&L measurement until its lifecycle is defined. Next, obtain an authoritative historical Groww contract catalog/listing record for the 65 missing slots; if unavailable, preserve this run as incomplete. Keep the Ekalayava lifecycle decision separate and unresolved.

## 13. Verification and safety
- Read-only Groww authentication succeeded. Fifteen missing exact-symbol contract-days were fetched (1,168 raw rows; 1,125 regular-session bars). No orders were placed.
- `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`; no live execution was activated.
- Credentials, `.env`, `secrets.txt`, API keys, and access tokens are excluded from this report and from the intended Git changes.
- Full existing test suite result: **61 passed, 0 failed**.

