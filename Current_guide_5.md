MASTER RESEARCH TASK — ULTIMATE EKALAYAVA STOP-LOSS AND EXIT POLICY DEVELOPMENT

Objective

Develop and rigorously evaluate a candidate stop-loss and exit policy for the existing Ultimate Ekalayava NIFTY options strategy.

The goal is to determine whether the strategy can capture favourable premium movements while controlling downside risk, without overfitting historical data.

This is a bounded, paper-only research task. Inspect the existing repository, canonical strategy definitions, saved trade ledgers, historical policy experiments, validation reports and available candle data before changing anything.

Do not rebuild the system. Reuse the existing strategy engine, research framework, simulator, reports and tests wherever possible.

1. Mandatory safety and scope

Keep these settings unchanged:

* EXECUTION_ALLOWED=false
* PAPER_ONLY=true
* LIVE_ORDER_SUBMISSION_ENABLED=false

Never submit, modify or cancel broker orders.

Do not connect this experiment to a live execution pathway.

Do not download unavailable historical datasets or perform broad historical backfills.

Do not run a full parameter-optimization grid.

Do not modify the canonical Ekalayava entry rules.

Do not overwrite existing research reports, ledgers or strategy definitions.

Do not declare any experimental policy approved for real-money execution.

Make changes only in the research/simulation layer. Preserve the working tree and inspect existing changes before editing.

2. Read existing research before starting

Inspect these existing reports if present:

* TARGET_HIT_ANALYSIS_L2L_EKALAYAVA_2026-10-13.md
* EXECUTION_AUDIT_AND_READONLY_OBSERVER_READINESS_2026-10-13.md
* TODAY_FULL_SESSION_L2L_EKALAYAVA_REPLAY_2026-10-13.md
* NIFTY_Strategy_Definitions_Level_to_Level_Ekalavya.md

Inspect the relevant code, including the existing Ekalayava entry engine, exit-policy simulator, saved entry ledger, historical experimental-policy ledger, data-coverage inventory and test suite.

Existing research contains 253 Ekalayava entry observations. Prior experiments include:

* A_STRUCTURAL_TROUGH_B4_TP25: 157 simulated target exits, gross −272.90 points and validation gross −72.25.
* B_BREAKOUT_CANDLE_B2_TP100_OPENING_HIGH: 65 simulated target exits, gross +1,145.70 points, maximum drawdown 306.30 points and longest losing streak 25.

Treat these as experimental historical results, not approved policies or verified real fills.

Confirm these figures from the saved evidence before using them. Do not rerun the historical optimization grid just to reproduce them.

3. Preserve the canonical Ekalayava entry rules

The entry definition must remain unchanged:

1. Establish Opening High and Opening Low from the first completed five-minute premium candle.
2. Observe the premium trading below Opening Low.
3. Identify a subsequent recovery/base.
4. Identify a causally formed swing high.
5. Enter on the breakout of that swing high before Opening High.
6. Do not require the entry candle to close above Opening High.

All swing and structure detection must use information available at the relevant timestamp. Never use future candles to identify a historical swing or create an earlier signal.

Do not introduce a new entry filter to improve exit results.

The exit-policy research must use the same underlying canonical entry observations wherever data coverage permits, so comparisons are fair.

4. Today’s example: use it as a trace, not as the answer

Inspect the existing report for 13 October 2026.

The recorded PE ITM3 example has:

* Entry observation at 10:25 IST.
* Entry premium: 43.55.
* Structural trough before breakout: 26.15.
* Maximum favourable excursion through 13:45: +22.65 points.
* Maximum adverse excursion through 13:45: −34.25 points.
* Opening High target: 216.05.
* No Opening High touch recorded through 13:45.

Independently verify these values against the source records before using them.

This example is only a partial-session observation. It is not a completed trade, and the maximum favourable excursion is not guaranteed profit.

Use this trade to trace how each candidate stop and exit would have behaved on the available candle sequence. Do not select a policy solely because it appears favourable on this one example.

Do not claim what happened after 13:45 unless complete, verified subsequent candles are already available.

5. First requirement: reconstruct entry-by-entry candle paths

