# Execution Audit and Read-Only Observer Readiness

**Date:** 2026-10-13
**Decision:** **BLOCKED** for supervised market-session observer validation until the corrected candle path has passed an end-to-end, bounded run during market hours. Real-money execution remains disabled and is outside the scope of this observer.

## 1. Executive summary

The saved trade ledgers reconcile to the target-hit report; no optimization grid was rerun. The L2L canonical baseline has 57 target exits from 203 eligible entries. The saved policy with the most target exits, `SL_6_TP_25`, has 116/236 (49.15%), 59 more exits and +21.07 percentage points, but gross points decline from +237.45 to +218.69. Ekalayava has no canonical exit lifecycle and therefore no canonical target-exit count or P&L. Its highest-exit experimental policy, `A_STRUCTURAL_TROUGH_B4_TP25`, has 157/253 target exits, but gross is −272.90 and validation gross is −72.25.

The source audit found the observer’s reachable flow to be read-only and fail-closed under unsafe configuration. One bounded after-hours Groww request retrieved and validated candle data, then exposed a local final-bar timestamp bug. That bug is fixed and has an offline regression test. The corrected path has **not** been retried against Groww, and a complete supervised market-session run has not occurred. No order endpoint was invoked, no historical dataset was downloaded, and no candle data from the bounded request was persisted.

The exact target metrics and policy comparisons are in [`TARGET_HIT_ANALYSIS_L2L_EKALAYAVA_2026-10-13.md`](./TARGET_HIT_ANALYSIS_L2L_EKALAYAVA_2026-10-13.md) and the generated CSVs described below. Counts describe saved events, not the complete market opportunity set; coverage is incomplete.

## 2. Repository and evidence inventory

Reviewed the canonical and experimental strategy definitions, saved trade and observation ledgers, generated summaries, coverage inventory, runtime configuration, Groww auth/data wrappers, exact contract selector, paper observer/engine, safety lock, journal, and tests.

Relevant code and evidence:

- `app/strategies.py`, `app/research_target_policies.py`, and `app/research_ekalayava_exits.py`: entry/exit policy definitions and offline fills.
- `app/paper.py`: L2L research backtest and path/outcome classification.
- `app/paper_observer.py`, `app/paper_engine.py`, `app/contract_selection.py`, `app/groww_auth.py`, and `app/groww_data.py`: read-only observer, paper processing, contract selection, authentication, and market-data access.
- `app/config.py` and `app/safety.py`: configuration validation and execution lock.
- `reports/multi_year_baseline_metrics.csv`, `reports/multi_year_l2l_combined_sl_tp_trades.csv`, `reports/ekalayava_exit_policy_trades.csv`, `reports/multi_year_ekalayava_observations.csv`, and `reports/multi_year_data_coverage.json`: saved evidence sources.
- `reports/target_hit_policy_period_summary.csv`, `reports/target_hit_baseline_comparison.csv`, and `reports/target_hit_data_quality_summary.csv`: reproducible aggregation outputs. Generator: `tools/generate_target_hit_reports.py`.

The saved L2L combined ledger has 12 policies × 361 setup rows. Ekalayava has 37 experimental policies × 253 entries; canonical observation records join to experimental rows one-to-one by date, timestamp, and exact symbol. The C-anchor alias is not counted as a separate policy. Report generation uses saved ledgers only; no full grid was rerun.

## 3. Independently reconciled L2L baseline

The `SL_4_TP_100` canonical baseline contains 361 setup rows: 203 eligible entries, 57 target exits, 145 stop exits, 1 ambiguous terminal touch, 0 unresolved outcomes, and 158 pre-entry skips (157 stop-already-breached and 1 target-already-reached). Gross is +237.45 premium points.

The highest target-exit-count saved candidate is `SL_6_TP_25`: 116/236 eligible entries (49.15%), versus baseline 57/203 (28.08%). This is +59 exits and +21.07 percentage points. It has 132 touches, of which 16 are ambiguous rather than confirmed target exits; 104 stop exits and no unresolved paths. Gross falls by 18.76 points to +218.69. Maximum drawdown improves from 250.05 to 161.13 and the longest losing streak from 23 to 8. Thus, risk-sequence metrics and target counts move favorably in this saved simulation while gross deteriorates; neither makes it a proven improvement.

