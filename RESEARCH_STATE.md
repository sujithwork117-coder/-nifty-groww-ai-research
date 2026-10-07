# Research State — NIFTY Groww Paper Research

**Authoritative handoff:** this file supersedes stale task sequencing in older `PROJECT_STATE.md` / `NEXT_TASK.md` notes. Updated 2026-10-07. Research only; no live trading. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`.

## Current objective

Describe and validate canonical NIFTY 5-minute Level-to-Level and Ekalayava behavior across historical periods using Groww data. The July–August 2026 audit/backtest is complete as an explicitly incomplete sample because 65 required daily contract slots are absent from Groww's returned expiry catalogs. Preserve baseline strategy definitions. Ekalayava is not ready for complete P&L analysis until its missing exit lifecycle is specified.

## Canonical strategies

- **Level-to-Level:** NIFTY CE/PE ITM2/ITM3; completed 5-minute bars, Asia/Kolkata; opening range from first bar; premium breaks below Opening Low then first completed green bar enters at close; SL = Opening Low minus configured 4 premium points (baseline); target = Opening High; entry window 09:15–11:00.
- **Ekalayava:** NIFTY CE/PE ITM2/ITM3, same bars/timezone; premium first breaks Opening Low; causal swing high is current high above previous two highs (left=2/right=0); a later completed bar with both high and close above that swing reference, while remaining below Opening High, enters at close; Opening High is target. Canonical spec defines **no SL, opposite-signal exit, forced EOD exit, expiry handling, or end-of-data valuation**. Do not invent one. Existing simulator observes same-day bars after entry (up to 78), stops at the first Opening-High touch, and otherwise labels OPEN; this is not a complete lifecycle/P&L engine.

## July–August 2026 contract audit and baseline (incomplete)

- Requested period kept inclusive: **2026-07-01 → 2026-08-31**, 44 NIFTY trading dates (23 July, 21 August). Underlying regular-session coverage: **3,300/3,300** five-minute bars (09:15–15:25 IST).
- Groww expiry catalogs returned 07/14/21/28 July, 04/11/18/25 August, and 01 September; contract counts were **10, 166, 22, 205, 120, 103, 89, 181, 80**. All returned symbols matched the catalog expiry. Observed strike spacing was 50 NIFTY points.
- Audit found the prior selector inferred expiry/ranks from local option files and could shift ranks when files were missing or select different expiries by side. Fixed it to require Groww expiry catalogs, recalculate daily from the NIFTY 09:15 open, select exact side/rank strikes, and mark absent symbols unavailable. Canonical rules were not changed. The canonical spec does not define strike spacing; 50-point spacing is documented as an observed catalog convention. No missing contract symbol was synthesized.
- Expected options: **176 contract-days**, 75 regular candles each (13,200 expected). Exact Groww catalog slots available: **111/176 (63.1%)**; all 111 have complete 75/75 session bars and 09:15 openings. **0 partial contract-days; 65 missing/unavailable** (4,875 required bars). By slot: CE ITM2 29/44, CE ITM3 27/44, PE ITM2 26/44, PE ITM3 29/44. Usable dates: **17 full, 17 partial, 10 unusable**. July: 11 full/2 partial/10 unusable; August: 6 full/15 partial/0 unusable.
- Fifteen locally missing but catalog-identified contract-days were fetched read-only from Groww (**1,168 raw rows**, 1,125 regular bars). No absent catalog slot was queried with a constructed symbol. The 111 selected contract-days' timestamps align with the underlying grid (8,325/8,325); volume/OI are present, though the strategy uses timestamp/OHLC only.
- Underlying is one 5-minute CSV; options are individual symbol CSVs. Exact timestamp duplicates were deduplicated with no conflicting OHLC rows; no interpolation. Groww returned symbols but no numeric tokens. Source files included out-of-session rows, so the research runner now clips input to 09:15–15:25 IST. Strategy definitions and `app/paper.py` were unchanged.
- **L2L July:** 34 setups; 25 resolved (3 target/22 SL), 9 skipped; gross resolved points **−64.70**, mean **−2.59**, median **−6.70**, target proportion among resolved **12.0%**, mean hold **30.0 min**, mean resolved MFE/MAE **+16.01/−11.64**, max drawdown **65.30**.
- **L2L August:** 38 setups; 16 resolved (9 target/7 SL), 22 skipped; gross points **+146.10**, mean **+9.13**, median **+5.55**, target proportion **56.3%**, mean hold **26.25 min**, mean resolved MFE/MAE **+15.86/−7.08**, max drawdown **25.70**.
- **L2L combined:** 72 setups; 41 resolved (12 target/29 SL), 31 skipped; gross resolved points **+81.40**, mean **+1.99**, median **−4.00**, target proportion **29.3%**, mean hold **28.54 min**, mean resolved MFE/MAE **+15.95/−9.86**, max drawdown **74.50**. August 22–28 contributed +111.85 points; 25-Aug alone +90.90. Gross contract premium points are not cost-adjusted returns.
- **Ekalayava July:** 21 entries (6 CE/15 PE; 9 ITM2/12 ITM3), 11 target touches/10 OPEN; descriptive touch fraction **52.4%**; mean/median MFE **29.15/19.70**, mean/median MAE **−29.73/−18.15**, target distance **45.76/44.05**, mean target-touch time **119.5 min** (touches only).
- **Ekalayava August:** 26 entries (16 CE/10 PE; 14 ITM2/12 ITM3), 11 touches/15 OPEN; descriptive touch fraction **42.3%**; mean/median MFE **23.92/17.45**, mean/median MAE **−20.44/−14.10**, target distance **46.90/33.78**, mean target-touch time **70.9 min**.
- **Ekalayava combined:** 47 entries (22 CE/25 PE; 23 ITM2/24 ITM3), 22 target touches/25 OPEN; mean/median MFE **26.25/17.65**, mean/median MAE **−24.59/−15.60**, target distance **46.39/35.95**, mean target-touch time **95.2 min**. No SL/lifecycle was added; target points are not realized P&L.
- Results are incomplete; missing contracts may suppress setups/outcomes. Tests: **61 passed**. Safety remained `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`. Full slot-level traces and breakdowns: `reports/july_august_2026_full_analysis.md`. Raw research datasets remain ignored/untracked.

## Fresh four-session observation — 2026-09-28 to 2026-10-01 (incomplete)

- Groww read-only authentication succeeded; direct underlying retries returned: Sep 28 75/75 regular bars; Sep 29 58/75 with 17 missing from 14:05–15:25; Sep 30 0/75; Oct 1 0/75. The NSE 2026 F&O holiday circular lists Oct 2 as a holiday, not Sep 30 or Oct 1; missing bars are treated as data unavailability.
- The canonical selector could choose contracts only for Sep 28–29 because Sep 30/Oct 1 lack a unique 09:15 underlying open. Eight Sep 28–29 CE/PE ITM2/ITM3 contract-days were queried; 0 complete, all 8 partial. Sep 28: 228/300 option bars; Sep 29: 194/300. 0/4 dates fully usable; Sep 28–29 partial, Sep 30–Oct 1 unusable. No candles were filled. Retry added no bars to selected existing contracts.
- L2L: 3 observed candidate setups on Sep 29 (CE ITM2, CE ITM3, PE ITM3), all `SKIPPED_SL_ALREADY_BREACHED`; 0 targets, 0 SL exits, 0 resolved trades, 0 resolved points. Sep 28 produced no observed setup on its only eligible contract (PE ITM3); other contracts lacked 09:15. Sep 30/Oct 1 were not runnable.
- Ekalayava: 0 entries on eligible Sep 28 PE ITM3; three observed entries on Sep 29. CE ITM2 entered 10:40 at 276.70, touched 403.55 opening high at 12:00, observed MFE/MAE +140.50/-21.20. CE ITM3 entered 10:40 at 324.10, touched 436.15 at 11:30, observed MFE/MAE +140.20/-19.95. PE ITM3 entered 09:35 at 1353.70, no target touch in observed bars, MFE/MAE +13.55/-169.20. Thus 2/3 observed entries touched target, both CE; the PE entry remained unresolved. Option observations end by 13:55 and are gapped; EOD status and full-path extrema are unknown. No Ekalayava exit rule was added; target touches are not realized P&L.
- These four dates do not support a complete L2L profitability/concentration conclusion or a reliable Ekalayava target rate. Context only: Period A/B Ekalayava target-touch rates were 48.2%/43.9%; current 2/3 is too small and censored to compare. Details: `reports/2026-09-28_to_2026-10-01_fresh_market_analysis.md`.
- Next date-specific research step: determine whether Groww can return Sep 29 afternoon and Sep 30/Oct 1 historical candles; if unavailable, preserve the four dates as incomplete. Do not rerun older periods. Ekalayava lifecycle approval remains unresolved before P&L or paper trading.

## Fresh session results — 2026-09-28 (option coverage incomplete)

- Groww read-only authentication succeeded. Underlying: 75/75 regular-session bars (09:15–15:25), no missing intervals. Sep 28 NIFTY opened at 23079.75, closed 22780.25 at 15:25 (-299.50); session range 317.50 points.
- Nearest expiry was Sep 29. Selected canonical contracts: CE ITM2 22350 (61/75, 14 missing, no 09:15 bar); PE ITM2 23950 (52/75, 23 missing, no open); CE ITM3 22300 (72/75, 3 missing, no open); PE ITM3 24050 (43/75, 32 missing, open present). 0/4 option contract-days complete.
- Existing strategy implementations found 0 observed L2L setups and 0 Ekalayava entries on the only contract with a valid opening bar (PE ITM3). Other three were not run because their canonical opening candle is missing. Counts are not evidence of no setup in the incomplete full market record. L2L observed targets/SL/points 0/0/0; Eka target/MFE/MAE N/A with no entries, exit lifecycle unchanged.
- No comparative behavioral conclusion is supported for this day. The underlying tape opened at its session high and declined, but option gaps prevent a four-contract strategy assessment. No missing candles were filled; no orders were placed. Details: `reports/2026-09-28_fresh_market_analysis.md`.
- Next research question: can the three missing option opening candles and the 72 missing session intervals be recovered from the same authorized Groww historical source without substituting/filling data? If not, retain this day as incomplete and do not generalize the strategy outcomes.

## Completed periods and numerical results

### Period A — 2026-04-25 through 2026-09-25

- Saved baselines contain 106 sessions (2026-04-27–2026-09-25), 8,895 underlying bars; all 106 underlying sessions complete.
- Option contract-days: 381 complete, 25 partial, 18 missing of 424; 2,328 missing 5-minute intervals; 29,472 option bars; day status: 91 fully usable, 5 partial, 10 unusable.
- Level-to-Level: 247 setups; 156 valid, 91 skipped; 49 TARGET, 107 SL, no OPEN; resolved gross premium points 502.40; mean 3.22, median -4.00; mean MFE 11.48, MAE -7.53; maximum drawdown 208.25 in cross-period report's resolved timestamp/symbol ordering.
- Ekalayava: 170 entries; 82 target touches, 88 OPEN; no SL. Mean MFE 36.76, mean MAE -43.95; mean target distance 43.59 (median 34.97); target-hit path duration mean 106.04 min. 3,574.6 target points are not realized P&L.

### Period B — 2026-01-01 through 2026-04-24 (non-overlapping)

- 76 saved underlying sessions, all present; options: 276 complete, 22 partial, 6 missing of 304; 1,278 missing intervals; session-slot availability 94.39%; days: 58 fully usable, 14 partial, 4 unusable.
- Level-to-Level: 181 setups; 92 valid, 89 skipped; 23 TARGET, 68 SL, 1 ambiguous; resolved gross premium points -333.70; mean -3.67, median -8.35; mean MFE 9.16, MAE -8.86; maximum drawdown 432.75 in comparison report ordering.
- Ekalayava: 132 entries; 58 target touches, 74 OPEN; no SL. Mean MFE 42.84, mean MAE -47.91; mean target distance 52.11 (median 38.72); target-hit path duration mean 73.88 min. Target points are not realized P&L.

## Completed research phases — do not repeat

1. Groww read-only auth/config was confirmed in the Windows local checkout; no credentials belong in Git.
2. Historical data collection and canonical baseline-v1 for Period A, including coverage report.
3. Period A detailed baseline diagnostics.
4. Ekalayava specification/implementation audit: implementation’s target-only OPEN behavior is consistent with undefined exits; it is incomplete for full P&L. No strategy changes.
5. Earlier non-overlapping Period B collection, baseline, coverage, and cross-period comparison.
6. Current post-entry behavior analysis across existing events: 302 total Ekalayava entries; no new downloads or backtest rerun. Saved MFE/MAE matched candle-derived values for every event. Behavior results below.

## Ekalayava post-entry behavior (descriptive only)

- Period A target touches 82/170 (48.2%); B 58/132 (43.9%). Target-only observed time mean/median: A 106/85 min; B 73.9/45 min.
- Mean/median MFE: A 36.76/23.73; B 42.84/29.35 premium points. Mean/median MAE: A -43.95/-36.08; B -47.91/-36.80.
- Observed below-entry low occurred in A 170/170; B 129/132. Mean first-adverse time: 5.9 min A, 5.3 min B. In the first post-entry 5-minute bar, both sides of entry were spanned in A 155/170 and B 123/132; intrabar ordering is unknowable from OHLC.
- Pre-entry observed sequence trough revisited: A 100/170 (58.8%), B 76/132 (57.6%). Breakdown low revisited: 134/170 (78.8%), 103/132 (78.0%). Breakout candle low revisited: 127/170 (74.7%), 96/132 (72.7%). These references are behavioral measurements, not canonical stop rules.
- Endpoint path gaps affected 3 events: A target event 2026-09-16 had 4 missing bars; B open 2026-03-19 had 11; B target 2026-04-02 had 2. Two breakdown-to-entry paths were incomplete (A 2026-09-10: 1 gap; B 2026-04-02: 31 gaps). Other missing contract-days may suppress undetected events.
- Observed differences: B had higher mean MFE and more negative mean MAE; lower target-touch fraction but shorter target-hit times. CE/PE target fractions differed by period. These are event-sample descriptions, not causal findings or performance ranking.

## Ekalayava lifecycle issue and unresolved work

The user/spec owner must decide and version the exit/valuation lifecycle before any complete Ekalayava P&L comparison or paper trading: whether any SL exists; target candle/exit convention; opposite-signal handling; end-of-day treatment; expiry; and end-of-data valuation/censoring. Also clarify if “reversal low” requires any formal definition beyond the existing causal swing/break sequence. Do not infer missing rules. Until then, report target touches and excursions only, and label OPEN outcomes unresolved.

## Evidence/report map

- `reports/july_august_2026_full_analysis.md` — full July–August 2026 catalog/expiry audit, 176 daily slot traces, coverage, corrected canonical baselines, and July-vs-August breakdowns. Explicitly incomplete: 65 exact contract-days unavailable from the returned Groww catalogs.
- `reports/baseline_diagnostic_2026-04-25_to_2026-09-25.md` — Period A diagnostic metrics and missing-data impact.
- `reports/ekalayava_spec_implementation_audit.md` — canonical rule audit, current implementation, undefined lifecycle, 88 A opens, and why target points are not P&L.
- `reports/cross_period_baseline_comparison.md` — A/B coverage and baseline strategy distributions.
- `reports/ekalayava_trade_behavior_cross_period.md` — event-level ledger and detailed behavioral comparison for all 302 Ekalayava entries.
- `reports/2026-09-28_to_2026-10-01_fresh_market_analysis.md` — four-date fresh observation; incomplete coverage, observed candidate outcomes, and Ekalayava post-entry excursions.
- Preserved event/data sources: `data/reports/baseline_v1_requested_period.json`, `data/reports/baseline_v1_period_b_2026-01-01_to_2026-04-24.json`, and the corresponding `data/derived/` period folders. Raw research datasets follow existing ignore policy and are not intended for Git.

## Exact next research step

For the July–August audit, first determine whether Groww can supply an authoritative historical instrument catalog/listing record for the 65 absent exact contract slots; only then fetch those exact symbols and rerun the affected period. If Groww cannot identify them, retain this baseline as incomplete and do not substitute. Separately, recover the missing Sep29 afternoon and Sep30/Oct1 data before treating the four-session observation as complete. Obtain a versioned Ekalayava exit-lifecycle decision before any Ekalayava P&L comparison or paper trading. Do not rerun completed periods or change canonical rules.

## Experiments already complete and not to repeat

- Period A and Period B data downloads, coverage calculations, canonical baseline backtests, Period A diagnostic, Ekalayava specification audit, and baseline cross-period comparison.
- Current Ekalayava post-entry event/candle analysis. No additional market data or canonical backtest is needed to reproduce this report.
- July–August 2026 Groww contract/expiry audit, 15 exact-symbol missing-day downloads, regular-session coverage audit, and canonical L2L/Ekalayava baseline run. This run is complete but not a complete-period result because 65 contract-days were absent from Groww's current catalogs.
- Older bounded weekly/AI experiments listed in `EXPERIMENT_LOG.md` are not substitutes for the two-period canonical baselines and should not be rerun as part of this objective.



