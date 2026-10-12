# Research State — NIFTY Groww Paper Research

## Multi-year L2L + Ekalayava exit research — 2026-10-12

- Scope requested: 2025-07-01–2025-12-31 and 2026-01-01–2026-09-29, IST. Only the existing 2026 period was testable; 2025 H2 was absent locally and outside Groww's documented 5-minute history range. No old-data fetch, alternate provider, or contract substitution was made. Scope coverage manifest: `reports/multi_year_final_scope_coverage.json`.
- Coverage for 2026-01-01–09-29: 184 expected sessions; underlying 13,783/13,800 5m candles (17 missing on Sep 29, 14:05–15:25); 736 expected exact option contract-days, 561 complete, 1 partial, 174 missing/unselectable; 42,149/55,200 option candles (76.36%); 112 fully usable, 55 partial, 17 unusable days; 13,276 missing option intervals. Partial slot: Feb 3 PE ITM3 (74/75).
- Corrected L2L baseline remains 361 setups; 203 entries; 57 targets, 145 SL, 1 ambiguous, 158 skipped; +237.45 gross points, PF 1.166, max DD 250.05, longest loss streak 23. Jan 1 PE ITM2 entry 129.10 was already over Opening High 126.50; entry-quality artifact now reclassifies this source-ledger `TARGET` as skipped, matching the corrected replay. L2L quality summary: 194/203 (95.6%) had first post-entry low below entry; mean opening range 47.14; median target distance 36.55. No new entry filter is recommended. Existing Jan–Jun-selected SL2, TP50 and SL4+TP50 alternatives failed Jul–Aug validation; retain canonical SL4/Opening High.
- Executed Ekalayava policy research on 253 saved causal entries: A structural trough / B breakout-candle low / D Opening Low anchors × buffers 0/2/4 × targets TP100/75/50/25 = 36 policies, plus one separate trailing candidate; 9,361 policy-entry results. C recovery/base invalidation aliases A because there is no distinct recorded boundary. Stops/targets are experimental only. Jan–Jun development selected A0/TP100 (+1,001.70 gross; +5.24/entry; PF 1.337; DD 513.25; streak 23), B2/TP100 (+1,142.40; +5.98/entry; PF 1.580; DD 306.30; streak 25), D0/TP25 (77/191 valid in training, 114 excluded for invalid stop-at-entry; −82.34; −0.43 per eligible entry; PF 0.797), and trailing A−2/TP100 (+143.55; +0.75/entry; PF 1.062; DD 542.95). A, B and trailing passed the limited Jul–Aug screen (+213.00/+4.53, +114.70/+2.44, +19.40/+0.41 per eligible entry respectively); D failed (only 21/47 validation entries had valid stops; 26 excluded; −67.65/−1.44 per eligible entry). All three passing candidates were negative in the incomplete 15-entry September check: A −155.35 (PF .327), B −111.40 (PF .304), trailing −83.90 (PF .423). No Ekalayava stop/exit candidate is ready for adoption; original strategy specification and production behavior remain unchanged.
- A0/TP100 subgroup record: CE +632.35 (43 target/75 stop/8 EOD), PE +427.00 (44/76/7); ITM2 +476.95 (43/76/9), ITM3 +582.40 (44/75/6). Its 11:00+ entry bucket contributed +1,888.20 while early and 10:00–10:59 buckets were −572.40 and −256.45; this concentration is descriptive and requires validation, not a proposed time filter. The D Opening Low stop is invalid at entry for 140–147 of 253 signals per D policy; exclusions stay in eligible-entry denominators. All results are gross premium points without costs or rupee sizing.
- Main report: `reports/MULTI_YEAR_L2L_EKALAVAYA_RESEARCH_FINAL.md`. Ekalayava trade paths/summary/selection: `reports/ekalayava_exit_policy_trades.csv`, `reports/ekalayava_exit_policy_summary.csv`, `reports/ekalayava_exit_candidate_selection.json`. L2L entry paths/summaries: `reports/multi_year_l2l_entry_quality.csv` and `reports/multi_year_l2l_entry_quality_summary.csv`. Implementation: `app/research_ekalayava_exits.py`; offline runner: `tools/run_ekalayava_exit_research.py`.
- This experiment is complete; do not repeat it absent new independent data or a specific new question. Next research step: obtain provenance-verifiable exact-contract 5m data for an independent period (2025 H2 if available from a compliant source), pre-register the evaluation, and keep any Ekalayava lifecycle change unapproved until owner-reviewed. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`; no order or observer was run.

**Updated:** 2026-10-13. This is the single handoff summary. Research and paper observation only; no live trading. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`. The latest authoritative cumulative run is the corrected Jan–Sep 2026 validation below. Earlier reports are preserved but some used the old selector and must not be merged with the corrected results.