The exit-count increase also appears in the existing Jul–Aug validation segment: 25/50 (50.00%) for `SL_6_TP_25` versus 12/41 (29.27%) for baseline, +20.73 percentage points. Validation gross is only +26.61 versus baseline +81.40. This is a previously used validation period, not an independent holdout.

## 4. Ekalayava entry and exit audit

The canonical entry/observation ledger contains 253 entries, 109 observed Opening-High touches (43.08%), and 144 non-touches. Its canonical exit lifecycle is undefined: all 253 outcomes remain unresolved as trades, so a canonical target-exit count, stop count, gross P&L, drawdown, and losing streak are unavailable.

The experimental candidate with the most target exits is `A_STRUCTURAL_TROUGH_B4_TP25`: 157/253 (62.06%), 189 observed candidate-target touches, 93 stops, 3 experimental end-of-session exits, and no ambiguous or unresolved outcomes in the saved policy ledger. Thirty-two of its 189 touches did not qualify as this candidate’s simulated target exit. Its gross is −272.90 points; its validation gross is −72.25. The 109 canonical Opening-High touches and the 189 experimental TP25 touches use different target levels and are not an apples-to-apples exit comparison.

The canonical signal remains observation-only absent an approved exit lifecycle. All Ekalayava buffer/target combinations remain experimental and are not adopted by this change.

## 5. Execution-model audit and proposed fill specification

The saved L2L policy simulator enters at the completed signal candle’s close, starts exit monitoring on the next completed candle, evaluates stop/target from OHLC, and labels a same-candle stop-and-target touch ambiguous. It books threshold prices for single-level touches, does not model a stop gap at the open, and has no forced end-of-day exit. Historical policy CSVs contain 75 source bars per entry but not per-candle timestamps, so independent cadence replay of those saved policy paths is not possible.

The experimental Ekalayava simulator differs: a stop gap through the active stop fills at the candle open; a target gap is priced at the target; a same-bar touch of both is ambiguous unless the open itself establishes precedence; and some experimental policies close at the final valid session candle. These are simulator conventions, not evidence of actual executable fills.

`app/paper.py::simulate_level` previously treated an incomplete future path as though later available candles were sufficient to resolve it and left no-future-candle entries open without an explicit data-quality outcome. It now fails closed as `UNRESOLVED_DATA_GAP` or `UNRESOLVED_NO_FUTURE_CANDLES`; it does not synthesize candles or add an end-of-day exit. Tests cover a gap before a later target and an entry with no future bars.

**Proposed specification for any future execution-quality study (not implemented or adopted here):**

1. Freeze entry timing and price semantics before comparing policies; do not equate a completed-bar close with a guaranteed order fill.
2. Use adverse stop-gap treatment at the first executable price available after a gap, and do not award favorable gap improvement without supporting quote/trade evidence.
3. Treat same-bar stop/target ordering as unresolved when OHLC cannot establish sequence. Missing bars, stale feeds, and missing session tails remain unresolved rather than being interpolated.
4. Model option bid/ask spread, slippage, fees, liquidity, and quantity separately from gross premium-point results. A candle touch alone is not proof that a target limit order filled.
5. Define explicit session-end treatment only as a separately named, approved policy; do not silently impose an EOD exit on the canonical strategies.

This proposal must not be confused with the historical target-hit report, which reports the saved simulators’ conventions.

## 6. Historical evidence availability

The available inventory covers 2026-01-01 through 2026-09-30: 740 expected option contract-days, 561 complete, 1 partial, and 178 missing or unselectable, with 42,149 of 55,500 expected option bars (75.94%). Underlying bars cover 13,783/13,875 through Sep 29; Sep 30 is absent and Sep 29 is missing 17 late bars. No local 2022–2025 five-minute dataset is present.

Missing contracts can hide entries and outcomes. CSV policy ledgers provide saved event evidence but cannot establish a complete market opportunity count. No additional historical data was downloaded during this work. A separate one-shot read-only Groww candle response was retrieved in memory for processing validation only and was not saved.

## 7. Fixes and generated outputs

