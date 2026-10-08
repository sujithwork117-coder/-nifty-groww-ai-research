# Research State — NIFTY Groww Paper Research

**Updated:** 2026-10-08. This is the single handoff summary. Research and paper observation only; no live trading. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`. The latest authoritative cumulative run is the corrected Jan–Sep 2026 validation below. Earlier reports are preserved but some used the old selector and must not be merged with the corrected results.

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

### L2L target-hit timing study — 2026-10-08

- Reused the corrected stored Jan–Sep baseline and existing option candles; no full rerun or new download. The 361 L2L setups comprise 203 resolved (58 TARGET / 145 SL), 157 skipped, and 1 ambiguous. Target hits are 58/203 = **28.6%** of resolved trades.
- Target timing is measured from the completed entry-candle close. Of 58 targets, 14 (24.1%) first appear in the first post-entry candle (0–5 minute window), 25 (43.1%) within two bars (≤10m), 34 (58.6%) within three bars (≤15m), 39 (67.2%) within six bars (≤30m), 49 (84.5%) within twelve bars (≤60m), 57 (98.3%) within eighteen bars (≤90m), and 1 in the 110–115m window. Median actual time is bounded by **10–15m**; mean by **23.6–28.6m**. Fastest observed window is 0–5m.
- Target hits by side/rank: CE 26/104 resolved, PE 32/99; ITM2 27/102, ITM3 31/101. Monthly target counts Jan–Sep: **11, 6, 2, 4, 14, 5, 3, 9, 4**. Entry-close hour: 40 targets from 09:xx and 18 from 10:xx; none from 11:00.
- 5-minute OHLC cannot provide the exact intrabar target instant or target-vs-low ordering; report candle windows, not exact touch times. All 58 first observed target bars matched the stored exit timestamp, with no missing expected candles between entry and that bar. Two entry candles had high ≥ target, but entry is at candle close so these cannot establish a post-entry touch. One target outcome had entry 129.10 already above target 126.50, a baseline `high >= target` interpretation artifact; do not read that as an upward target move. Full evidence and 203 resolved-setup ledger: `reports/l2l_target_timing_research.md`.
- Observed timing shows material short-duration behavior (14 target hits in the first post-entry bar), alongside a long tail; no time filter/exit optimization was performed and no canonical rule changed.

### Ekalayava (observation only)

- **253 entries; 109 opening-high touches (43.1%); 144 no-touch observations. All 253 lifecycle outcomes remain unresolved.** No SL count, win rate, realized P&L, or target-point total is defined.
- Full same-day post-entry observation through 15:25: mean/median MFE +57.35/+31.05; mean/median MAE −53.27/−45.60; mean/median time to MFE 113.99/85 min; time to MAE 179.05/195 min. Among target touches, time mean/median 93.72/65 min; target distance mean/median 61.10/54.80.
- Descriptive, causal pre-entry candidate low = lowest premium low from first opening-low break through completed entry candle; later revisit: 187/253 (73.9%). Breakout-candle low revisited 223/253 (88.1%); opening low revisited 249/253 (98.4%). These are not stop rules.
- Train Jan–Jun: 191 entries, 83 touches; validation Jul–Aug: 47, 22 touches; September through Sep 29: 15, 4 touches. Target touches are not wins.

## Paper engine + selected-date historical replay — 2026-10-08

- Replaced the prior live listener’s “latest bucket is complete” behavior with `FiveMinuteCandleBuilder`, which emits only after the 5-minute close boundary, rejects duplicate/late ticks, orders in-bucket ticks, reports gaps without fabricating candles, and can snapshot/restore.
- Live contract selection now uses the historical catalog-first method: completed NIFTY 09:15 open → earliest Groww expiry on/after that date → exact CE/PE ITM2/ITM3 strikes from that expiry chain. Expiry-label mismatch and missing exact ranks fail closed. Rollover evidence: Jan 6 selected expiry Jan 6 (CE 26100/26050; PE 26250/26300); Jan 7 selected Jan 13 (CE 26050/26000; PE 26200/26250). No strike/expiry substitution.
- `PaperContractEngine` is stateful per contract-day. It implements the canonical red-break → first later completed green L2L entry at close with configured 4-point SL buffer and Opening High target; daily duplicate protection; SL/target/ambiguous handling; no forced EOD exit. Gaps invalidate new entries and leave open trades unresolved. Restart requires the same exact symbol and strategy parameters.
- Ekalayava engine follows current causal left=2/right=0 swing-high entry implementation. It records the pre-entry low proxy/candidate, candidate SL location, breakout, MFE/MAE, target touch/time, and structural/breakout-low revisits. Candidate SL is explicitly unapproved and observational. It never writes a realized result; target touches stay unresolved.
- New append-only, record-ID-deduplicated JSONL journal includes contract identity, NIFTY price, strategy levels, entry cause, statuses, MFE/MAE/time-to-extremum, target touch, structural observations, and data-quality status.
- Candle-by-candle replay used existing complete local data, not new downloads or a full-period rerun. Eight signal examples (5 L2L, 3 Ekalayava) plus one no-setup contract-day were replayed; each selected option day had 75/75 session bars. All selected entry times/prices matched stored baselines. L2L target/SL/skip/ambiguous outcomes, exit times, SL/target levels, and MFE/MAE matched. Ekalayava entry, target-touch time, MFE/MAE, and candidate structural low matched. Jan 1 CE ITM2 Ekalayava: 09:50 entry, no touch, MFE +1.65 / MAE −43.80, candidate low 127.40; Jan 2 PE ITM2: 14:35, no touch, +2.40 / −14.30, candidate 39.70; Jan 5 CE ITM3: 09:50, target touched 10:20, +62.85 / −78.55, candidate 105.90. All remained unresolved; no Ekalayava P&L.
- Prefix replay had no L2L signal before the completed first-green entry candle; adding that candle generated the same timestamp as full-day replay. Missing bars, late/out-of-order ticks, duplicate candles, state restore, and parameter mismatch are tested.
- Full test suite after changes: **76 passed**. Canonical strategy functions/definitions were not changed. No live polling was started; no order APIs were called.
- Readiness remains **L2L NOT READY; Ekalayava OBSERVATION-ONLY**. Components pass replay/unit checks, but a live Groww observer coordinator is not wired end-to-end to capture the underlying open, subscribe/build four exact option streams, persist all engines, or recover through real network reconnects. NSE holiday/special-session calendar integration is also missing. Ekalayava structural SL anchor/buffer/trigger and lifecycle remain undefined.

## Earlier phases and selector caveat

- Period A (Apr 27–Sep 25) and Period B (Jan 1–Apr 24) reports remain preserved. Their previously reported results used the earlier selector and are **superseded for cumulative comparisons** by the new daily catalog-first rerun. Do not add Period A/B totals to the final Jan–Sep totals.
- July–August corrected run remains useful and matches the full-run slice: 44 sessions; underlying 100%; 111/176 option slots complete, 65 catalog-absent; L2L 72 setups, 41 resolved (12 target/29 SL), 31 skipped, +81.40; Ekalayava 47 entries, 22 target touches, 25 no touch.
- Earlier Sep 28–Oct 1 fresh reports are preserved, but their Sep 28–29 option selection does not resolve to the exact required ITM2/ITM3 symbols in the returned catalog. Their trade observations are excluded from corrected final OOS. Sep 30 underlying remains unavailable.
- Older Period A/B Ekalayava behavior comparison (302 events) remains archival evidence from the earlier selector; use corrected Jan–Sep events for current cumulative conclusions.

## Paper readiness and safety

- `app.config` hard-fails if execution is enabled or paper-only is false; current values are false/true. No order API calls exist in application code; no orders were placed.
- `app.candle_builder` and `app.paper_engine` now provide close-aware candles, exact daily selection, stateful L2L and observational Ekalayava, duplicate/restart protection, and append-only journal events. Representative selected-day replays match stored historical baseline signals/outcomes.
- End-to-end live wiring remains incomplete: no Groww read-only observer coordinator connects NIFTY open → daily selector → four option streams → persisted engines/journal. Reconnect/error recovery has component tests but no live-feed integration test. NSE holiday/special-session calendar is not wired.
- L2L remains **NOT READY** for controlled live paper observation until observer integration and calendar/recovery checks pass. Ekalayava remains **OBSERVATION-ONLY**; no executable structural SL or full exit lifecycle exists. Target touch is not an exit or win.
- Market code is deterministic; LLM use is limited to research-agent tasks, not every candle.
- `.env`, `secrets.txt`, tokens, and keys are ignored/untracked and never included in reports.

Checklist and replay trace: `reports/paper_engine_replay_validation.md`.

## Reports

- `reports/jan_sep_2026_final_validation.md` — selector audit, rollover traces, coverage, splits, conclusions.
- `reports/l2l_final_validation.md` — L2L distributions, sensitivity, concentration, readiness.
- `reports/ekalayava_final_validation.md` — MFE/MAE, structural-low revisits, touch distributions, unresolved lifecycle.
- `reports/paper_trading_readiness.md` — deterministic live/paper component audit and readiness decision.
- Preserved prior detailed reports: `reports/july_august_2026_full_analysis.md`, `reports/baseline_diagnostic_2026-04-25_to_2026-09-25.md`, `reports/ekalayava_spec_implementation_audit.md`, `reports/cross_period_baseline_comparison.md`, `reports/ekalayava_trade_behavior_cross_period.md`, and the Sep 28 / Sep 28–Oct 1 reports.

## Exact next research step

1. Implement a read-only Groww observer coordinator and exchange calendar; verify completed NIFTY 09:15 capture, exact daily expiry/strikes, four option streams, durable per-contract state/journal, and real reconnect/error recovery through replay or a controlled dry run. Do not start continuous execution.
2. Obtain a versioned Ekalayava decision for exact structural anchor, numeric buffer/trigger, target behavior, same-candle ambiguity, opposite signal, EOD, expiry, and end-of-data before P&L or paper-trade lifecycle work.
3. Separately request authoritative Groww listings for the 174 absent exact historical slots and retry Sep 30 underlying; preserve any unavailable data without substitution.

## Completed experiments — do not repeat

- Period A, Period B, diagnostic, Ekalayava spec audit, cross-period baseline, and prior Ekalayava behavior study.
- July–August 2026 contract audit and corrected baseline.
- Corrected full Jan–Sep 2026 catalog-first selection, exact-symbol recovery, coverage, L2L/Ekalayava rerun, 3/4-point L2L sensitivity, and readiness audit. Repeat only after exact missing data is recovered or a versioned strategy-spec change requires it.
- Stateful paper engine, completed-candle builder, representative candle-by-candle historical replay, and Jan 6→Jan 7 expiry rollover validation. Do not repeat these selected replays unless engine logic changes; expand only to cover integration/recovery blockers.
