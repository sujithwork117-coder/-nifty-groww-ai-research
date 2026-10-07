# Research State — NIFTY Groww Paper Research

**Authoritative handoff:** this file supersedes stale task sequencing in older `PROJECT_STATE.md` / `NEXT_TASK.md` notes. Updated 2026-10-07. Research only; no live trading. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`.

## Current objective

Describe and validate canonical NIFTY 5-minute Level-to-Level and Ekalayava behavior across historical periods using existing Groww data. Preserve baseline strategy definitions. Ekalayava is not ready for complete P&L analysis until its missing exit lifecycle is specified.

## Canonical strategies

- **Level-to-Level:** NIFTY CE/PE ITM2/ITM3; completed 5-minute bars, Asia/Kolkata; opening range from first bar; premium breaks below Opening Low then first completed green bar enters at close; SL = Opening Low minus configured 4 premium points (baseline); target = Opening High; entry window 09:15–11:00.
- **Ekalayava:** NIFTY CE/PE ITM2/ITM3, same bars/timezone; premium first breaks Opening Low; causal swing high is current high above previous two highs (left=2/right=0); a later completed bar with both high and close above that swing reference, while remaining below Opening High, enters at close; Opening High is target. Canonical spec defines **no SL, opposite-signal exit, forced EOD exit, expiry handling, or end-of-data valuation**. Do not invent one. Existing simulator observes same-day bars after entry (up to 78), stops at the first Opening-High touch, and otherwise labels OPEN; this is not a complete lifecycle/P&L engine.

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

- `reports/baseline_diagnostic_2026-04-25_to_2026-09-25.md` — Period A diagnostic metrics and missing-data impact.
- `reports/ekalayava_spec_implementation_audit.md` — canonical rule audit, current implementation, undefined lifecycle, 88 A opens, and why target points are not P&L.
- `reports/cross_period_baseline_comparison.md` — A/B coverage and baseline strategy distributions.
- `reports/ekalayava_trade_behavior_cross_period.md` — event-level ledger and detailed behavioral comparison for all 302 Ekalayava entries.
- Preserved event/data sources: `data/reports/baseline_v1_requested_period.json`, `data/reports/baseline_v1_period_b_2026-01-01_to_2026-04-24.json`, and the corresponding `data/derived/` period folders. Raw research datasets follow existing ignore policy and are not intended for Git.

## Exact next research step

Obtain an explicit, versioned Ekalayava lifecycle decision from the strategy/spec owner. Then translate only that approved decision into tests and an implementation change, review safety, and rerun both existing periods. If no exit is authorized, continue censored/descriptive event analysis only; do not claim complete P&L.

## Experiments already complete and not to repeat

- Period A and Period B data downloads, coverage calculations, canonical baseline backtests, Period A diagnostic, Ekalayava specification audit, and baseline cross-period comparison.
- Current Ekalayava post-entry event/candle analysis. No additional market data or canonical backtest is needed to reproduce this report.
- Older bounded weekly/AI experiments listed in `EXPERIMENT_LOG.md` are not substitutes for the two-period canonical baselines and should not be rerun as part of this objective.



