# Paper-Trading Readiness — Independent Verification

**Updated:** 2026-10-12. Repository and source audit, local tests, and one read-only Groww profile check were performed. At verification time it was about 23:56 IST, after NSE market hours. Authentication and `get_user_profile()` succeeded in this run. No candle-data endpoint was called, no observer session was started, and no historical data was downloaded.

## Decision

| Strategy | Status | Evidence and remaining condition |
|---|---|---|
| Level-to-Level | **NOT READY** | The engine, selector, paper state, and mock coordinator tests are in place. Live Groww 5-minute candle delivery, latency, and recovery have not been verified. A supervised market-hours candle-stream check is required before calling this ready for live paper observation. |
| Ekalayava | **NOT READY** for a live observer session; **observation-only by rule** | Causal signal/observation code and mock tests are present. Its canonical SL/exit lifecycle remains undefined, so it has no canonical realized P&L. The same unverified Groww candle integration blocks actual observation. |

Both remain paper-only: `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`. Neither is ready for real-money trading.

## What was verified

- **Actual Groww connectivity:** read-only authentication and `get_user_profile()` both succeeded at about 23:56 IST on 2026-10-12. Credential values were not printed. No candle, quote, LTP, or order API was called. This verifies authentication/profile access only, not market-data delivery.
- **Unit-tested:** canonical L2L red-break → first subsequent green entry, target-already-reached skip, stop/target/ambiguity, completed bar enforcement, duplicate/restart state, exact contract selection, calendar, and paper-only safety.
- **Mock integration tested:** NIFTY opening bar → exact daily catalog-first expiry and ITM2/ITM3 CE/PE symbols → same-session completed 5-minute bars → per-contract engines → durable state/journal; per-symbol failures, reconnect, stale option feed, invalid timestamps, and restart/replayed candles.
- **Not verified with Groww candles:** live 5-minute endpoint response shape/timing, actual four-contract completeness, rate-limit behavior against service, and recovery in a live market session.

## Findings and fixes in this verification

- The earlier readiness report overstated L2L readiness based on a fake Groww-compatible client. It is downgraded to **NOT READY** pending the actual supervised candle-stream check.
- A stale option response could previously leave the observer healthy and permit delayed bars to be processed as current. Stale underlying/option candles now degrade health; stale option streams are durably marked and their engine disables new entries while open positions remain unresolved.
- The journal now carries stable `setup_id`, Ekalayava structural-low distance from entry, and durable observer events for stale/unavailable streams, gaps, exact-contract omissions, reconnects, and replayed-candle suppression. Appends are deduplicated, serialized in-process, written as complete JSONL records, and fsynced. Run only one observer process per state directory.
- `app.paper_observer` now has an explicit manual CLI. It is not started on import. Invalid candle sequences are quarantined to that exact stream while other exact contracts continue.

## Strategy audit

### Level-to-Level

The paper engine freezes opening high/low from the completed 09:15 option candle. It waits for a completed red candle with `low < opening_low`, then enters on the first later completed green candle at its close. A qualifying first green is consumed even if entry is skipped because it is already at/below the stop or at/above target. Stop is opening low minus the configured canonical 4 premium points; target is opening high. The entry-window check is on the candle start time and is inclusive through 11:00 IST. Trade monitoring starts after the entry candle. Same-candle stop/target is ambiguous; no timeout or forced session-end exit is added. State is scoped to exact symbol and date and restart skips already processed candles.

### Ekalayava

The implementation uses a causal left=2/right=0 swing candidate: a completed candle high above the previous two highs becomes the current breakout reference, available to a later candle. Entry requires a later completed candle with high and close above that stored swing while the candle high remains below Opening High; it does not require a close above Opening High. The recorded research anchor is the minimum low from the first completed Opening-Low break through the completed bar before entry; the breakout candle cannot redefine it. Anchor distance is now journaled.

No numeric Ekalayava buffer is canonical. With buffer unset, signals and subsequent MFE/MAE/target-touch observations remain unresolved and are not P&L. Explicit buffer simulation is labeled experimental and requires opt-in. It monitors only bars after entry, marks same-bar stop/target as ambiguous, and a later target cannot reverse a prior stop.

## Journal and data handling

Signal records contain stable event/setup IDs, IST event and candle timestamps, exact symbol/expiry/strike/side/rank, opening range, entry and setup timestamps, Ekalayava swing/anchor/distance, optional buffer, defined stops/targets, MFE/MAE, exit/outcome, and data quality. MFE/MAE use post-entry completed-candle highs/lows; the entry candle is excluded because entry is at its close. Observer operational events share the per-session journal and use stable record IDs. Duplicate rows are ignored; a partial trailing line is separated before the next append. State snapshots and health snapshots use temporary-file replacement. Do not run simultaneous observer processes against one state directory.

The exact catalog selector leaves absent CE/PE ITM2/ITM3 ranks missing; it does not substitute an adjacent strike. Existing Jan–Sep coverage remains incomplete (740 expected option contract-days: 561 complete, 1 partial, 178 missing/unselectable; 42,149/55,500 intervals, 75.9%). No historical figures were recalculated in this verification.

## Supervised manual validation

Only start during a supervised NSE session after confirming `EXECUTION_ALLOWED=false` and `PAPER_ONLY=true`:

```powershell
.\.venv\Scripts\python.exe -m app.paper_observer
```

The observer uses read-only Groww authentication and candle endpoints. Leave the terminal visible and inspect `data/paper_observer/observer_health.json` and the session `paper_journal.jsonl` for health, exact selected symbols, latest completed candle timestamps, data gaps, and safety flags. Stop with **Ctrl+C**; the CLI records `STOPPED_BY_OPERATOR`. If health is degraded, do not treat missing contracts or late candles as signals. This manual run is the outstanding integration gate.

Focused verification command:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_live_listener.py tests/test_paper_observer.py tests/test_nse_calendar.py tests/test_journal.py tests/test_config_secrets.py tests/test_contract_selection.py tests/test_groww_data.py tests/test_safety_audit.py tests/test_safety.py tests/test_paper_replay.py
```

Final verification on 2026-10-12: focused readiness/observer/selector/journal/safety tests **44 passed**; full repository suite **99 passed**. Commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_live_listener.py tests/test_paper_observer.py tests/test_nse_calendar.py tests/test_journal.py tests/test_config_secrets.py tests/test_contract_selection.py tests/test_groww_data.py tests/test_safety_audit.py tests/test_safety.py tests/test_paper_replay.py
.\.venv\Scripts\python.exe -m pytest -q
```

## Safety

- Runtime flags were checked as booleans only: `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`.
- `.env`, `secrets.txt`, credential/token patterns, and `data/paper_observer/` are ignored; no credential values are in reports or journal schema.
- Application source has no order-placement, modification, or cancellation calls.
- Groww authentication/profile succeeded; no market-data endpoint or order endpoint was called. No real orders were submitted and no observer was started.

Historical findings remain in [`l2l_final_validation.md`](l2l_final_validation.md), [`EKALAYAVA_FINAL_RESEARCH.md`](EKALAYAVA_FINAL_RESEARCH.md), and [`STRATEGY_FINAL_COMPARISON.md`](STRATEGY_FINAL_COMPARISON.md); they were not regenerated.