## Multi-year optimization and validation run — 2026-10-13

- Completed offline analysis using existing saved Jan–Sep dataset; no market data was downloaded and no observer/order API was run. Exact baseline reproduced: **361 L2L setups; 57 target, 145 SL, 1 ambiguous, 158 skipped; +237.45 gross points; PF 1.166; max DD 250.05; loss streak 23; median hold 10m** (zero event-replay mismatches). Ekalayava: **253 entries; 109/253 (43.1%) Opening High touches; all 253 unresolved** under the missing canonical exit lifecycle.
- Data inventory found 2026-01-01 through 2026-09-29 only. Coverage for requested Jan–Sep 30: 185 expected sessions; underlying present 184, 13,783/13,875 bars (99.3%); 740 option contract-days, 561 complete, 1 partial, 178 missing/unselectable; 42,149/55,500 option bars (75.94%); 112 fully usable, 55 partial, 18 unusable days. September is incomplete (33/84 option slots; underlying absent Sep 30). No local 2022–2025 5m datasets; Groww docs limit 5m historical access to recent three months, so no older years tested and no substitute source used.
- L2L stop forensics: 145 complete pre-stop paths, 73 positive vs 72 zero MFE; MFE mean/median 8.50/0.55 points; 48 reached ≥25%, 22 ≥50%, 8 ≥75%, and 0 reached 100% of target distance before stop. 72 stops occurred in first post-entry bar. 67 later touched Opening High after stop; this is not recovery of stopped trades.
- Independent alternatives selected on Jan–Jun only: SL2 (+48.30 training; +0.180/setup), TP50 (+221.63; +0.824/setup), combined SL4+TP50 (+221.63; +0.824/setup). Each failed the predeclared Jul–Aug validation screen: candidate points/setup below baseline +1.131; independent SL2 also had DD 80.80 vs baseline 74.50. September is an incomplete chronological diagnostic, previously examined for target policies, not an untouched holdout. Overall recommendation **NO RELIABLE WINNER — MORE EVIDENCE REQUIRED; retain canonical SL4/Opening High**.
- Baseline points concentrated: May +298.00 (larger than full-period +237.45); March −92.35, April −65.65, June −96.70, July −64.70. Ekalayava mean/median MFE +57.35/+31.05 and MAE −53.27/−45.60; target-touch time mean/median 93.72/65m. Target touches are observations, not wins or P&L.
- Full evidence: `reports/MULTI_YEAR_STRATEGY_OPTIMIZATION_FINAL.md`; machine-readable candidates, trade paths, coverage, and selection under `reports/multi_year_*.csv`, `.json`. Existing prior reports remain preserved. Canonical rules and production code unchanged. Exact next research step: obtain provenance-verifiable 2022–2025 5m NIFTY underlying plus exact daily option contracts or formally limit scope to 2026; independently, approve Ekalayava exit lifecycle before any P&L backtest. Do not repeat this bounded 2026 candidate grid without new data/specification.

## Paper observer finalization and independent verification — 2026-10-12

