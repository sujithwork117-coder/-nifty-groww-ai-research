# Paper Engine and Historical Replay Validation

**Date:** 2026-10-08
**Scope:** Paper-engine implementation and representative historical replay only. The Jan–Sep baseline was not rerun. Strategy definitions were not changed. No live polling was started and no broker order API was called. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`.

## Summary

The previous live listener returned a still-forming five-minute bucket and generated L2L from a single green candle whose low was below Opening Low. It did not preserve the required prior red-break state. Contract discovery could also iterate multiple expiries. Those paths have been replaced with a close-aware candle builder, a date-specific exact-contract selector, and a stateful paper engine. The engine runs L2L and Ekalayava independently and journals paper-only events.

The new engine was replayed candle-by-candle on representative complete contract-days from the already-existing Jan–Sep assembled dataset and compared with the stored canonical baseline events. All selected entry timestamps/prices and L2L outcomes/exit times matched. Ekalayava entry, target-touch time, MFE/MAE, and descriptive structural-low candidate matched; Ekalayava remained unresolved and no realized P&L was generated. The replay selection is diagnostic, not a new period-level result.

## Changes made

- `FiveMinuteCandleBuilder` aggregates timestamped LTP observations into 5-minute OHLC bars and emits a bar only after its bucket close. It rejects late/duplicate ticks, sorts in-bucket out-of-order ticks, reports missing intervals, and can snapshot/restore in-progress buckets.
- `select_daily_itm_contracts` selects the earliest Groww expiry on or after the NIFTY session date, checks contract-symbol expiry labels, resolves the exact catalog strike ladder, and returns missing ranks explicitly. No fallback strike or expiry is chosen. The live-facing selector requires the completed NIFTY 09:15 candle.
- `PaperContractEngine` is scoped to one exact contract-day. It requires completed, ordered candles; ignores duplicate bars; fails closed on out-of-order bars; invalidates unentered setups after a data gap; persists resumable state; and refuses to resume under different strategy parameters.
- L2L now requires a completed red candle to break below Opening Low, then enters at the close of the first later completed green candle within 09:15–11:00 IST. It uses the existing configured 4-point stop buffer and Opening High target, protects against duplicate daily entries, and marks same-candle SL/target as ambiguous. It does not force-close at session end.
- Ekalayava uses the existing causal `left=2/right=0` swing-high sequence and enters on a later completed swing-high breakout below Opening High. The pre-entry minimum low is logged as an **unapproved descriptive structural-low candidate** and candidate stop location. There is no executable Ekalayava SL, exit, win/loss, or realized P&L.
- New JSONL paper journal rows are append-only and deduplicated by stable record IDs. They include contract identity, entry cause, levels, status, MFE/MAE, target-touch time, structural observations, data quality, and paper-only flags.
- The Groww-side callback now requires the stateful engine and a finalized candle; the prior stateless signal shortcut was removed.

## Contract-selection verification

Unit tests verify exact CE/PE ITM2/ITM3 selection, rejection of missing exact ranks, rejection of mismatched symbol expiry labels, and daily expiry rollover. The existing catalog-first selection artifact independently shows the Jan 6 expiry-day chain and next-day rollover:

| Trading date | Selected expiry | CE ITM2 | CE ITM3 | PE ITM2 | PE ITM3 |
|---|---|---|---|---|---|
| 2026-01-06 | 2026-01-06 | 26100 | 26050 | 26250 | 26300 |
| 2026-01-07 | 2026-01-13 | 26050 | 26000 | 26200 | 26250 |

The live selector’s tests use the same catalog ladder method as historical selection. A missing exact strike is reported unavailable; no rank or expiry is substituted.

## Historical replay evidence

Each selected option day below had **75/75** regular-session bars (09:15–15:25 IST) in the existing local assembled dataset. Replay fed one bar at a time and did not pass future rows into the engine. Baseline values are from the stored `final_baseline.json`; no full-period backtest was rerun.

### Level-to-Level

| Date | Contract | Stored baseline | Replay entry | Replay outcome / exit | Comparison |
|---|---|---|---|---|---|
| 2026-01-01 | CE ITM2 26100 | 09:25, SL 138.80 / target 167.20; SL 09:30 | 09:25 | SL 09:30 | Entry, levels, outcome, exit, MFE +2.45 and MAE −13.30 match |
| 2026-01-01 | CE ITM3 26050 | 09:25, SL 174.10 / target 206.25; SL 09:30 | 09:25 | SL 09:30 | Entry, levels, outcome, exit, MFE +3.30 and MAE −14.40 match |
| 2026-01-01 | PE ITM2 26250 | 09:55, SL 102.90 / target 126.50; target 10:00 | 09:55 | TARGET 10:00 | Entry, levels, outcome, exit, MFE +2.80 and MAE −10.65 match |
| 2026-01-02 | PE ITM2 26250 | 09:30; skipped because entry close was already below SL 87.45 | 09:30 | `SKIPPED_SL_ALREADY_BREACHED` | Entry and levels match; no trade lifecycle or P&L |
| 2026-01-22 | CE ITM3 25200 | 10:30, SL 204.60 / target 234.65; ambiguous 10:35 | 10:30 | AMBIGUOUS 10:35 | Entry, levels, ambiguity, exit timestamp, MFE +15.00 and MAE −19.50 match |
| 2026-01-01 | PE ITM3 26300 | No stored setup | — | No signal in replay | 75 bars processed; zero paper signals |

The first-green rule, multiple-candle continuation, SL, target, same-candle ambiguity, skipped-entry behavior, and no-setup behavior are also covered by synthetic unit tests.

### Ekalayava observation

| Date | Contract | Baseline/replay entry | Opening-high observation | MFE / MAE | Structural-low candidate | Lifecycle |
|---|---|---|---|---:|---:|---|
| 2026-01-01 | CE ITM2 26100 | 09:50 / 09:50 | No touch | +1.65 / −43.80 | 127.40 | Unresolved at session end |
| 2026-01-02 | PE ITM2 26250 | 14:35 / 14:35 | No touch | +2.40 / −14.30 | 39.70 | Unresolved at session end |
| 2026-01-05 | CE ITM3 26200 | 09:50 / 09:50 | Touched 10:20 / 10:20 | +62.85 / −78.55 | 105.90 | Unresolved at session end |

Entry timestamp/price, target-touch observation, MFE/MAE, and candidate-low measurement matched stored baseline events. Ekalayava replay labels the closing observation `UNRESOLVED_AT_SESSION_END`; the historical event used `OPEN`. This is a status-label difference only: both mean no defined exit or realized result. The target touch did not become a win or P&L.

## No-lookahead and recovery checks

- Prefix replay through the red breakdown produces no L2L entry; adding the first subsequent completed green candle produces the signal at that candle’s close. A replay of the full day produces the same entry timestamp, so later candles do not move the signal backward.
- Ekalayava tests expose swing highs only from the current completed bar and its preceding two highs. The breakout can occur only on a later completed candle; no future candle confirms an earlier swing.
- Duplicate completed candles do not repeat events. Out-of-order bars fail closed. Gaps are recorded without creating candles and disable new entries for that contract-day. State restore preserves the last processed bar and strategy parameters; mismatched configuration is rejected.
- The selected historical replay days were complete. Partial-day behavior was checked with synthetic gap cases, not with a new market-data download.

## Readiness checklist

| Component | Status | Evidence / remaining condition |
|---|---|---|
| Contract selection | PASS (selector component) | Exact daily expiry/strike tests, rollover, expiry-label validation, and no-substitution test; live data-feed wiring remains separate |
| Completed 5-minute candle builder | PASS (component) | Close-boundary, duplicate/late/out-of-order tick, gap, session-time, and snapshot/restore tests |
| L2L state machine | PASS (component/replay) | Red-break → first subsequent green; selected replay matches stored entries and outcomes |
| L2L SL/target | PASS (component/replay) | Existing 4-point buffer, Opening High target, SL, target, ambiguity, and skipped cases match |
| Ekalayava entry | PASS (component/replay) | Existing causal swing-high breakout; representative entries match |
| Ekalayava structural-SL observation | PASS (observation only) | Candidate low and revisit evidence recorded; not promoted to an executable stop |
| Paper journal | PASS (component) | Append-only JSONL records, stable IDs, duplicate suppression, required fields |
| Duplicate-entry protection | PASS (component) | One entry per strategy/contract/day; repeated candles/restarts do not duplicate |
| No-lookahead | PASS (tested behavior) | Prefix replay and causal swing tests |
| Reconnect/restart | BLOCKED for live readiness | Builder/engine snapshots restore state; no connected Groww stream/reconnect orchestration was run or validated |
| Error handling | BLOCKED for live readiness | Malformed inputs fail closed and polling errors are surfaced; end-to-end timeout/disconnect recovery is not validated |
| Market hours | BLOCKED for live readiness | Candle-time bounds and L2L/Ekalayava entry windows are enforced; no NSE holiday/special-session calendar is wired into the listener |
| Paper-only lock | PASS | Runtime flags checked; execution lock remains fail-closed; source scan found no order placement/modification/cancellation calls |
| Historical replay | PASS for selected evidence | Eight signal examples plus one no-setup contract-day replayed; selected contract-days each had 75/75 bars |
| Test coverage | PASS | Full test suite: **76 passed** |

## Readiness and remaining blockers

- **L2L: NOT READY for controlled live paper observation.** The state machine and selected-date replay pass, but no end-to-end Groww read-only feed coordinator currently carries the NIFTY opening candle into the daily selector, subscribes/builds the four exact option streams, persists all four engines, and handles feed recovery. The NSE holiday/special-session calendar is also not integrated.
- **Ekalayava: OBSERVATION-ONLY.** Its causal entry and post-entry observation components work in replay. It has no approved executable structural stop or complete exit lifecycle; therefore it cannot produce valid realized P&L or be marked controlled-paper-ready. Live stream wiring is also outstanding.
- The historical sample remains incomplete: the prior Jan–Sep handoff records 178/740 option slots missing or unselectable, 112 fully usable / 55 partial / 18 unusable days, and no Sep 30 underlying feed. This task did not download data or rerun those experiments.
- No live process was started, no credentials were printed or added, and no order API was used.

**Exact next step:** implement a read-only Groww observer coordinator with a verified NSE trading calendar; prove daily 09:15 underlying capture, exact contract rollover, four option candle streams, reconnect/restart, and journal recovery in replay or a controlled dry run. Keep orders absent/disabled. Obtain an explicit versioned Ekalayava structural anchor/buffer and lifecycle decision before any Ekalayava P&L comparison or paper trade.
