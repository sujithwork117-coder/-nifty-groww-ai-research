# Final NIFTY Jan–Sep 2026 Validation

**Requested period:** 2026-01-01 through 2026-09-30 inclusive. **Status: INCOMPLETE DATA; full period retained.** Groww data is available through 2026-09-29. Sep 30 was an NSE trading date but Groww returned no NIFTY underlying candles. No dates, candles, or contracts were fabricated or substituted. This is research only: `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`.

## Results at a glance

| Measure | Result |
|---|---:|
| Exchange sessions in requested window | 185 (includes Feb 1 special Sunday session) |
| Underlying session data | 184/185 sessions; 13,783/13,875 regular bars (99.3%) |
| Option contract-days | 561 complete, 1 partial, 178 missing of 740 expected |
| Option candles | 42,149/55,500 (75.9%); 13,351 intervals missing |
| Usable days | 112 fully usable, 55 partial, 18 unusable |
| Level-to-Level | 361 setups; 203 resolved (58 targets, 145 SL), 157 skipped, 1 ambiguous; +234.85 gross option-premium points |
| Ekalayava | 253 entries; 109 opening-high touches, 144 no-touch observations; all 253 lifecycle outcomes unresolved; no P&L |
| Readiness | L2L: **NOT READY**; Ekalayava: **OBSERVATION-ONLY** |