- Implemented a read-only `GrowwPaperObserver`: completed NIFTY 09:15 opening bar → existing exact daily expiry/ITM2/ITM3 CE/PE selector → same-session 5-minute option candles → per-contract-day paper engines → durable state and append-only journal. No adjacent contract substitution or fabricated bars.
- Closed-bar gating excludes an in-progress bucket, including the 09:30 bar at 09:32; a one-bar grace through 15:35 permits retrieval of the completed 15:25–15:30 candle. No new polling is done after the grace window.
- Restart/reconnect resumes strictly after each saved last candle; duplicate records are journal-deduplicated. Stream errors are sanitized, rate limits use bounded retries/backoff, exact-contract failures are isolated, and candle gaps invalidate new entries through the existing engine.
- Added fail-closed 2026 NSE session calendar: normal weekdays and published holidays, Feb 1 published Budget session, and closure for unsupported years / Nov 8 special session pending timings. Recheck calendar against future NSE notices.
- Independent review found the previous L2L readiness statement exceeded its evidence: mock observer integration had passed, but no live candle endpoint test had been done. L2L is **NOT READY** for live paper observation until the supervised market-hours integration gate below. Ekalayava is also **NOT READY** for an actual observer session until the same candle feed gate; its strategy lifecycle remains **observation-only**, with no canonical SL/P&L.
- This verification checked only credential presence as a boolean, then Groww read-only authentication and `get_user_profile()` succeeded. It was about 23:22 IST, after market hours. No candle/quote/LTP endpoint, historical download, continuous observer, or order call was made. Live 5-minute feed and four-stream completeness remain unverified.
- Independent recheck later on 2026-10-12 (about 23:56 IST) again completed read-only Groww authentication and `get_user_profile()` successfully, without printing credentials. The exchange was closed; no candle-data endpoint or observer was run. This does not clear the supervised live-candle integration gate.
- Fixed stale-feed handling: stale option/underlying timestamps now degrade health; stale option data disables new entries and leaves open positions unresolved. Added durable observer journal events for stream errors, gaps, contract omissions, reconnects, and duplicate/replayed candle suppression. Signal records now include setup ID and Ekalayava anchor distance. Journal append is deduplicated, serialized in-process, fsynced, and handles a partial trailing line. Do not run multiple observers on one state directory.
- Added explicit CLI `\.venv\Scripts\python.exe -m app.paper_observer`; it runs only when manually invoked, can be stopped with Ctrl+C, and persists a stopped status. Manual supervised market-hours validation remains required.
- Verification tests: focused readiness/observer/selector/journal/safety suite **44 passed**; full repository suite **99 passed** on 2026-10-12. No historical research was rerun in the readiness recheck.
- Runtime observer files under `data/paper_observer/` are ignored by Git. Paper journal and health output contain no credential fields.

## Project objective and current status

Validate canonical NIFTY 5-minute Level-to-Level and Ekalayava behavior using exact daily Groww contracts, maintain data-quality evidence, and only then assess controlled paper observation. No broker orders are allowed. Current readiness: **L2L NOT READY for an actual observer session pending supervised live candle-feed validation; Ekalayava is observation-only and is also blocked on that feed validation**.

## Latest finalization results — 2026-10-08

This section supersedes the originally saved raw L2L counts below where they differ. One Jan 1 PE ITM2 event entered at 129.10 with Opening High target 126.50; the prior `high >= target` simulator labeled a later bar a target despite entry already exceeding target. It is now `SKIPPED_TARGET_ALREADY_REACHED` in the historical simulator and paper engine; strategy entry/target rules did not change.

