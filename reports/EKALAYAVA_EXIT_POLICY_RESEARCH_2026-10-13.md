# Ekalayava Exit-Policy Research — 2026-10-13

> **Follow-up:** This is the earlier local-data snapshot. Its 2025 coverage
> statements were superseded by the bounded Groww retrieval and exact-path
> replay documented in
> [EKALAYAVA_HISTORICAL_DATA_COVERAGE_JUL_DEC_2025.md](./EKALAYAVA_HISTORICAL_DATA_COVERAGE_JUL_DEC_2025.md)
> and [EKALAYAVA_MULTI_PERIOD_EXIT_VALIDATION.md](./EKALAYAVA_MULTI_PERIOD_EXIT_VALIDATION.md).
> The final no-policy-approved decision is in
> [EKALAYAVA_FINAL_SL_TARGET_DECISION.md](./EKALAYAVA_FINAL_SL_TARGET_DECISION.md).

## Decision

**No experimental stop/target policy is selected or approved. Keep the canonical
Ekalayava entry rules unchanged and its canonical exit lifecycle unresolved.**
The archived 253-entry policy summaries are informative but cannot be
independently replayed from the timestamped candle paths currently in this
workspace. Only seven exact-contract entry paths could be reconstructed
locally: six from the July–August validation period and one from the incomplete
September period. The separate, read-only October 13 trace is one trade, not
validation evidence.

No broker order was submitted, modified, or cancelled. Execution remains
disabled, paper-only remains enabled, and the live-order pathway was not used.
Gross premium points below are not net profitability; spread, slippage,
brokerage, taxes, and other costs are unavailable.

## Evidence reviewed

Reviewed the current guide, canonical entry/exit research, saved observations
and policy ledgers, archived candidate-selection report, existing simulator
and tests, and the October 13 partial-session replay. Key inputs:

* `Current_guide_5.md`
* `reports/multi_year_ekalayava_observations.csv` (253 entry observations)
* `reports/ekalayava_exit_policy_trades.csv` (9,361 saved policy outcomes)
* `reports/ekalayava_exit_policy_summary.csv`
* `reports/ekalayava_exit_candidate_selection.json`
* `reports/ekalayava_final_validation.md`
* `reports/TODAY_FULL_SESSION_L2L_EKALAYAVA_REPLAY_2026-10-13.md`
* `app/research_ekalayava_exits.py`
* `tests/test_research_ekalayava_exits.py`

The existing replay simulator monitors only after the completed entry candle;
uses the candle open for a gap through a stop and the target price for a target
gap; classifies a same-candle stop/target touch as ambiguous; does not
interpolate missing bars; and updates the existing lower-low trailing proxy
after a completed bar for use on the next bar.

## Candle-path coverage

The 253 observations and saved policy outcomes are not a substitute for
timestamped post-entry candles. The policy ledger records outcomes and
aggregate measures, but its candle-count metadata does not provide the
entry-by-entry OHLC path needed to independently replay a new policy.

An exact-symbol search across the local raw, derived, and run option CSVs found
69 unique option-contract files. Only **7 of 253 observations (2.8%)** had a
local file for the exact symbol: six July–August validation observations and
one September observation. No January–June training entry had a matching local
contract file. The seven available paths were joined on the exact option
symbol/expiry and entry timestamp, checked for duplicate timestamps and
five-minute interval continuity, and replayed without joining a different
contract. The local validation subset is therefore only 6 of 47 entries and
must not be treated as representative.

No unavailable historical data was downloaded or backfilled. Six observations
in the validation set and all 191 training entries remain without locally
replayable exact-contract paths. September is incomplete and its one local
entry is not a holdout validation result.

## Frozen candidate definitions

These five candidates were fixed for the new local-path replay. This was not a
blinded or prospective preregistration: the archived summary results had
already been reviewed. No grid search was run.

| Candidate | Experimental rule |
|---|---|
| `A_B4_TP25_V1` | Structural trough minus 4 premium points; fixed target = entry + 25 points. |
| `A_B4_OPENING_HIGH_V1` | Structural trough minus 4 points; target = Opening High. |
| `B_B2_CAUSAL_TRAIL_OPENING_HIGH_V1` | Structural trough minus 2 points; Opening High target; existing lower-low trailing proxy with a 2-point buffer. |
| `C_B2_1R_V1` | Structural trough minus 2 points; risk = entry − initial stop; target = entry + 1R. |
| `C_B2_2R_V1` | Same initial stop; target = entry + 2R. |