- `app/paper.py`: explicitly marks missing future intervals and empty post-entry paths unresolved.
- `tests/test_paper_backtest.py`: adds regressions for a missing interval before a later target and no future candles.
- `app/paper_observer.py`: fixes final completed-bar handling after market close by clamping with `pd.Timestamp(end) - timedelta(minutes=5)`; this accepts a Python `datetime` from the market-close clamp.
- `tests/test_paper_observer.py::test_completed_session_bars_handles_the_final_bar_after_market_close`: verifies that at 15:35 IST the 15:25 candle is returned as complete.
- `tools/generate_target_hit_reports.py`, `tests/test_target_hit_analysis.py`, and the target-hit report/CSVs provide saved-ledger aggregation with policy, period, contract and entry-time segments, duplicate checks, touch/exit separation, and data-quality checks.
- Updated `reports/paper_trading_readiness.md` so its provider and test history reflects the bounded candle request and latest verification.

The generator reported 2,476 policy/period/segment rows, 2,624 comparison rows, and 25 data-quality checks. `target_hit_data_quality_summary.csv` records no full optimization-grid replay, no saved unresolved policy outcomes, incomplete contract coverage, and no downloaded historical dataset.

## 8. Test and static-check results

Commands actually run after these code changes:

```text
/home/codespace/.python/current/bin/python -m pytest -q tests/test_paper_backtest.py tests/test_target_hit_analysis.py tests/test_paper_observer.py
18 passed in 1.09s; exit code 0

/home/codespace/.python/current/bin/python -m pytest -q
114 passed in 6.87s; exit code 0

/home/codespace/.python/current/bin/python tools/generate_target_hit_reports.py
Generated 2476 policy/period/segment rows, 2624 comparison rows, and 25 data-quality checks; exit code 0

git diff --check
No whitespace errors; exit code 0
```

Pylance syntax validation passed for `app/paper.py`, `app/paper_observer.py`, `tools/generate_target_hit_reports.py`, `tests/test_target_hit_analysis.py`, and `tests/test_paper_observer.py`; `tests/test_paper_backtest.py` was also imported and executed by pytest. The observer file’s current Pylance diagnostics include two unused-variable warnings (`date` and `trade`); no syntax error was reported. These unrelated warnings were not changed.

## 9. Groww connectivity outcome

The earlier read-only Groww authentication and profile check succeeded. During one bounded, after-hours NIFTY cash 5-minute request, authentication, provider retrieval, and provider candle validation succeeded; the observer then raised an `AttributeError` in the final-bar filter because the clamped market-close value could be a Python `datetime`. The corrected local implementation is covered by a deterministic synthetic regression, but it has **not** been retried against Groww after the fix. This was not a complete observer run: live option contract selection, four-contract completeness, market-hours timing, and full persistence/recovery remain unverified.

The check was one-shot, bypassed the retry wrapper, had bounded timeout controls, wrote no candle data, and called no quote, LTP, or order endpoint. No continuous strategy loop was started.

## 10. Read-only safety evidence

- `app/safety.py::ExecutionLock` rejects `execution_allowed=true` or `paper_only=false` at initialization and rechecks the kill switch and paper-only flags at operation boundaries.
- `app/paper_observer.py::GrowwPaperObserver.__init__` and `run_once`, and `app/paper_engine.py::PaperContractEngine` initialization and `process_candle`, apply this lock. Reconnect uses the existing read-only client factory and does not change execution configuration.
- Observer and engine records identify `READ_ONLY_OBSERVATION`, `execution=DISABLED`, and `paper_only=true`.
- `tests/test_safety_audit.py` checks kill-switch denial and that application source contains no `place_order(`, `modify_order(`, or `cancel_order(` call. Direct inspection found no order-submission, modification, or cancellation methods in the application source.
- Effective configuration values from `app.config.CFG` were checked without outputting credentials: `execution_allowed=False`, `paper_only=True`, `kill_switch=False`, `ekalayava_experimental_exit_simulation=False`.
- No real order was submitted, modified, or cancelled. The result supports read-only paper observation only, not live execution.

## 11. Observer readiness matrix

Statuses use the guide’s allowed values. PASS means the local code boundary or deterministic offline tests support the listed behavior; it does not mean a complete live observer session passed.