- **L2L final adjusted:** 361 setups; 202 target/SL-resolved (57 target, 145 SL), 158 skipped (157 stop-breached, 1 target-already-reached), 1 ambiguous; +237.45 gross resolved premium points; mean/median +1.18/−4.53; average target/SL +29.25/−9.86; mean resolved MFE/MAE +18.22/−12.82; mean/median holding 21.66/10 min; equal-unit event-sequence drawdown 250.05; longest target/SL streak 4/23. Valid targets 57/202 = 28.2%.
- **L2L timing:** median interval 10–15 min; mean bounds 24.0–29.0 min; 13/57 within 5 min, 24/57 within 10 min, 33/57 within 15 min, 48/57 within 60 min, 56/57 within 90 min, one at 110–115 min. No 90-minute holding rule follows from these observations.
- **Ekalayava baseline:** 253 entries; 109 Opening-High touches (43.1%), 144 no-touch paths; all 253 canonical lifecycle outcomes remain unresolved. Mean MFE/MAE +57.35/−53.27; median +31.05/−45.60; target distance mean/median 61.10/54.80; target-touch time mean/median 93.72/65 min.
- **Ekalayava structural research:** Primary causal candidate is minimum premium low from first Opening-Low-break candle through the completed bar immediately before entry; valid below entry in 253/253, median distance 22.95, later revisited 187/253 (73.9%). Hypothetical buffer 0/2/4 outcomes (target/SL/unresolved) are 87/151/15, 89/146/18, 91/142/20; resolved target fractions 36.6%, 37.9%, 39.1%. These are not canonical P&L. No numeric buffer is justified; optional `EKALAYAVA_SL_BUFFER_POINTS` remains unset by default, preserving observation-only behavior. The canonical strategy document remains unchanged.
- **Readiness/safety at the 2026-10-08 report date:** L2L **NOT READY**; Ekalayava **READY FOR OBSERVATION ONLY**. The Groww coordinator, exchange calendar, and reconnect integration were not end-to-end then. These components were implemented on 2026-10-12; see the current section above. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`; no order was run.
- Detailed artifacts: `reports/l2l_final_validation.md` and `reports/L2L_FINAL_VALIDATION.json` (existing lowercase Markdown convention retained), `reports/EKALAYAVA_FINAL_RESEARCH.md/.json`, `reports/STRATEGY_FINAL_COMPARISON.md`, and `reports/paper_trading_readiness.md` (existing lowercase convention retained).

## Canonical strategy definitions

- **Level-to-Level (L2L):** NIFTY CE/PE ITM2/ITM3; Asia/Kolkata completed 5-minute bars; first candle defines opening high/low; a completed red candle breaks below Opening Low; enter at close of the first subsequent completed green bar, between 09:15–11:00; SL = Opening Low minus configured buffer (canonical/default 4 premium points); target = Opening High.
- **Ekalayava:** opening-low breakdown → recovery and causal swing high (current code uses left=2/right=0) → later completed candle breaks/closes above swing high while still below Opening High → entry at close. Opening High is target/reference. No canonical executable SL, opposite-signal exit, EOD/expiry exit, or end-of-data valuation exists.
- **Ekalayava structural SL:** The canonical document still does not specify an exact anchor, numeric buffer, or trigger. New research proposes the pre-breakout reversal-sequence trough as a causal anchor, but no numeric buffer was justified and this candidate is not canonical until approved/versioned. Paper engine can optionally evaluate a configured stop; `EKALAYAVA_SL_BUFFER_POINTS` defaults to unset, which keeps Ekalayava observation-only.

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

### L2L (canonical 4-point buffer; target-at-entry edge case is adjusted in latest section above)

- Original stored source summary: 361 setups; the final validation reclassifies one of its 58 target labels as a target-already-reached skip. Use the corrected 57-target / 145-SL / 158-skip totals and +237.45 points in the latest section above.
- Train Jan–Jun after the correction: 269 setups; 147 resolved (41 target/106 SL), 121 skipped, 1 ambiguous; +134.85 points.
- Validation Jul–Aug: 72 setups; 41 resolved (12/29), 31 skipped; +81.40 points.
- Final OOS Sep: 20 setups; 14 resolved (4/10), 6 skipped; +21.20 points. **Incomplete:** through Sep 29 only, 33/84 option slots complete.
- Jan–Mar after the correction: 130 setups, 62 resolved (18/44), 67 skipped, 1 ambiguous; −0.80. Apr–Jun: 139 setups, 85 resolved (23/62), 54 skipped; +135.65. Jul–Sep: 92 setups, 55 resolved (16/39), 37 skipped; +102.60.
- Monthly points Jan→Sep after the correction: **+49.95, +41.60, −92.35, −65.65, +298.00, −96.70, −64.70, +146.10, +21.20**. May alone exceeds the total; these are gross points, not net returns/profitability.
- Descriptive 3-point-buffer sensitivity on the same full sample: 51 target/137 SL/172 skipped/1 ambiguous; +78.20 points. No rule changed and no parameter was selected.

### L2L target-hit timing study — 2026-10-08 (latest adjusted counts above supersede old source ledger counts)

- The original timing ledger retains 58 source target labels. One is excluded in the final validation because entry already exceeded the target. Corrected counts: 202 target/SL-resolved (57 target/145 SL), 158 skipped, one ambiguous; target fraction 28.2%.
- From entry close, 13/57 (22.8%) appear in the first later candle (0–5m), 24/57 within 10m, 33/57 within 15m, 38/57 within 30m, 48/57 within 60m, 56/57 within 90m, and one in the 110–115m window. Median interval **10–15m**; mean bounds **24.0–29.0m**.
- Valid target hits by side/rank: CE 26/104 resolved, PE 31/98; ITM2 26/101, ITM3 31/101. Monthly target counts Jan–Sep: **10, 6, 2, 4, 14, 5, 3, 9, 4**. Entry-close hour: 39 valid targets from 09:xx and 18 from 10:xx; none from 11:00.
- 5-minute OHLC cannot provide exact intrabar target time or target-vs-low ordering. Two original entry candles had high ≥ target, but entry is at candle close so neither establishes a post-entry touch. One entry was already above target and is now skipped. The prior 203-row timing ledger is preserved; use corrected 57-hit counts above for final statistics.
- Observed timing shows material short-duration behavior (13 valid target hits in the first post-entry bar), alongside a long tail; no time filter/exit optimization was performed and no canonical rule changed.

### Ekalayava (observation only)

- **253 entries; 109 opening-high touches (43.1%); 144 no-touch observations. All 253 lifecycle outcomes remain unresolved.** No SL count, win rate, realized P&L, or target-point total is defined.
- Full same-day post-entry observation through 15:25: mean/median MFE +57.35/+31.05; mean/median MAE −53.27/−45.60; mean/median time to MFE 113.99/85 min; time to MAE 179.05/195 min. Among target touches, time mean/median 93.72/65 min; target distance mean/median 61.10/54.80.
- Descriptive, causal pre-entry candidate low = lowest premium low from first opening-low break through completed entry candle; later revisit: 187/253 (73.9%). Breakout-candle low revisited 223/253 (88.1%); opening low revisited 249/253 (98.4%). These are not stop rules.
- Train Jan–Jun: 191 entries, 83 touches; validation Jul–Aug: 47, 22 touches; September through Sep 29: 15, 4 touches. Target touches are not wins.

## Paper engine + selected-date historical replay — 2026-10-08

- Replaced the prior live listener’s “latest bucket is complete” behavior with `FiveMinuteCandleBuilder`, which emits only after the 5-minute close boundary, rejects duplicate/late ticks, orders in-bucket ticks, reports gaps without fabricating candles, and can snapshot/restore.
- Live contract selection now uses the historical catalog-first method: completed NIFTY 09:15 open → earliest Groww expiry on/after that date → exact CE/PE ITM2/ITM3 strikes from that expiry chain. Expiry-label mismatch and missing exact ranks fail closed. Rollover evidence: Jan 6 selected expiry Jan 6 (CE 26100/26050; PE 26250/26300); Jan 7 selected Jan 13 (CE 26050/26000; PE 26200/26250). No strike/expiry substitution.
- `PaperContractEngine` is stateful per contract-day. It implements the canonical red-break → first later completed green L2L entry at close with configured 4-point SL buffer and Opening High target; daily duplicate protection; SL/target/ambiguous handling; no forced EOD exit. Gaps invalidate new entries and leave open trades unresolved. Restart requires the same exact symbol and strategy parameters.
- Ekalayava engine follows the current causal left=2/right=0 swing-high entry. It freezes the empirical reversal-sequence trough before the breakout candle. With buffer unset, it records observations and no realized outcome. With an explicitly configured nonnegative buffer, it can journal paper stop/target/ambiguous lifecycle results. This optional feature is research-only and does not update the canonical definition.
- New append-only, record-ID-deduplicated JSONL journal includes contract identity, NIFTY price, strategy levels, entry cause, statuses, MFE/MAE/time-to-extremum, target touch, structural observations, and data-quality status.
- Candle-by-candle replay used existing complete local data, not new downloads or a full-period rerun. Eight signal examples (5 L2L, 3 Ekalayava) plus one no-setup contract-day were replayed; each selected option day had 75/75 session bars. All selected entry times/prices matched stored baselines. L2L target/SL/skip/ambiguous outcomes, exit times, SL/target levels, and MFE/MAE matched. Ekalayava entry, target-touch time, MFE/MAE, and candidate structural low matched. Jan 1 CE ITM2 Ekalayava: 09:50 entry, no touch, MFE +1.65 / MAE −43.80, candidate low 127.40; Jan 2 PE ITM2: 14:35, no touch, +2.40 / −14.30, candidate 39.70; Jan 5 CE ITM3: 09:50, target touched 10:20, +62.85 / −78.55, candidate 105.90. All remained unresolved; no Ekalayava P&L.
- Prefix replay had no L2L signal before the completed first-green entry candle; adding that candle generated the same timestamp as full-day replay. Missing bars, late/out-of-order ticks, duplicate candles, state restore, and parameter mismatch are tested.
- Latest full test suite: **82 passed** after adding stop-buffer default/configuration, optional Ekalayava lifecycle, journaling, and L2L target-already-reached guard tests. Canonical strategy entry definitions remain unchanged. No live polling was started; no order APIs were called.
- At the 2026-10-08 replay report date, readiness remained **L2L NOT READY; Ekalayava READY FOR OBSERVATION ONLY**. The coordinator/calendar/reconnect wiring was added and tested 2026-10-12. Ekalayava anchor proposal is documented; numeric buffer and canonical adoption/lifecycle decisions remain unresolved.

## Earlier phases and selector caveat

- Period A (Apr 27–Sep 25) and Period B (Jan 1–Apr 24) reports remain preserved. Their previously reported results used the earlier selector and are **superseded for cumulative comparisons** by the new daily catalog-first rerun. Do not add Period A/B totals to the final Jan–Sep totals.
- July–August corrected run remains useful and matches the full-run slice: 44 sessions; underlying 100%; 111/176 option slots complete, 65 catalog-absent; L2L 72 setups, 41 resolved (12 target/29 SL), 31 skipped, +81.40; Ekalayava 47 entries, 22 target touches, 25 no touch.
- Earlier Sep 28–Oct 1 fresh reports are preserved, but their Sep 28–29 option selection does not resolve to the exact required ITM2/ITM3 symbols in the returned catalog. Their trade observations are excluded from corrected final OOS. Sep 30 underlying remains unavailable.
- Older Period A/B Ekalayava behavior comparison (302 events) remains archival evidence from the earlier selector; use corrected Jan–Sep events for current cumulative conclusions.

## Paper readiness and safety — current decision 2026-10-12

- `app.config` hard-fails if execution is enabled or paper-only is false; current values are false/true. No order API calls exist in application code; no orders were placed.
- `app.candle_builder` and `app.paper_engine` now provide close-aware candles, exact daily selection, stateful L2L and observational Ekalayava, duplicate/restart protection, and append-only journal events. Representative selected-day replays match stored historical baseline signals/outcomes.
- Read-only observer wiring, calendar, persistent engines/journal, exact-session contract selection, completed-candle gating, and deterministic reconnect/restart checks are implemented. L2L and Ekalayava are **NOT READY for an actual live observer session** until Groww candle endpoint behavior and current-session completeness are checked in a supervised market-hours run. Ekalayava strategy output remains **observation-only**; no canonical structural SL or full exit lifecycle exists. Target touch is not an exit or win. Authentication and read-only profile access succeeded on 2026-10-12; candle connectivity was not tested because the market was closed.
- Market code is deterministic; LLM use is limited to research-agent tasks, not every candle.
- `.env`, `secrets.txt`, tokens, and keys are ignored/untracked and never included in reports.

Checklist and replay trace: `reports/paper_engine_replay_validation.md`.

## Reports

- `reports/jan_sep_2026_final_validation.md` — selector audit, rollover traces, coverage, splits, conclusions.
- `reports/l2l_final_validation.md` — L2L distributions, sensitivity, concentration, readiness.
- `reports/L2L_FINAL_VALIDATION.md/.json` — final adjusted L2L results and target-timing edge-case correction.
- `reports/ekalayava_final_validation.md` — MFE/MAE, structural-low revisits, touch distributions, unresolved lifecycle.
- `reports/EKALAYAVA_FINAL_RESEARCH.md/.json` — structural anchor, buffer sensitivity, subgroup and chronological hypothetical lifecycle research.
- `reports/STRATEGY_FINAL_COMPARISON.md` — measured distributions and limitations for both strategies.
- `reports/PAPER_TRADING_READINESS.md` — current integration and paper-only readiness audit.
- `reports/paper_trading_readiness.md` — deterministic live/paper component audit and readiness decision.
- Preserved prior detailed reports: `reports/july_august_2026_full_analysis.md`, `reports/baseline_diagnostic_2026-04-25_to_2026-09-25.md`, `reports/ekalayava_spec_implementation_audit.md`, `reports/cross_period_baseline_comparison.md`, `reports/ekalayava_trade_behavior_cross_period.md`, and the Sep 28 / Sep 28–Oct 1 reports.

## Exact next research step

1. In a supervised paper-only session, validate Groww authentication and candle endpoint behavior, opening-bar capture, exact four-contract selection where catalog data supports it, actual completeness, and disconnect/reconnect recovery. Do not place orders or start unattended continuous execution.
2. Obtain an owner-approved, versioned Ekalayava lifecycle decision for the exact structural anchor, buffer/trigger, target behavior, same-candle ambiguity, opposite signal, EOD, expiry, and end-of-data before reporting P&L or simulating an approved lifecycle.
3. Separately request authoritative Groww listings for the 174 absent exact historical slots and retry Sep 30 underlying only if historical-data recovery is explicitly resumed; do not repeat the completed baselines.

## Completed experiments — do not repeat

- Period A, Period B, diagnostic, Ekalayava spec audit, cross-period baseline, and prior Ekalayava behavior study.
- July–August 2026 contract audit and corrected baseline.
- Corrected full Jan–Sep 2026 catalog-first selection, exact-symbol recovery, coverage, L2L/Ekalayava rerun, 3/4-point L2L sensitivity, and readiness audit. Repeat only after exact missing data is recovered or a versioned strategy-spec change requires it.
- Stateful paper engine, completed-candle builder, representative candle-by-candle historical replay, and Jan 6→Jan 7 expiry rollover validation. Do not repeat these selected replays unless engine logic changes; expand only to cover integration/recovery blockers.