For all families, an invalid stop at or above entry is excluded by the
simulator. In the reward-to-risk candidates, risk must be positive; the target
is calculated from that same risk distance. Outcomes and assumed fills are
hypothetical, based on completed five-minute OHLC candles, not guaranteed
executions.

**Family B remains a proxy, not the requested confirmed-swing-low policy.**
The existing tested rule tightens after a completed candle makes a low below
both of the prior two completed lows; its stop is that low minus 2 points,
never loosens, and becomes active on the next candle. This is causal and
covered by the existing trailing test, but it does not wait for subsequent
right-side candles to confirm a pivot swing low. It must not be represented as
validation of a newly confirmed structural-swing trailing policy. A strict
confirmed-swing rule was not added without the required evidence and tests.

The prior `B_BREAKOUT_CANDLE_B2_TP100_OPENING_HIGH` experiment is not
comparable to these candidates: it uses a different stop anchor. Its large
gross result is not evidence for a structural-stop policy.

## Archived training and validation results

These are values reproduced from the **saved summary CSV**, not freshly
reconstructed results. The source paths for most entries are unavailable in
this workspace, so they are not independent confirmation. Each candidate had
47 archived validation entries and 191 archived training entries; archived
unresolved and ambiguous counts were zero.

| Candidate / archived policy | Period | Targets / stops / EOD | Gross points | Max drawdown | Longest losing streak |
|---|---|---:|---:|---:|---:|
| A B4 + 25 (`A_STRUCTURAL_TROUGH_B4_TP25`) | Train, n=191 | 118 / 73 / 0 | −212.31 | 600.58 | 9 |
| | Validation, n=47 | 29 / 16 / 2 | −72.25 | 249.84 | 7 |
| A B4 + Opening High (`A_STRUCTURAL_TROUGH_B4_TP100_OPENING_HIGH`) | Train, n=191 | 70 / 108 / 13 | +793.70 | 601.15 | 23 |
| | Validation, n=47 | 19 / 21 / 7 | +192.15 | 244.90 | 8 |
| B2 lower-low trailing proxy (`TRAIL_CAUSAL_LOWER_LOW_B2_TP100`) | Train, n=191 | 45 / 144 / 2 | +143.55 | 542.95 | 17 |
| | Validation, n=47 | 11 / 36 / 0 | +19.40 | 198.35 | 8 |
| C B2 + 1R / 2R | Train / validation | Not in saved policy ledger | Not available | Not available | Not available |

The archived A B4 + Opening High policy has the largest saved validation gross
and positive average gross result per eligible validation entry (+4.09 points,
versus −1.54 for A B4 + 25 and +0.41 for the trailing proxy). It also has lower
validation drawdown than A B4 + 25, but higher drawdown than the trailing
proxy; its eight-trade losing streak matches the trailing proxy and exceeds
A B4 + 25. Its training drawdown and losing streak were 601.15 points and 23,
and validation gross fell substantially from +793.70 to +192.15. These mixed
results, plus missing source paths and costs, do **not** justify selection.

The saved incomplete-September summaries are further warning evidence, not
validation: the trailing proxy recorded −83.90 gross across 15 observations
(13 stops, one target, one EOD), while the coverage itself is incomplete.

## New exact-path subset replay

The seven available local paths were replayed through the existing simulator
for the five fixed candidates. The six July–August rows are a sparse slice of
the validation period; the September row is shown separately. In that six-row
slice, target/stop counts, gross points, drawdown, and losing streak were:

| Candidate | Validation subset n=6: targets / stops | Gross points | Max drawdown | Longest losing streak |
|---|---:|---:|---:|---:|
| A B4 + 25 | 3 / 3 | −52.10 | 127.10 | 3 |
| A B4 + Opening High | 5 / 1 | +117.95 | 31.80 | 1 |
| B2 trailing proxy | 2 / 4 | +10.80 | 15.75 | 1 |
| C B2 + 1R | 3 / 3 | −53.00 | 121.10 | 3 |
| C B2 + 2R | 2 / 4 | −49.40 | 121.10 | 3 |

