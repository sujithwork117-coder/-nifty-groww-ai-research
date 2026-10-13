# Ekalayava Final Rule Specification and Approval State

## Status

**Canonical entry: preserved. Canonical exit: unresolved. Experimental exit
policy: none approved.** This document is a deterministic account of the
existing entry and the research simulator conventions, not authorization to
trade or an adopted production lifecycle. No exit code was wired into the
paper engine.

## Canonical entry rules

The entry analyzer in `app/strategies.py` is the unchanged baseline:

1. Process completed five-minute option candles in timestamp order.
2. Set the Opening High and Opening Low from the first completed five-minute
   candle of the session.
3. Require the premium to break below the Opening Low.
4. After the breakdown, identify a recovery/reversal structure using only
   information available by the current candle. The existing detector uses
   its causal left-two/right-zero swing-high logic.
5. Enter at the completed candle close when price breaks above the eligible
   swing high before reaching the Opening High. As permitted by the existing
   rule, the entry close itself may remain below the Opening High.
6. Do not use future candles to qualify the entry. Contract selection is
   exact-symbol/catalog based; do not substitute a neighboring strike or
   expiry when a path is missing.

This research does not change, optimize, or weaken entry eligibility.

## Experimental exits compared (not approved)

Definitions use entry price `E`, causal structure trough `L`, Opening High
`H`, buffer `b`, and initial risk `R = E - S`. Each initial stop is
`S = L - b`; any non-positive risk is invalid and must not be traded.

| Version | Initial stop | Initial target | Post-entry adjustment |
|---|---|---|---|
| `A_B4_TP25_V1` | `L − 4` | `E + 25` premium points | None |
| `A_B4_OPENING_HIGH_V1` | `L − 4` | `H` | None |
| `B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1` | `L − 2` | `H` | Proxy trail: after a completed bar, prior-two-bar lower-low minus 2; applies from the next bar |
| `C_B2_1R_V1` | `L − 2` | `E + 1R` | None |
| `C_B2_1_5R_V1` | `L − 2` | `E + 1.5R` | None |
| `C_B2_2R_V1` | `L − 2` | `E + 2R` | None |

Archived `A_STRUCTURAL_TROUGH_B4_TP25` is a different policy: its target is
`E + 0.25 * (H - E)`, not a fixed 25-point gain. It was independently replayed
as an archived policy and must not be conflated with `A_B4_TP25_V1`.

## Research simulator lifecycle

The existing research simulator applies the following deterministic
conventions to these candidates:

* Start stop/target monitoring on the candle after the completed entry candle.
* If a bar opens through the stop, model the stop exit at the open. A gap
  through the target is modeled at the target price.
* If both stop and target are touched in one five-minute bar and their order
  cannot be known, classify the result as ambiguous, not as whichever outcome
  is favorable.
* Do not interpolate absent candles. Incomplete/missing paths remain partial
  or unresolved and must not be converted to wins, losses, or no-signal days.
* No partial exit is simulated.
* The last available session close is used for an experimental
  end-of-session outcome in the candidate comparison. This is not an
  established canonical time exit.
* A trailing stop update is based only on a completed bar and is active on
  the following bar. Never widen the stop to avoid realizing a loss.
* No transaction costs, spread or slippage are estimated absent reliable
  inputs; all reported points are gross and not net returns.

## Approval and operating constraints

No formula above is selected for operational use. The validation-selected
`C_B2_2R_V1` failed to show cross-period stability: −258.20 training points,
+75.85 validation points, +172.70 untouched 2025 test points, and −71.30
across seven exact 2026 paths. The sample and missing data do not support a
reliable winner.

Live order execution remains disabled (`EXECUTION_ALLOWED=False`);
paper-only mode remains enabled (`PAPER_ONLY=True`). No order was submitted,
modified or cancelled. Any future paper-observation approval must be explicit,
separate, and must preserve the existing duplicate-signal, logging,
authentication and kill-switch safeguards.
