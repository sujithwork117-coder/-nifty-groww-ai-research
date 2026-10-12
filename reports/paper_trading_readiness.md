# Paper-Trading Readiness — Observer Integration Audit

**Updated:** 2026-10-12. This report records code inspection and local automated tests. No Groww request, market polling, historical-data download, continuous observer, or order endpoint was used for this update.

## Decision

| Strategy | Status | Scope |
|---|---|---|
| Level-to-Level | **READY FOR LIVE PAPER OBSERVATION** | Read-only, paper-only observer wiring and deterministic recovery tests are implemented. The first supervised session should confirm the configured Groww account’s read-only candle access and data quality. This is not real-money readiness. |
| Ekalayava | **READY FOR OBSERVATION ONLY** | Entries and post-entry observations are journaled; lifecycle remains unresolved by canonical specification. Optional candidate stop simulation requires explicit buffer and experimental opt-in. |

Safety remains `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`. No real order path is present.

## Implemented observer path

`GrowwPaperObserver` coordinates the completed NIFTY 09:15 bar, the existing exact catalog-first daily selector, and the exact CE/PE ITM2/ITM3 symbols. It retrieves only same-session 5-minute candles and sends bars to per-contract-day `PaperContractEngine` instances only after their five-minute close boundary.

The observer persists engine state and an append-only, ID-deduplicated paper journal; the operator-safe health snapshot contains observer health, exact selected contracts, recent signals, last completed bars, paper-position summaries, skipped contracts, data-gap status, and safety flags. Restarted polling skips bars already processed. Missing candles invalidate new entries through engine gap handling; missing exact contracts are reported without adjacent-strike substitution. Transient API errors are sanitized and retried with bounded backoff; an injected client factory supports read-only reconnect. The observer is not started on import and was not started in this task.

Market hours use a fail-closed 2026 NSE calendar. It includes listed 2026 holidays and the published Feb 1 Budget session. Unknown years and the Nov 8 special session with unpublished timings fail closed. The calendar must be reviewed when official holiday or special-session notices change.

## Strategy boundaries

- **L2L:** Completed opening candle → completed red close below Opening Low → first later completed green candle → entry at that green close. Stop and target retain the canonical four-point buffer and Opening High. Entry already at/above target is skipped. No timeout or forced session-end liquidation is introduced; open positions are reported as open at session end.
- **Ekalayava:** Canonical causal entry and Opening-High target observations remain. The pre-breakout reversal-sequence trough is a research candidate anchor only. The numeric buffer is unset by default, so no stop, resolved outcome, win/loss, or realized P&L is claimed. A candidate simulation is distinctly tagged and requires both an explicit nonnegative buffer and `EKALAYAVA_EXPERIMENTAL_EXIT_SIMULATION=true`; same-candle stop/target touches are ambiguous. No automatic EOD, expiry, opposite-signal, or end-of-data exit is invented.
- Each engine is scoped to an exact symbol and trading date. The observer selects the applicable expiry/strikes each session; positions are not carried to a different contract-day. A live interruption or detected gap leaves lifecycle unresolved and blocks new entries for that stream.

## Validation and remaining boundary

Focused tests cover exact selection, closed-bar enforcement, state/journal recovery, per-contract failure isolation, bounded reconnect, the official calendar entries, and experimental Ekalayava configuration. The complete repository test suite is run for this change; its result is recorded in `RESEARCH_STATE.md` and the delivery summary.

The code path is tested with a deterministic Groww-compatible fake, not against the live Groww service in this task. The first supervised paper-observation session remains an operational integration check for credentials, endpoint behavior, API rate limits, and actual stream completeness. Do not interpret paper signals as executable advice or Ekalayava target touches as exits.

Historical context remains unchanged: the corrected Jan–Sep dataset includes 185 expected sessions, 184 with underlying source data; 740 expected option contract-days, of which 561 are complete, 1 partial, and 178 missing/unselectable; option interval coverage is 42,149/55,500 (75.9%). L2L baseline remains 361 setups, 202 resolved (57 target/145 SL), 158 skipped, 1 ambiguous, +237.45 gross resolved premium points. Ekalayava remains 253 entries, 109 Opening-High touches (43.1%), and 253 unresolved canonical lifecycles. These historical results were not rerun.

## Safety verification

- Configuration rejects execution-enabled or non-paper-only settings.
- `.env`, `secrets.txt`, token/key patterns, and observer runtime state are ignored; no credential values are included in this report or source changes.
- Source audit confirms the application has no order placement, modification, or cancellation method calls.
- No orders were placed and no observer session was started.

Detailed evidence: [`l2l_final_validation.md`](l2l_final_validation.md), [`EKALAYAVA_FINAL_RESEARCH.md`](EKALAYAVA_FINAL_RESEARCH.md), and [`paper_engine_replay_validation.md`](paper_engine_replay_validation.md).
