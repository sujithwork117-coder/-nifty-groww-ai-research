# Ekalayava Specification and Implementation Audit

**Audit scope:** existing canonical strategy definition, implementation, backtest/exit handling, event schema, tests, and repository documentation. This audit used the existing code and the saved five-month baseline output only. No market data was downloaded, no strategy was rerun, and no strategy code or definition was changed.

## A. Canonical specification

Source of truth: `NIFTY_Strategy_Definitions_Level_to_Level_Ekalavya.md`, identified in that file as the canonical strategy-definition document. Sections 3.2, 6, 12, and 13 govern this audit.

| Element | What the canonical document says |
|---|---|
| Instrument/timeframe | NIFTY options; CE and PE; ITM2 and ITM3; completed 5-minute candles; Asia/Kolkata. Opening High/Low come from the first 5-minute candle. |
| Entry | Premium first moves below Opening Low, then reversal/recovery develops, a causal swing high forms, and a later completed candle confirms a break of that swing high. Enter at the completed candle close under the chosen causal breakout rule. Entry must be before the Opening High; do not wait for a close above the target. |
| Swing/reversal detail | Reversal is described qualitatively. The document requires an explicit causal swing rule and says to report the existing fixed-window rule before changing it; it does not prescribe a particular lookback or a numeric reversal test. |
| Stop-loss | **Undefined / requires a rule.** The document expressly prohibits inventing a fixed stop or assuming Opening Low, reversal low, or swing low is the stop. |
| Target | **Opening High.** |
| Exit | The document identifies Opening High as the target but does not define a complete trade-management/exit lifecycle beyond that target. It does not define an alternative exit when target is not hit. |
| Opposite signal | No Ekalayava opposite-signal exit or reversal rule is specified. |
| End of day | No forced close, session-end mark, or overnight carry rule is specified. |
| Expiry | No expiry-day exit or expiry settlement handling is specified as part of Ekalayava. Common guidance says to enumerate and label available expiries rather than silently invent a final expiry choice. |
| End of data | No rule specifies whether an unresolved position is closed, marked, or censored at the end of available data. |

The canonical document also says the supplied class examples do not establish a precise stop-loss (sections 3.2/12). The repository’s `NIFTY_Groww_Pure_Learning_v001.zip` contains project code, tests, and sample data, but no class slides, video, transcript, or other source material that supplies an exit rule. Thus the supplied class examples are described by the canonical document but cannot be independently inspected from this repository.

## B. Actual implementation

### Entry detection

`app/strategies.py::ekalayava_events` (`app/strategies.py:21`) implements one event per date per contract:

1. It uses the first candle’s opening levels and skips that opening candle as a setup candle.
2. It waits for a candle low below Opening Low.
3. It uses `swing_highs(left=2, right=0)` from `app/premium_swing.py:1`: a candle is marked when its high is above the prior two highs. This is causal; it uses no later candle.
4. After such a swing is seen, a later candle must have both high and close strictly above the swing high. The code rejects a candle whose high has already reached Opening High before it evaluates entry, so an accepted entry is before the target.
5. The entry is that completed candle’s close. `README.md:9` documents this current operational rule, including the prior-two-high lookback and the high-and-close breakout condition.

The broad below-low → recovery/swing → later breakout sequence is consistent with the canonical sequence. The canonical document leaves the exact reversal test and swing lookback open for an explicit causal implementation choice; the present implementation supplies a causal prior-two-high rule. It does not separately calculate or require a named reversal-low / higher-low pattern. `premium_features` computes a rolling `reversal_from_recent_low` feature, but `ekalayava_events` does not use it as a condition. Because the canonical reversal language is qualitative, this is an unresolved specification detail, not a basis for silently imposing a different condition during this audit.

### Outcome and exit handling

`app/paper.py::analyze_ekalayava` (`app/paper.py:70`) invokes `simulate_target` (`app/paper.py:90`). The simulator:

- examines only candles strictly after entry;
- limits the path to the same Asia/Kolkata trading date (`_same_day_future`, `app/paper.py:8`) and at most 78 rows;
- recognizes only `row.high >= target` as an exit and records `TARGET` at Opening High;
- initializes outcome as `OPEN`, with null exit time/price, and leaves it that way if target is not reached or there are no later same-day candles;
- calculates MFE/MAE on the observed post-entry path;
- has no Ekalayava SL, opposite-signal, forced end-of-day, expiry, or end-of-data close/mark logic.

The `end="15:15"` argument constrains setup/entry detection; it is not a liquidation instruction. Simulation itself stops when same-day data ends. It does not carry Ekalayava positions to subsequent dates.

The period aggregator (`app/period_research.py::_summary`, `app/period_research.py:96–130`) deliberately reports Ekalayava win rate as undefined because no stop-loss is defined. The saved baseline contains 170 Ekalayava events: 82 `TARGET`, 88 `OPEN`, 0 `SL`, and 3,574.6 summed target points.

### Event schema

The period backtest event rows carry entry/contract metadata, target, outcome, `exit_time`, `exit_price`, `points_gained_lost`, `time_to_exit_minutes`, MFE, and MAE. Ekalayava rows do not have a defined stop value. The OPEN rows set exit time/price/points/holding time to null, while retaining excursion values. The separate lightweight journal schema in `app/journal.py:3` has fields for `sl`, target, MFE, MAE, and outcome, but omits exit timestamp, exit premium, holding time, and explicit exit reason (and several contract identifiers); it is not a full trade-lifecycle audit record.

## C. Differences and specification conflicts