Before evaluating policies, determine whether the available data can support reliable path replay.

For each existing Ekalayava entry, join the exact entry timestamp and option contract to the subsequent completed five-minute candles.

Record:

* Exact instrument and expiry.
* Entry timestamp and recorded entry price.
* Entry signal and strategy version.
* Opening High and Opening Low.
* Structural trough known at entry, if one exists.
* Breakout-candle low, if available.
* Subsequent completed candle OHLC values.
* Maximum favourable excursion (MFE).
* Maximum adverse excursion (MAE).
* Missing intervals and data-quality issues.
* Last valid observation timestamp.

Never join different option contracts or expiries accidentally.

Do not infer the missing candle path from aggregate MFE/MAE alone.

If the saved data does not contain timestamped post-entry candle paths, mark that policy comparison as blocked or incomplete. Do not fabricate candle sequences.

Reuse available local data. Do not start a broad historical download.

6. Define a small, controlled candidate set

Evaluate three policy families. Keep the candidate count small and fixed before inspecting comparative results.

Family A — Structural stop plus fixed premium target

Initial stop reference: the recovery/base structural trough known at entry, where that reference can be established causally.

The stop buffer must be explicit, expressed in premium points, and fixed before evaluation. If existing policy definitions support a limited set of buffers, reuse those candidates rather than inventing a large grid.

Test a small set of fixed premium targets, including a 20–25-point target and one larger target consistent with the existing research.

The simulator must reject invalid stop placement and record the exact rejection reason.

Family B — Structural stop plus trailing exit

Use the same initial structural stop.

After the trade moves favourably, allow the stop to trail only beneath newly confirmed structural swing lows. A swing low can influence the stop only after it becomes observable under the causal swing-confirmation rule.

Specify exactly:

* When trailing becomes active.
* How a new swing low is confirmed.
* How the stop is calculated.
* Whether the stop can only tighten.
* How a stop gap is treated.

Do not use future candles to move a stop backwards in time.

Do not add a trailing rule that has not been implemented and tested.

Family C — Structural stop plus reward-to-risk target

Define initial risk as the positive distance between entry and the valid initial stop.

Evaluate a small, predefined set of reward-to-risk multiples using the same initial stop.

Record the target formula, risk distance and actual target price for every entry.

Skip invalid cases explicitly. Never use a zero or negative risk distance.

Experimental isolation

Assign every candidate a unique policy ID and version.

Keep the current canonical Ekalayava entry strategy unchanged. All three families remain experimental; none becomes the canonical exit policy automatically.

Do not combine multiple policy changes into a single candidate.

7. Use conservative execution assumptions

A five-minute candle’s high or low touching a level does not prove that a real limit order would have filled.

Use explicit, consistent simulator conventions:

1. A hypothetical entry at the completed signal candle’s close is a research assumption, not a guaranteed fill.
2. Begin stop/target monitoring after the entry candle unless existing, verified execution semantics explicitly justify another treatment.
3. For a stop gapped through at the next candle’s open, use a conservative executable-price assumption rather than awarding an artificial improvement.
4. For a target gapped through, do not automatically assume a better fill than the target.
5. If stop and target are both touched in one candle and their order cannot be established, classify the result as ambiguous.
6. Missing candles and stale data must remain unresolved; do not interpolate.
7. If the session ends with an open hypothetical position, report it as unresolved unless an explicitly named experimental end-of-session policy applies.
8. Do not silently add a forced end-of-day exit to the canonical strategy.
9. Separate gross premium-point results from estimated transaction costs.
10. If bid/ask spread, slippage, brokerage, taxes or other cost inputs are unavailable, clearly label net profitability as unverified.

Use consistent execution conventions across all compared candidates.

8. Chronological evaluation and anti-overfitting

Use the existing training/validation partition documented in the repository. Do not invent a new partition after viewing the results.

If existing partitions are insufficient, define a chronological split before candidate evaluation and document it.

Do not randomly shuffle time-series observations.

For each candidate report:

* Training entry count and outcome counts.
* Validation entry count and outcome counts.
* Gross points.
* Net points only when defensible cost assumptions are available.
* Target-exit rate.
* Stop-exit rate.
* Ambiguous and unresolved outcomes.
* Maximum chronological drawdown.
* Longest losing streak.
* Average and median result per eligible entry.
* Average initial risk.
* Average realised reward-to-risk ratio.
* MFE and MAE distributions.
* Performance by CE/PE and ITM rank where sample size supports comparison.
* Sensitivity to missing data and execution assumptions.

Count each underlying entry once per candidate policy. Prevent duplicate policy/setup identities.

Do not choose the best candidate solely by target-hit rate or gross points.

Do not choose a policy solely because it performed best in the full sample.

A candidate that looks excellent in training but degrades materially in validation must be flagged.

If validation is too small or incomplete to support a reliable decision, state that explicitly.

9. Reconcile previous results

Compare new results with the existing saved policy ledger only where the underlying entries, source candle paths and execution assumptions are comparable.

Explain differences caused by:

* Changed simulator conventions.
* Stop-gap handling.
* Same-candle ambiguity.
* Session-end handling.
* Missing candles.
* Different eligible-entry counts.
* Incomplete contract coverage.

Do not silently overwrite earlier results or represent an apples-to-oranges comparison as an improvement.

If the available candle paths cannot reproduce an earlier experiment, document the limitation rather than inventing an explanation.

10. Focused tests required

Add or run tests covering:

* Causal structural-trough detection.
* Structural-stop calculation.
* Invalid stop placement.
* Fixed target calculation.
* Reward-to-risk target calculation.
* Trailing stop activation.
* Causal swing-low confirmation.
* Stop tightening behaviour.
* Stop gap at candle open.
* Target gap treatment.
* Same-candle stop/target ambiguity.
* Missing candle intervals.
* Duplicate timestamps.
* Entry-candle exclusion from exit monitoring.
* Unresolved session-end position.
* No future-data leakage.
* Duplicate policy/setup prevention.
* Execution flags remaining disabled.

Run the relevant existing tests first, followed by the full relevant research/simulator suite if feasible.

Report actual commands and results. Do not claim tests passed unless they were run.

11. Deliverables

Create a new report:

EKALAYAVA_EXIT_POLICY_RESEARCH_2026-10-13.md

Include:

1. Existing evidence reviewed.
2. Data availability and candle-path completeness.
3. Candidate policy definitions and fixed parameters.
4. Execution assumptions.
5. Results for each candidate.
6. Training versus validation comparison.
7. Drawdown and losing-streak comparison.
8. Cost and slippage limitations.
9. Results for the 10:25 PE ITM3 trace, if the necessary candle path is available.
10. Reasons candidates failed or remain inconclusive.
11. Test commands and outcomes.
12. Whether any candidate merits further paper testing.
13. The single recommended next research step.

Save machine-readable candidate results using existing repository conventions, with new filenames. Never overwrite canonical definitions or existing research ledgers.

12. Decision rules

Do not automatically approve any policy.

A candidate may be recommended for further paper testing only if:

* Its stop and exit rules are fully specified.
* It is causally implementable in live five-minute candles.
* Its validation results are not materially worse than its training results.
* Drawdown and losing-streak behaviour are acceptable relative to the existing candidates.
* Its result is not driven by a few isolated trades or favourable assumptions.
* Data coverage is sufficient to interpret the comparison.
* Important transaction costs and execution uncertainties are disclosed.

If no candidate meets these conditions, retain the current canonical entry rules and keep the exit lifecycle unresolved pending better evidence.

13. Final response

Summarise:

1. Which candidate policy performed best on validation, if any.
2. Whether it outperformed the alternatives on more than target-hit rate.
3. Its gross result, drawdown, losing streak and unresolved count.
4. Whether the 10:25 PE ITM3 example would have survived the candidate’s stop and how its later path is evidenced.
5. Whether the candle-path data is sufficient for a trustworthy comparison.
6. Whether any policy merits additional paper-only evaluation.
7. What remains unproven.
8. The path to the new report.

Keep all real-money execution disabled. Do not claim profitability or declare an experimental exit policy canonical based on this research alone.
