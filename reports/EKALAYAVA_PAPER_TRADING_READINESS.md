# Ekalayava Paper-Trading Readiness

## Status: not ready to activate an exit policy

**No experimental stop/target policy is approved.** Keep canonical entry
behavior unchanged; do not connect any candidate exit lifecycle to the
paper engine. `EXECUTION_ALLOWED=False` and `PAPER_ONLY=True` remain required.
No live, paper, or broker orders are submitted by this research workflow.

The B2 lower-low proxy is audited as the previous gross leader, not the
current combined-gross leader, and is not a validated net-profit policy.
`A_B4_OPENING_HIGH_V1` now leads descriptively at +685.55 gross points; its
2025 training and validation results were negative, so it is not approved.
The B2 exact stop and target counts, path-level replays, period performance
and hypothetical transaction-cost scenarios are reported in
`EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md`. Its lower-low rule is not a
confirmed structural swing-low rule.

## Why activation is blocked

* The candidate comparisons and 2025 test have already been examined; the
  results are retrospective and cannot serve as a fresh selection holdout.
* Even with exact recovered candles, fills are approximated from OHLC. Actual
  bid/ask spreads, queue position, slippage, brokerage, taxes and executable
  contract multipliers are not reliably available in the historical files.
* The research does not prove stable net expectancy across independent
  periods, and the cost threshold for positive gross performance is not a
  measured transaction-cost estimate.
* No selected deterministic exit is synchronized with the paper engine.

## Supervised paper-observation plan (observation only)

Collect a consecutive, predeclared sample of at least 100 qualifying signals
over at least 60 trading sessions, whichever takes longer. This is a minimum
observation horizon to prevent stopping when the first results look favorable;
it is not a statistical guarantee, approval threshold, or authorization to
trade. Do not discard losing, incomplete, or inconvenient observations.
Capture quotes/fills and explicit costs only in a supervised paper environment.

For every observed signal, record:

| Field | Required observation |
|---|---|
| Identity | Date, canonical setup ID, exact option symbol, expiry, strike, CE/PE and ITM rank |
| Entry context | Entry timestamp, entry price, first-candle Opening High/Low, breakdown time, causal swing-high time/price, structural trough |
| Candidate snapshot | Candidate name/version, initial stop, target, formula and predeclared assumptions; store as diagnostics only |
| Path | Every completed five-minute timestamp and OHLC from entry through the observed terminal point; mark gaps and duplicates |
| Management | Each stop update, source candle, computed stop, and the first candle on which it is eligible to act |
| Execution evidence | Bid/ask or executable paper quote, simulated fill, spread, slippage, brokerage/tax inputs and source |
| Terminal outcome | Exit timestamp, observed price, exit reason, whether a target was touched while open or only after exit |
| Integrity | Exact-contract validation, missing intervals, ambiguous OHLC ordering, source and retrieval timestamp |

Before any future candidate selection, freeze its formula, selection process,
cost model and evaluation criteria. Keep the existing canonical entry and
paper-engine safety controls unchanged. A paper observation records evidence;
it does not activate the candidate's stop or target.

## Safety and code boundary

Research simulators remain separate from the paper engine. Experimental exit
configuration remains disabled unless separately and explicitly authorized
after a new evidence review. Do not enable live execution, place/modify/cancel
orders, weaken authentication or duplicate-signal protection, or use an empty
account balance as a safety control.
