# Research State — NIFTY Groww Paper Research

**Updated:** 2026-10-07. This is the single handoff summary. Research only; no live trading. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`. The latest authoritative cumulative run is the corrected Jan–Sep 2026 validation below. Earlier reports are preserved but some used the old selector and must not be merged with the corrected results.

## Project objective and current status

Validate canonical NIFTY 5-minute Level-to-Level and Ekalayava behavior using exact daily Groww contracts, maintain data-quality evidence, and only then assess controlled paper observation. No broker orders are allowed. Current readiness: **L2L NOT READY; Ekalayava OBSERVATION-ONLY**.

## Canonical strategy definitions

- **Level-to-Level (L2L):** NIFTY CE/PE ITM2/ITM3; Asia/Kolkata completed 5-minute bars; first candle defines opening high/low; a completed red candle breaks below Opening Low; enter at close of the first subsequent completed green bar, between 09:15–11:00; SL = Opening Low minus configured buffer (canonical/default 4 premium points); target = Opening High.
- **Ekalayava:** opening-low breakdown → recovery and causal swing high (current code uses left=2/right=0) → later completed candle breaks/closes above swing high while still below Opening High → entry at close. Opening High is target/reference. No canonical executable SL, opposite-signal exit, EOD/expiry exit, or end-of-data valuation exists.
- **Ekalayava structural SL:** User’s stated concept is below relevant reversal/price-action structure. No exact anchor candle/low, buffer, or trigger convention is defined in repository/class evidence. Current code records a descriptive pre-entry low candidate, not a stop. Do not infer an executable SL. Ekalayava is not valid for P&L comparison until lifecycle decisions are versioned.

## Correct contract-selection architecture

For every trading date independently: read unique NIFTY 09:15 open → choose earliest returned Groww expiry on/after the date → calculate exact CE/PE ITM2/ITM3 strikes on the catalog’s observed ladder → resolve exact symbols → load only those contract candles for that date. Do not shift missing ranks/expiries or use local file availability to define the universe. All strategy inputs are clipped to 09:15–15:25.

Groww returned 39 expiry catalogs for Jan–Sep 2026 and the Oct 6 next-expiry chain. Every Jan–Sep chain had 50-point minimum observed strike spacing and matching symbol expiry labels. The 50-point spacing is observed catalog convention; the canonical strategy document does not specify a strike-step formula. 174 exact expected symbols were absent from returned catalogs.

## Latest authoritative full-period run: 2026-01-01 → 2026-09-30

**Period retained in full. Data available only through Sep 29; Sep 30 is an NSE trading date with no Groww underlying candles.** The calendar includes the Feb 1 special Sunday session and excludes exchange holidays. 185 expected sessions; 184 have underlying source data.

### Coverage

- Underlying regular-session bars: **13,783/13,875 (99.3%)**; Sep 29 lacks 17 late-session bars (14:05–15:25); Sep 30 lacks all 75 bars.
- Options: **740 expected contract-days**; 561 complete, 1 partial (Feb 3 PE ITM3, 74/75), 178 missing/unselectable; **42,149/55,500 bars (75.9%)**, 13,351 intervals missing.
- 112 fully usable, 55 partially usable, 18 unusable days.
- 174 slots lacked an exact required symbol in the returned catalogs; 4 Sep 30 slots could not be selected without the underlying open.
- Authenticated, read-only Groww retries added 2,174 regular bars across 29 exact-symbol contract-days (25 symbols). 28 were 75/75; one remained 74/75. No fabricated data or substitute contracts.

### L2L (canonical 4-point buffer)

- Full observed sample: **361 setups; 203 resolved (58 target, 145 SL), 157 skipped, 1 ambiguous; +234.85 gross premium points**. Mean/median resolved trade +1.16/−4.45; average winner +29.25; average loser −9.81; resolved mean MFE/MAE +18.14/−12.81; mean holding 21.58 min; maximum drawdown 251.95 gross points in chronological event sequence; longest win/loss streak 4/23.
- Train Jan–Jun: 269 setups; 148 resolved (42 target/106 SL), 120 skipped, 1 ambiguous; +132.25 points.
- Validation Jul–Aug: 72 setups; 41 resolved (12/29), 31 skipped; +81.40 points.
- Final OOS Sep: 20 setups; 14 resolved (4/10), 6 skipped; +21.20 points. **Incomplete:** through Sep 29 only, 33/84 option slots complete.
- Jan–Mar: 130 setups, 63 resolved (19/44), 66 skipped, 1 ambiguous; −3.40. Apr–Jun: 139 setups, 85 resolved (23/62), 54 skipped; +135.65. Jul–Sep: 92 setups, 55 resolved (16/39), 37 skipped; +102.60.
- Monthly points Jan→Sep: **+47.35, +41.60, −92.35, −65.65, +298.00, −96.70, −64.70, +146.10, +21.20**. May alone exceeds the total; five daily contributions sum +545.40. These are gross points, not net returns/profitability.
- Descriptive 3-point-buffer sensitivity on the same full sample: 51 target/137 SL/172 skipped/1 ambiguous; +78.20 points. No rule changed and no parameter was selected.

### Ekalayava (observation only)

- **253 entries; 109 opening-high touches (43.1%); 144 no-touch observations. All 253 lifecycle outcomes remain unresolved.** No SL count, win rate, realized P&L, or target-point total is defined.
- Full same-day post-entry observation through 15:25: mean/median MFE +57.35/+31.05; mean/median MAE −53.27/−45.60; mean/median time to MFE 113.99/85 min; time to MAE 179.05/195 min. Among target touches, time mean/median 93.72/65 min; target distance mean/median 61.10/54.80.
- Descriptive, causal pre-entry candidate low = lowest premium low from first opening-low break through completed entry candle; later revisit: 187/253 (73.9%). Breakout-candle low revisited 223/253 (88.1%); opening low revisited 249/253 (98.4%). These are not stop rules.
- Train Jan–Jun: 191 entries, 83 touches; validation Jul–Aug: 47, 22 touches; September through Sep 29: 15, 4 touches. Target touches are not wins.

## Earlier phases and selector caveat

- Period A (Apr 27–Sep 25) and Period B (Jan 1–Apr 24) reports remain preserved. Their previously reported results used the earlier selector and are **superseded for cumulative comparisons** by the new daily catalog-first rerun. Do not add Period A/B totals to the final Jan–Sep totals.
- July–August corrected run remains useful and matches the full-run slice: 44 sessions; underlying 100%; 111/176 option slots complete, 65 catalog-absent; L2L 72 setups, 41 resolved (12 target/29 SL), 31 skipped, +81.40; Ekalayava 47 entries, 22 target touches, 25 no touch.
- Earlier Sep 28–Oct 1 fresh reports are preserved, but their Sep 28–29 option selection does not resolve to the exact required ITM2/ITM3 symbols in the returned catalog. Their trade observations are excluded from corrected final OOS. Sep 30 underlying remains unavailable.
- Older Period A/B Ekalayava behavior comparison (302 events) remains archival evidence from the earlier selector; use corrected Jan–Sep events for current cumulative conclusions.

## Paper readiness and safety

- `app.config` hard-fails if execution is enabled or paper-only is false; current values are false/true. No order API calls exist in application code; no orders were placed.
- `app.live_listener` is not ready: it can return the current incomplete candle and its stateless signal condition is not the canonical prior-red/first-subsequent-green sequence. It has no daily catalog selector, duplicate protection, or full journal schema. No Ekalayava listener path exists.
- Market code is deterministic; LLM use is limited to research-agent tasks, not every candle.
- `.env`, `secrets.txt`, tokens, and keys are ignored/untracked and never included in reports.

## Reports

- `reports/jan_sep_2026_final_validation.md` — selector audit, rollover traces, coverage, splits, conclusions.
- `reports/l2l_final_validation.md` — L2L distributions, sensitivity, concentration, readiness.
- `reports/ekalayava_final_validation.md` — MFE/MAE, structural-low revisits, touch distributions, unresolved lifecycle.
- `reports/paper_trading_readiness.md` — deterministic live/paper component audit and readiness decision.
- Preserved prior detailed reports: `reports/july_august_2026_full_analysis.md`, `reports/baseline_diagnostic_2026-04-25_to_2026-09-25.md`, `reports/ekalayava_spec_implementation_audit.md`, `reports/cross_period_baseline_comparison.md`, `reports/ekalayava_trade_behavior_cross_period.md`, and the Sep 28 / Sep 28–Oct 1 reports.

## Exact next research step

1. Ask Groww for an authoritative historical contract listing for the 174 absent exact slots and retry Sep 30 underlying from the same provider; keep unavailable data missing and never substitute.
2. Obtain a versioned Ekalayava rule for structural anchor, numeric buffer/trigger, target behavior, same-candle ambiguity, opposite signal, EOD, expiry, and end-of-data.
3. Repair/test live candle-close detection, stateful canonical L2L, daily exact selector/rollover, duplicate prevention, and complete journal fields before supervised paper observation. Keep broker execution absent/disabled.

## Completed experiments — do not repeat

- Period A, Period B, diagnostic, Ekalayava spec audit, cross-period baseline, and prior Ekalayava behavior study.
- July–August 2026 contract audit and corrected baseline.
- Corrected full Jan–Sep 2026 catalog-first selection, exact-symbol recovery, coverage, L2L/Ekalayava rerun, 3/4-point L2L sensitivity, and readiness audit. Repeat only after exact missing data is recovered or a versioned strategy-spec change requires it.