The 185-session count was cross-checked with the [NSE 2026 F&O holiday circular](https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf), [Jan 15 holiday update](https://nsearchives.nseindia.com/content/circulars/FAOP72262.pdf), and [Feb 1 special-session circular](https://nsearchives.nseindia.com/content/circulars/FAOP72352.pdf). The 184 observed dates include Feb 1 and omit only Sep 30.

## Contract selection audit

The corrected selector processes every date independently: NIFTY 09:15 open → earliest returned expiry on or after that date → exact CE/PE ITM2/ITM3 strikes and symbols from that expiry catalog → that exact symbol’s candles for that date. CE/PE use the same applicable expiry. Missing exact strikes are unavailable, never shifted to another rank or expiry.

Groww returned 39 expiry catalogs for Jan–Sep and 71 contracts in the Oct 6 next-expiry chain. Every Jan–Sep chain had a minimum observed strike spacing of 50 points and all parsed symbol expiry labels matched the catalog expiry. The 50-point spacing is observed catalog convention; it is not defined by the canonical strategy specification. Of 740 expected slots, 562 exact contract symbols were resolved, 174 were absent from the returned catalogs, and the four Sep 30 slots could not be selected because no NIFTY opening candle was available.

### Representative daily map around final weekly expiry rollovers

Bars are regular 5-minute session counts for CE ITM2 / CE ITM3 / PE ITM2 / PE ITM3. `N/A` means the exact contract was absent from the returned catalog. Sep 30 has no spot reference, so no strikes are invented.

| Date / role | NIFTY 09:15 | Applied expiry | CE ITM2 | CE ITM3 | PE ITM2 | PE ITM3 | Bars | All four complete? |
|---|---:|---|---|---|---|---|---|---|
| Jan 27 expiry | 25079.00 | Jan 27 | 25000 NSE-NIFTY-27Jan26-25000-CE | 24950 NSE-NIFTY-27Jan26-24950-CE | 25150 NSE-NIFTY-27Jan26-25150-PE | 25200 NSE-NIFTY-27Jan26-25200-PE | 75/75/75/75 | Yes |
| Jan 28 after | 25248.60 | Feb 03 | 25150 NSE-NIFTY-03Feb26-25150-CE | 25100 NSE-NIFTY-03Feb26-25100-CE | 25300 NSE-NIFTY-03Feb26-25300-PE | 25350 NSE-NIFTY-03Feb26-25350-PE | 75/75/75/75 | Yes |
| Feb 24 expiry | 25641.80 | Feb 24 | 25550 NSE-NIFTY-24Feb26-25550-CE | 25500 NSE-NIFTY-24Feb26-25500-CE | 25700 NSE-NIFTY-24Feb26-25700-PE | 25750 NSE-NIFTY-24Feb26-25750-PE | 75/75/75/75 | Yes |
| Feb 25 after | 25515.05 | Mar 02 | 25450 NSE-NIFTY-02Mar26-25450-CE | 25400 NSE-NIFTY-02Mar26-25400-CE | 25600 NSE-NIFTY-02Mar26-25600-PE | 25650 NSE-NIFTY-02Mar26-25650-PE | 75/75/75/75 | Yes |
| Mar 30 expiry | 22574.70 | Mar 30 | 22500 NSE-NIFTY-30Mar26-22500-CE | N/A | N/A | N/A | 75/0/0/0 | No |
| Apr 01 after | 22878.90 | Apr 07 | N/A | N/A | N/A | N/A | 0/0/0/0 | No |
| Apr 28 expiry | 24044.90 | Apr 28 | 23950 NSE-NIFTY-28Apr26-23950-CE | 23900 NSE-NIFTY-28Apr26-23900-CE | 24100 NSE-NIFTY-28Apr26-24100-PE | 24150 NSE-NIFTY-28Apr26-24150-PE | 75/75/75/75 | Yes |
| Apr 29 after | 24103.00 | May 05 | 24050 NSE-NIFTY-05May26-24050-CE | 24000 NSE-NIFTY-05May26-24000-CE | 24200 NSE-NIFTY-05May26-24200-PE | 24250 NSE-NIFTY-05May26-24250-PE | 75/75/75/75 | Yes |
| May 26 expiry | 24006.75 | May 26 | 23950 NSE-NIFTY-26May26-23950-CE | 23900 NSE-NIFTY-26May26-23900-CE | 24100 NSE-NIFTY-26May26-24100-PE | 24150 NSE-NIFTY-26May26-24150-PE | 75/75/75/75 | Yes |
| May 27 after | 23896.35 | Jun 02 | 23800 NSE-NIFTY-02Jun26-23800-CE | 23750 NSE-NIFTY-02Jun26-23750-CE | 23950 NSE-NIFTY-02Jun26-23950-PE | 24000 NSE-NIFTY-02Jun26-24000-PE | 75/75/75/75 | Yes |
| Jun 30 expiry | 24031.60 | Jun 30 | 23950 NSE-NIFTY-30Jun26-23950-CE | 23900 NSE-NIFTY-30Jun26-23900-CE | 24100 NSE-NIFTY-30Jun26-24100-PE | 24150 NSE-NIFTY-30Jun26-24150-PE | 75/75/75/75 | Yes |
| Jul 01 after | 23908.55 | Jul 07 | N/A | N/A | N/A | N/A | 0/0/0/0 | No |
| Jul 28 expiry | 23973.00 | Jul 28 | 23900 NSE-NIFTY-28Jul26-23900-CE | 23850 NSE-NIFTY-28Jul26-23850-CE | 24050 NSE-NIFTY-28Jul26-24050-PE | 24100 NSE-NIFTY-28Jul26-24100-PE | 75/75/75/75 | Yes |
| Jul 29 after | 24176.65 | Aug 04 | 24100 NSE-NIFTY-04Aug26-24100-CE | N/A | N/A | 24300 NSE-NIFTY-04Aug26-24300-PE | 75/0/0/75 | No |
| Aug 25 expiry | 24182.45 | Aug 25 | 24100 NSE-NIFTY-25Aug26-24100-CE | 24050 NSE-NIFTY-25Aug26-24050-CE | 24250 NSE-NIFTY-25Aug26-24250-PE | 24300 NSE-NIFTY-25Aug26-24300-PE | 75/75/75/75 | Yes |
| Aug 26 after | 24343.05 | Sep 01 | 24250 NSE-NIFTY-01Sep26-24250-CE | 24200 NSE-NIFTY-01Sep26-24200-CE | 24400 NSE-NIFTY-01Sep26-24400-PE | 24450 NSE-NIFTY-01Sep26-24450-PE | 75/75/75/75 | Yes |
| Sep 29 expiry | 22741.45 | Sep 29 | N/A | N/A | N/A | N/A | 0/0/0/0 | No |
| Sep 30 after | N/A | Oct 06 | Not selectable | Not selectable | Not selectable | Not selectable | 0/0/0/0 | No |

This corrected map shows the prior Sep 28–29 fresh-session entries used option contracts that do not resolve to the required exact ITM2/ITM3 symbols in the returned expiry catalog. Those earlier observations are preserved but excluded from this corrected final OOS run.

## Data quality and coverage

All option inputs were clipped to 09:15–15:25 Asia/Kolkata. Underlying source merge: 15,424 unique timestamps, 145 duplicate timestamp keys across source files, 0 conflicting OHLC duplicates, 0 invalid OHLC rows. Option merge: 515 unique symbols from 858 source files; 0 conflicting OHLC duplicates, 0 invalid OHLC rows. No interpolation or forward-fill was used.

| Month | Expected sessions | Underlying present | Expected option slots | Complete | Partial | Missing | Option bars present |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jan | 20 | 20 | 80 | 80 | 0 | 0 | 6000 |
| Feb | 21 | 21 | 84 | 83 | 1 | 0 | 6299 |
| Mar | 19 | 19 | 76 | 37 | 0 | 39 | 2775 |
| Apr | 20 | 20 | 80 | 59 | 0 | 21 | 4425 |
| May | 19 | 19 | 76 | 76 | 0 | 0 | 5700 |
| Jun | 21 | 21 | 84 | 82 | 0 | 2 | 6150 |
| Jul | 23 | 23 | 92 | 49 | 0 | 43 | 3675 |
| Aug | 21 | 21 | 84 | 62 | 0 | 22 | 4650 |
| Sep | 21 | 20 | 84 | 33 | 0 | 51 | 2475 |
| **Total** | **185** | **184** | **740** | **561** | **1** | **178** | **42,149** |

- Underlying: Sep 28 is 75/75 bars; Sep 29 is 58/75 with 17 intervals absent from 14:05–15:25; Sep 30 is 0/75. All 184 dates with source rows have a 09:15 opening candle.
- Option slots: 174 required exact strikes were absent from the returned catalogs; 4 Sep 30 slots were not selectable without the underlying opening price. The exact-symbol retries returned 2,174 regular-session bars for 29 contract-days; 28 are 75/75, Feb 3 PE ITM3 remains 74/75.
- Of 185 expected sessions: 112 fully usable, 55 partially usable, and 18 unusable. Missing slots can suppress setups and outcomes. No events on an unusable day do not imply that no setup would have occurred.

## Backtest results and validation splits

The existing canonical strategy engines were run over every selected exact contract-day with available bars. L2L used its unchanged default 4-point stop buffer and opening-high target. Ekalayava entry remains the causal opening-low break → recovery/swing → completed swing-breakout close. Ekalayava post-entry excursion tracking now observes through the session close after target touches, but it creates no exit.

| Period | Sessions | L2L setups / resolved / target / SL / skipped / points | Ekalayava entries / target touches / no-touch / mean MFE / mean MAE |
|---|---:|---|---|
| Jan–Mar | 60 | 130 / 63 / 19 / 44 / 66 / −3.40 | 94 / 42 / 52 / 71.24 / −58.92 |
| Apr–Jun | 60 | 139 / 85 / 23 / 62 / 54 / +135.65 | 97 / 41 / 56 / 61.23 / −57.26 |
| Jul–Sep | 65 | 92 / 55 / 16 / 39 / 37 / +102.60 | 62 / 26 / 36 / 30.20 / −38.49 |
| Train Jan–Jun | 120 | 269 / 148 / 42 / 106 / 120 / +132.25 | 191 / 83 / 108 / 66.16 / −58.07 |
| Validation Jul–Aug | 44 | 72 / 41 / 12 / 29 / 31 / +81.40 | 47 / 22 / 25 / 33.18 / −34.71 |
| Final OOS Sep | 21 | 20 / 14 / 4 / 10 / 6 / +21.20 | 15 / 4 / 11 / 20.88 / −50.34 |

The OOS period is incomplete: its 15 Ekalayava and 20 L2L setups are observed only through Sep 29, and 33/84 option contract-days are complete. No rules were altered using September. The 3-point sensitivity described in the L2L report is descriptive only; the canonical default remains 4 points.

## Interpretation and limitations

- L2L total resolved gross points are positive in this observed sample, but are concentrated: May is +298.00; the other eight months net −63.15. Five days contribute +545.40 gross points, while positive-day gross contributions total +1,397.80 before negative days. This is not a net-return or profitability conclusion.
- The default four-point L2L result is sensitive to the existing 3/4-point buffer comparison: 4-point yielded 58 target / 145 SL / 157 skipped / 1 ambiguous and +234.85 points; the descriptive 3-point run yielded 51 / 137 / 172 / 1 and +78.20 points. No optimization or rule change was made.
- Ekalayava target touches are not wins. Every entry’s lifecycle remains unresolved because structural stop, alternative exit, end-of-day, expiry and end-of-data handling are not fully specified.
- L2L readiness is **NOT READY** because of the missing data and the live-listener implementation gap. Ekalayava readiness is **OBSERVATION-ONLY**.

## Evidence and reports

- Canonical strategy definitions: `NIFTY_Strategy_Definitions_Level_to_Level_Ekalavya.md`.
- [Level-to-Level detailed validation](l2l_final_validation.md), [Ekalayava detailed validation](ekalayava_final_validation.md), and [paper-trading readiness audit](paper_trading_readiness.md).
- The trace, catalog, selection manifest, missing-data retry manifest, and full event JSON remain in ignored local files under `data/derived/final_jan_sep_2026/`. Raw historical data is not included in Git.