1. **No outright exit-rule violation was found.** Leaving SL undefined and not inventing another exit follows the canonical document’s explicit instruction. The implementation is a target-only outcome simulator, not a complete P&L lifecycle implementation.
2. **Entry operationalization is more specific than the canonical narrative.** The code uses a causal current-high-above-prior-two-highs swing, then a later candle with both high and close above that reference, while requiring the entry candle high to remain below Opening High. The README documents these choices; the canonical document requires causal parameters and entry before Opening High but does not itself specify every numerical/price-comparison detail.
3. **An older project instruction conflicts with the current canonical definition.** `projectexecution.md:446–509` describes entry only after a completed candle closes above Opening High and says no target was specified / do not invent exits. That is inconsistent with the later canonical correction in `NIFTY_Strategy_Definitions_Level_to_Level_Ekalavya.md:436–456` and final definition at `:647–655`, which say entry before Opening High and Opening High is the target. The current strategy implementation follows the later canonical correction, not that stale Step 15H text. The README also reflects the later rule.
4. **Lifecycle behavior is missing by design/under-specification.** No implementation path handles stop-loss, opposite signal, end-of-day, expiry, or end-of-data for Ekalayava. Since the canonical document does not define those exits, this audit did not add them or call the omission a rule violation.

## D. Why the 88 trades remain OPEN

For these events the simulator found no post-entry, same-session candle with a high reaching Opening High. Since the only implemented exit is the target, the default `OPEN` status and null exit fields remain. The OPEN label is therefore expected behavior of this target-only simulator when its target condition is not observed; it is also evidence that the current research implementation cannot resolve a complete trade lifecycle.

These are **not positions carried continuously from entry until 2026-09-25**. The entries span 2026-04-27 through 2026-09-24, and each path was cut off at the end of the same-date rows available to the simulator—normally session close on complete dates, but potentially earlier where option candles were missing. The previous diagnostic’s “OPEN at period end 2026-09-25” wording overstates the simulation horizon. More precisely, they were OPEN at the end of each entry date’s observed same-day path. Of the 88, 81 were on fully usable dates, 6 on partially usable dates, and 1 on a date classified unusable by the baseline coverage report. Missing intervals may therefore also conceal a target touch for some events; the data cannot establish that counterfactual.

The baseline event records contain MFE and MAE for all 88 opens, but all 88 have null exit time, exit price, realized points, and holding duration.

## E. Can 3,574.6 points be treated as realized results?

**Not as complete Ekalayava P&L, and not for P&L comparison with Level-to-Level.** The 3,574.6 is the sum of the 82 target-touch outcomes, each credited at the Opening High by the simulator. It is a target-hit subset result from the existing paper backtest. It excludes 88 unresolved entries and has no defined stop-loss or alternative close rule, so it does not measure the P&L of the full 170-entry strategy. It also should not be described as a complete realized return. No fees, position sizing, or execution assumptions are established by this point sum.

## F. Missing information before a valid full P&L backtest

The strategy owner must supply or explicitly approve a versioned trade-management specification that resolves:

1. Whether the undefined SL stays absent or a specific stop rule is adopted. No stop is inferred by this audit.
2. Whether touching Opening High closes the full position, and how target/other exit conflicts within one 5-minute candle are handled.
3. Whether and how an opposite signal exits an open position.
4. Whether positions must close at end of day, and the applicable exit price convention.
5. What happens on expiry (including expiry-day positions) and at the end of available historical data: close, mark-to-market, or report as censored/open with an explicit valuation convention.
6. The formal meaning of “low/reversal develops” if a separate reversal criterion is required beyond the current causal swing-and-break sequence.

Until these choices are recorded, the defensible output is setup analysis and target-touch counts/points with unresolved events labeled OPEN—not a complete Ekalayava P&L comparison.

**Audit verdict:** the implementation matches the specification’s stated entry-before-Opening-High and Opening-High target behavior under its documented causal swing convention, and correctly refrains from inventing an SL. It is not a complete implementation of Ekalayava trade management/P&L because the canonical exit lifecycle is unresolved. No implementation bug violating an explicit canonical exit rule was identified.

## G. Required next decision

Decide and version the Ekalayava exit and unresolved-position convention, including the SL decision and end-of-day / opposite-signal / expiry / end-of-data behavior. If no exit beyond the target is intended, explicitly define how non-targeted entries are classified and valued. Only after that decision should implementation and tests be updated, followed by a new P&L backtest. This audit made no such decision or code change.

## Files inspected

- `NIFTY_Strategy_Definitions_Level_to_Level_Ekalavya.md` (especially sections 3, 6, 7, 12, and 13)
- `app/strategies.py`, `app/premium_swing.py`, `app/paper.py`, `app/period_research.py`, `app/weekly_experiment.py`, `app/journal.py`
- `README.md`, `PROJECT_STATE.md`, `ERROR_LOG.md`, `projectexecution.md`, `agent_exec.md`, `STRATEGY_VERSIONS.md`, `RESEARCH_PLAN.md`, `EXPERIMENT_LOG.md`, `NEXT_TASK.md`
- `tests/test_ekalayava_backtest.py`, `tests/test_paper_backtest.py`, `tests/test_paper_engine.py`, `tests/test_period_research.py`, `tests/test_learning.py`
- `NIFTY_Groww_Pure_Learning_v001.zip` (contents listed above; no class source material)

### Test coverage observed

The Ekalayava-specific backtest tests cover reaching Opening High, requiring an earlier Opening-Low break, and rejecting entry if Opening High was already reached before breakout. They do not test an unresolved target/no-target path, SL, opposite-signal, forced end-of-day, expiry, or end-of-data handling. The paper-engine and paper-backtest tests concern Level-to-Level. No test currently asserts the intended lifecycle for Ekalayava opens; the existing canonical definition does not supply that lifecycle.

