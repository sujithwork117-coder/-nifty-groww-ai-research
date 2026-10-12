# Paper-Trading Readiness — Finalization Audit

**Audit date:** 2026-10-08. This was a code/report review plus local unit tests. No Groww request, market polling, continuous observer, or order endpoint was used.

## Decision

| Strategy | Status | Reason |
|---|---|---|
| Level-to-Level | **NOT READY for live paper observation** | Completed-candle builder, stateful contract-day engine, exact selector primitive, journaling, and replay tests exist. The end-to-end Groww coordinator, exchange calendar, multi-symbol stream handling, durable session orchestration, and real reconnect/recovery validation are not wired. |
| Ekalayava | **READY FOR OBSERVATION ONLY** | Entry/target observations are causal and stateful. No numeric structural-stop buffer is justified or configured by default. The proposed stop lifecycle is an opt-in research parameter, not yet a versioned canonical strategy rule. |

Neither status means real-money trading readiness. The system must remain `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`.

## Requirements audit

| Requirement | Current implementation/evidence | Status |
|---|---|---|
| Market session | `market_open_now` limits observation to weekday 09:15–15:30 Asia/Kolkata; does not include NSE holiday or special-session calendar. | Partial |
| Opening 09:15 NIFTY candle | Builder emits only after close; contract selection requires the completed 09:15 underlying bar and uses its open. No coordinator guarantees that capture. | Component ready; orchestration missing |
| Expiry and exact CE/PE ITM2/ITM3 | Read-only selector chooses earliest non-expired Groww expiry and exact observed-ladder strikes. Missing ranks remain missing; no silent rank/expiry substitution. | Component ready; orchestration missing |
| Completed 5-minute enforcement | Builder waits for the 5-minute close boundary. `PaperContractEngine` and listener facade reject unproven candles and out-of-order timestamps. | Implemented and unit-tested |
| Canonical L2L sequence | Stateful red breakdown → first later completed green → close entry; one signal per contract-day; stop/target checked on later candles. Entry at/above target is now skipped. | Implemented in paper engine; historical and unit-tested |
| Ekalayava entry | Causal left=2/right=0 swing-high state; entry on later completed breakout candle close before target. Structural trough is frozen before the breakout candle. | Implemented in paper engine; unit-tested |
| Ekalayava SL and target | `EKALAYAVA_SL_BUFFER_POINTS` is optional and unset by default. If set, stop is pre-breakout reversal trough minus that buffer; target is Opening High; later bar touches are checked, same-bar conflict is ambiguous. Without it, the trade remains observation-only. | Optional research lifecycle only; canonical approval pending |
| Trade journal | JSONL schema records date/time, strategy, exact contract identity, NIFTY reference, entry, structural anchor/price/buffer, swing and breakout, SL/target, exit/outcome, holding time, MFE/MAE, data-quality state, execution-disabled and paper-only flags. | Implemented and unit-tested |
| Duplicate prevention / restart | Daily signal state, stable record IDs, state snapshots and config-signature validation. | Component tested |
| Gaps and reconnect | Gaps invalidate new entries and mark open lifecycle data unresolved; read-only observer callback can report errors. There is no complete network reconnect coordinator proving safe resumption across all symbols. | Partial; integration blocker |
| Logging / kill switch / no order route | Append-only JSONL event log and `ExecutionLock`; source and safety tests show no Groww order placement/modification/cancellation functionality. | Paper-only controls present |

## Data readiness limits

The existing Jan–Sep dataset is not complete enough for full-universe conclusions: 185 sessions, 184 with underlying bars; options have 561 complete, 1 partial, and 178 missing/unselectable contract-days (42,149/55,500 expected bars; 75.9%). Missing exact contracts may suppress signals. This does not block code-level paper observation, but it limits historical validation and requires each live contract-day to be gated on its own data quality.

## Required blockers before a controlled paper session

1. Wire a read-only coordinator from completed NIFTY open → exact expiry/contract selection → four completed 5-minute option streams → per-contract engines → durable journal/state.
2. Add an exchange holiday/special-session calendar and explicit session-close handling.
3. Validate network reconnect, late/duplicate ticks, gaps, restart recovery, and exact-symbol resubscription end-to-end in a supervised dry run.
4. Before Ekalayava paper SL/target lifecycle is considered canonical, version the anchor, choose/approve a buffer or no-buffer rule, and resolve opposite signal, EOD, expiry, and end-of-data handling. Until then leave the buffer unset and record observations only.

## Safety verification

- Configuration hard-fails if `EXECUTION_ALLOWED=true` or `PAPER_ONLY=false`; repository test asserts the defaults.
- Current configured flags were inspected as booleans only; no credential values were read or printed.
- No API keys, tokens, `.env`, `secrets.txt`, or market credentials are included in report artifacts or code changes.
- No Groww orders were placed; the application has no order-placement/modification/cancellation route.
- No continuous market observer was started.

Research evidence: [`l2l_final_validation.md`](l2l_final_validation.md) and [`EKALAYAVA_FINAL_RESEARCH.md`](EKALAYAVA_FINAL_RESEARCH.md).