The single incomplete-September local row was a stop for every candidate
(A policies: −23.90 points each; B proxy: −12.35; C 1R: −21.90; C 2R: −21.90).
These seven paths are too few and too availability-selected to support a
candidate ranking. The complete row-by-row inputs, assumptions, outcomes, and
exit timestamps are in
`reports/ekalayava_exit_policy_entry_traces_2026-10-13.csv`.

## October 13 PE ITM3 single-entry trace

The earlier partial-session report records the exact instrument
`NSE-NIFTY-13Oct26-22500-PE`, a 10:25 IST entry observation at 43.55, structural
trough 26.15, Opening High 216.05, and MFE/MAE through 13:45 of +22.65/−34.25.
Those earlier excursion figures are not used as realized results.

After checking the paper-only safety flags, one bounded read-only Groww request
retrieved this exact contract from 10:25 through 14:25 IST. It returned 49 raw
rows; the unfinished final row was excluded, leaving 48 completed candles
through 14:20, with no duplicate timestamps and monotonic order. The returned
candles were not persisted. Each hypothetical outcome below occurred before
12:15, so the recorded exit is supported by the fetched path; no claim is made
about unobserved later candles.

| Candidate | Stop / target | Counterfactual result |
|---|---|---|
| A B4 + 25 | 22.15 / 68.55 | Stop at 12:15, −21.40 points. |
| A B4 + Opening High | 22.15 / 216.05 | Stop at 12:15, −21.40 points. |
| B2 trailing proxy | 24.15 initial / 216.05 | Stop at 11:30 at the tightened 42.45 stop, −1.10 points; tightenings at 10:45 and 11:20. |
| C B2 + 1R | 24.15 / 62.95 | Target at 10:35, +19.40 points. |
| C B2 + 2R | 24.15 / 82.35 | Stop at 12:15, −19.40 points. |

The example demonstrates how outcomes diverge across rules; it does not
establish which rule generalizes. In particular, C 1R's one-trade target is
not a reason to select it. The candidate outcomes are recorded in the two new
CSV files alongside the local exact-path replays.

## Costs, caveats, and tests

* No spread, slippage, brokerage, taxes, or other defensible cost assumptions
  are available. All reported points are gross; net performance is unverified.
* Five-minute high/low touches do not prove actual limit-order fills.
* Historical policy results cannot be recreated for 246 exact-contract
  observations with current local files. The six-entry local validation slice
  is not representative.
* Family B's existing lower-low proxy does not implement a confirmed pivot
  swing-low rule. The C-family candidates have only the six-entry local
  validation slice and no archived training/validation comparison.
* Existing focused exit-simulator tests cover target-before-later-stop,
  same-bar ambiguity, stop gaps, missing intervals, session-end close,
  next-bar trailing activation, and invalid stops. They do not cover every
  Guide 5 test item (including target gaps, duplicate policy/setup identity,
  strict confirmed-pivot logic, or all reward-to-risk calculations); no new
  simulator behavior was added.

Focused test command and result:

```text
pytest -q tests/test_research_ekalayava_exits.py
7 passed
```

The related paper-engine, observer, contract, data, safety, and exit-simulator
suite was also run:

```text
pytest -q tests/test_live_listener.py tests/test_paper_replay.py tests/test_paper_observer.py tests/test_paper_backtest.py tests/test_paper_engine.py tests/test_contract_selection.py tests/test_groww_data.py tests/test_nse_calendar.py tests/test_journal.py tests/test_safety_audit.py tests/test_safety.py tests/test_research_ekalayava_exits.py
59 passed in 1.33s
```

## Recommendation and next step

**No candidate merits further paper-policy evaluation or adoption yet.** The
archived A B4 + Opening High candidate is the saved validation gross leader,
but it has meaningful drawdown, an extended training losing streak, incomplete
reproducibility, and unmeasured costs. No saved data evaluates the two R
targets over the required training/validation universe. The existing trailing
proxy is not the strict swing-confirmed Family B rule.

The single recommended next research step is to **recover or locate the exact
timestamped option-candle paths for the existing 253 entry observations,
starting with all 47 July–August validation entries and their exact contract
expiries, using already available local/archive sources only**. Do not broaden
the parameter set or backfill unavailable history. If those source paths
cannot be recovered, keep the exit lifecycle unresolved rather than selecting
from the archived aggregates or the small available subset.
