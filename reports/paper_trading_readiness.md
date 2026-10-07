# Paper-Trading Readiness Audit — Jan–Sep 2026

**Audit date:** 2026-10-07. No live polling loop was started; no broker order endpoint was called. Current flags remain `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`.

## Readiness decision

| Strategy | Status | Basis |
|---|---|---|
| Level-to-Level | **NOT READY** | 178/740 expected option slots are missing/unselectable; Sep OOS lacks Sep 30 and many exact contracts. The live-listener signal is stateless and does not implement the canonical preceding-red then first-subsequent-green sequence. It may evaluate a still-forming 5-minute bucket. |
| Ekalayava | **OBSERVATION-ONLY** | Structural stop anchor/buffer and complete exit lifecycle are unresolved. Target touches are observations, not exits, wins, or realized P&L. Live listener has no Ekalayava signal/journal path. |

No strategy is marked “profitable” or authorized for continuous live paper execution by this historical sample.

## Historical evidence

The corrected date-specific selector used Groww expiry catalogs and exact CE/PE ITM2/ITM3 symbols. It resolved 562 contract-days with candles, of which 561 are complete and one partial; 174 exact catalog slots remain unavailable, and four Sep 30 slots lack an underlying open. Overall option-candle availability is 42,149/55,500 (75.9%). September OOS is only observed through Sep 29 (33/84 option slots complete).

Canonical L2L at the 4-point default produced 361 setups; 203 resolved (58 target,145 SL), 157 skipped, one ambiguous, and +234.85 gross premium points before costs/sizing. Results varied by month and are concentrated in several days. Ekalayava produced 253 entries and 109 opening-high touches, but all 253 entries remain lifecycle-unresolved. This does not establish performance or readiness.

## Existing deterministic/paper components

- `app/config.py` fails closed if `EXECUTION_ALLOWED` is true or `PAPER_ONLY` is false. Current loaded values are false/true.
- `app/safety.py` enforces paper mode. `app/paper.py` contains deterministic historical/paper calculations.
- `app/groww_data.py` exposes read-only candles, quotes, and LTP. Application source contains no order-placement, modification, or cancellation call; safety tests guard this.
- `app/live_listener.completed_5m_candle` groups ticks by five-minute bucket but returns the latest bucket without proving it has closed.
- `app/live_listener.paper_signal` tests only the current candle’s low below Opening Low and green close. It does not maintain the canonical prior-red/first-subsequent-green state or deduplicate entries.
- The listener does not integrate the daily expiry/contract selector, a complete paper lifecycle, or Ekalayava.
- `app/journal.py` omits required contract identity, expiry/strike/rank, NIFTY reference price, Ekalayava reversal structure, target-touch time, and data-quality fields.
- The live listener does not call an LLM per candle; LLM code is confined to research-agent workflows.

## Ekalayava structural stop status

The project currently has **no executable structural SL definition**. This run records a descriptive low candidate (minimum premium low from the opening-low breakdown through the completed entry candle) and whether later price revisited it. This measurement is not the approved structural anchor and is not fed to exit simulation or paper orders. The owner must specify the anchor candle/low, numeric buffer, and trigger convention, and resolve target-touch exit, same-candle ambiguity, opposite signal, EOD, expiry, and end-of-data handling. Until then Ekalayava is observation-only.

## Work required before controlled paper observation

1. Recover authoritative listing data for missing exact historical slots where Groww can provide it; retry Sep 30 underlying from Groww. Keep irrecoverable slots missing and never substitute.
2. Version the Ekalayava structural SL and lifecycle decisions before any paper trade or P&L comparison.
3. Make the live builder emit only completed 5-minute candles; implement/test the stateful L2L rule and daily exact contract/expiry selection; add duplicate-signal suppression and required journal fields.
4. Begin a supervised, non-continuous paper observation only after these gates pass. Keep broker execution code absent and hard-disabled.

## Safety audit

- `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`.
- No broker order endpoint was called.
- Application scan found no order placement/modification/cancellation calls.
- `.env`, `secrets.txt`, and credential/token/key files are ignored and untracked; no credential values appear in reports or staged changes.
- No continuous market-hour process was started.

**Final status:** L2L **NOT READY**; Ekalayava **OBSERVATION-ONLY**.