| Area | Status | Evidence and remaining condition |
|---|---|---|
| Read-only enforcement | PASS | Lock at observer/engine boundaries; no order methods reachable in application source; safety audit tests pass. |
| Contract selection | BLOCKED | Offline selector chooses exact expiry/strike ranks and leaves missing CE/PE ITM2/ITM3 absent. The selector has no source timestamp with which to verify chain freshness, and live option-chain completeness remains unverified. |
| Candle completion | BLOCKED | Timestamp/closed-bar logic and final-bar regression pass offline; corrected code has not completed an end-to-end Groww run. |
| Timezone and calendar | PASS | IST conversions, session bounds, and calendar behavior are covered by code/tests; live provider timestamps still need supervised confirmation. |
| Duplicate prevention | PASS | Stable candle/event identities and replay suppression are exercised with local/mock tests; reconnect behavior is not live-verified. |
| Persistence and restart recovery | BLOCKED | State/journal restart behavior has deterministic tests; live session recovery, storage-failure handling, and recovery after this fixed candle path are not supervised end to end. |
| Missing/stale data | PASS | Local gap/staleness handling degrades health, avoids synthetic bars, and prevents affected stale option streams from opening new entries; live feed behavior remains unverified. |
| Reconnect behavior | BLOCKED | Mock reconnect/reauthentication tests exist; live reconnect and rate-limit behavior have not been verified. |
| Signal journal integrity | PASS | Stable IDs, deduplication, serialized append, and persistence tests/code are present; a full live journal round trip remains pending. |
| Paper simulation | PASS | Candle processing is paper-only; L2L incomplete paths now remain unresolved; this does not validate real fills. |
| Kill switch and operational stop | PASS | Kill switch is enforced at boundaries and tested; manual CLI supports operator stop. |

**Overall observer status: BLOCKED** pending a supervised market-session run through corrected candle processing and persistence.

## 12. Files changed

- `app/paper.py`
- `app/paper_observer.py`
- `tests/test_paper_backtest.py`
- `tests/test_paper_observer.py`
- `tools/generate_target_hit_reports.py`
- `tests/test_target_hit_analysis.py`
- `reports/TARGET_HIT_ANALYSIS_L2L_EKALAYAVA_2026-10-13.md`
- `reports/target_hit_policy_period_summary.csv`
- `reports/target_hit_baseline_comparison.csv`
- `reports/target_hit_data_quality_summary.csv`
- `reports/paper_trading_readiness.md`
- `reports/EXECUTION_AUDIT_AND_READONLY_OBSERVER_READINESS_2026-10-13.md`

## 13. Remaining risks and uncertainties

- Incomplete historical contracts and missing periods may conceal setups/outcomes; policy CSVs do not retain per-candle timestamps for independent L2L replay.
- Gross points omit fees, bid/ask, slippage, liquidity, quantity, and reliable fill evidence.
- The L2L high-count candidate’s existing validation-period exit-rate increase did not improve validation gross. Existing validation data is reused and is not an independent holdout.
- Ekalayava experimental outcomes cannot be compared to canonical realized outcomes because the canonical exit lifecycle is undefined.
- The fixed observer path has not been run against Groww after correction. Live exact-contract completeness, market-hours candle delivery, provider pacing, reconnect, and durable recovery remain unverified.
- A passing test suite does not establish strategy profitability, robustness, or readiness for any live execution.

## 14. Single recommended next action

During the next supervised NSE market session, run one bounded **read-only** observer validation after independently confirming `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`, and the kill switch is inactive. Inspect exact selected contracts, completed candle timestamps, health, gap/stale events, journal/state persistence, and clean operator stop. Stop immediately on degraded health or any safety invariant violation; do not place orders.

## Decision summary

Verified the saved L2L baseline at 57/203 target exits and the highest-count L2L policy at 116/236; the +59 exits and +21.07 percentage-point rate did not improve gross. Ekalayava has no canonical target-exit count; its highest-count experimental policy recorded 157/253 exits with negative gross. Fixed unresolved-path classification and after-close final-candle handling, regenerated the CSV reports, and passed 18 focused and 114 full-suite tests. The after-hours Groww response exposed a processing defect; its fix is only offline-verified. Keep all execution disabled and the observer **BLOCKED** until the supervised read-only market-session validation succeeds.
