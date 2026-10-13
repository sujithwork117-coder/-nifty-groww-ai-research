FINAL OFFLINE MISSION — COMPLETE NIFTY STRATEGY FINALISATION, EXIT RESEARCH, SHADOW EVALUATION, SAFETY AUDIT AND MILESTONE CLOSURE

You are the senior quantitative research engineer, Python engineer, testing engineer and safety auditor for this existing NIFTY options paper-trading research repository.

Your task is to complete every milestone that can be honestly completed offline before the next market session. Do not stop after producing a plan, inspecting the repository, or running tests. Inspect the actual implementation, implement the missing offline components, validate the results, run the full test suite, reconcile the evidence, update the existing master report, and verify the final Git state.

Tomorrow must be reserved for the remaining genuine live-session checks.

1. Primary objective

Finalise the research and paper-observation architecture for these two existing strategies:

1. Level-to-Level (L2L).
2. Ultimate Ekalayava.

By the end of this mission, I need definitive answers to the following:

* How many of the existing Mission 11 milestones are fully completed?
* How many are partially completed, blocked, or waiting exclusively for tomorrow’s live session?
* How many additional milestones were completed by this finalisation mission?
* What are the validated historical entry counts, target hits, stop-loss exits, ambiguous outcomes, unresolved paths and experimental session-end exits for each strategy and each tested exit policy?
* Which exit policy, if any, has credible out-of-sample evidence?
* Does either strategy demonstrate robust positive expectancy after defensible transaction-cost sensitivity analysis?
* How many qualifying signals, hypothetical target hits, stop-loss outcomes and unresolved observations are available for paper evaluation?
* What precisely must be verified tomorrow before we can trust the observer’s live data?
* Is either strategy ready for supervised paper observation, and what evidence is still required before approving any strategy lifecycle?

Do not confuse a historical target touch with an executable trade, a target hit with a profitable net trade, a completed software milestone with a validated trading strategy, or readiness for paper observation with authorization for live trading.

2. Mandatory safety constraints

These are non-negotiable.

* Keep EXECUTION_ALLOWED=False.
* Keep PAPER_ONLY=True.
* Never enable live order execution.
* Never submit, modify, cancel or create a real broker order.
* Do not introduce any broker order-submission path.
* Do not change safety flags to make tests pass.
* Do not weaken the execution lock, kill switch, authentication checks or other safety controls.
* Do not use real money or make live-trading claims.
* Do not fabricate prices, candles, quotes, fills, spreads, costs, missing records or performance metrics.
* Do not substitute missing option contracts with a different strike, expiry or ITM rank.
* Do not use incomplete candles to generate completed-candle signals.
* Do not use future candles, future information, future swing highs or future contract information when determining a historical entry.
* Do not approve an exit policy merely because it has the highest aggregate historical gross points.
* Do not change canonical strategy rules to improve backtest results.
* Do not delete losing trades, missing observations, interrupted sessions, ambiguities or adverse outcomes.
* Do not silently overwrite historical reports or research results in ways that destroy their provenance.

No exit policy is automatically approved at the end of this mission. Approval must follow evidence, not a predetermined desired result.

3. Repository and working rules

Work in the existing repository and current main branch. The workspace used by the previous Mission 11 report was:

/workspaces/-nifty-groww-ai-research

First verify the actual workspace, branch, current commit, Git status, project configuration and existing master report. If the runtime path differs, locate the existing repository rather than creating another project.

Use the existing virtual environment and project dependencies. Inspect the actual files before making changes.

Read the current EKALAYAVA_MISSION11_MASTER_REPORT.md and the linked existing research evidence, including the target/stop count reconciliation, final evidence and data coverage, research execution summary, B2 trailing-proxy audit and paper-trading readiness report where available.

Treat existing artifacts and the current implementation as the source of truth for what actually exists. If reports conflict, document and investigate the conflict using existing artifacts. Do not combine incompatible counts or claim reconciliation without reproducing it.

Do not repeat already completed historical recovery, download more historical datasets, or rerun expensive experiments unnecessarily. Use the existing documented 2025 H2 and available 2026 datasets. Preserve existing data and research artifacts.

Use available compute and API credits carefully. Prefer deterministic local calculations, existing datasets and the existing test suite. No external LLM/API calls are needed.

Create no competing project, duplicate master report or unnecessary report collection. Update the existing master report with a clearly dated finalisation section and an auditable milestone table.

4. Preserve the canonical strategy definitions

Before coding, locate the canonical strategy definitions and existing engine implementations. Record their current parameters and confirm that this mission will not alter them.

A. Level-to-Level

Preserve the existing rules:

1. Use the first completed five-minute NIFTY candle to establish Opening High and Opening Low.
2. Wait for a completed red five-minute candle to break below Opening Low.
3. Enter at the close of the first subsequent completed green five-minute candle.
4. Respect the existing entry window of 09:15–11:00 IST.
5. Stop-loss level is Opening Low minus four points, using the existing premium/underlying reference specified by the canonical implementation.
6. Target is Opening High, using the same canonical reference.
7. Skip an entry if its entry price is already at or beyond the target.
8. Preserve same-candle stop/target ambiguity handling.
9. Do not invent a forced end-of-day exit or timeout that does not exist in the canonical rules.

Verify the precise instrument and price references in the current code rather than assuming that the NIFTY underlying and option premium are interchangeable.

The historical baseline previously reported 203 eligible entries, 57 targets, 145 stop-loss outcomes and one ambiguous outcome, with +237.45 gross points and a reported maximum drawdown of 250.05 points. Reproduce these figures from the appropriate existing artifacts if possible. If the dataset or definitions have changed, explain the exact difference instead of forcing a match.

B. Ultimate Ekalayava

Preserve the existing causal entry rules:

1. Establish the opening range from the completed opening five-minute candle.
2. Observe the option premium moving below Opening Low.
3. Identify recovery/base formation using only information available at that time.
4. Form a swing high causally; do not retrospectively use a future candle to declare an earlier swing high.
5. Enter on the permitted swing-high breakout before Opening High is reached.
6. The entry candle does not need to close above Opening High.
7. Preserve the existing exact contract selection and premium-reading requirements.
8. Preserve the existing five-minute timeframe.

The canonical Ekalayava engine currently records observations, MFE/MAE and unresolved lifecycles when no approved exit buffer is configured. Do not convert unresolved observations into realised P&L.

The existing seven experimental exit candidates must remain research candidates until the evidence supports a decision.

5. Establish a reproducible baseline before changing code

Run the relevant existing tests and reproduce the current research counts using the existing scripts and artifacts.

Record:

* Repository commit and branch.
* Dataset paths, date ranges and file fingerprints where practical.
* Trading sessions and expected versus available observations.
* Entry counts by strategy, date, instrument, CE/PE, ITM rank and entry time.
* Complete, partial, missing, duplicate and unresolved paths.
* Existing target, stop-loss and ambiguity counts.
* Existing gross results, drawdown and consecutive-loss metrics where supported.
* The exact definition of a point, the instrument represented by that point, and whether any multiplier is applied.

Create a baseline comparison before making changes. Do not silently change the denominator of any metric.

If an existing result cannot be reproduced, label it NOT REPRODUCED and explain why.

6. Complete the isolated seven-candidate Ekalayava exit evaluator

The existing research contains these seven candidates:

* A_B4_OPENING_HIGH_V1
* A_B4_TP25_V1
* A_STRUCTURAL_TROUGH_B4_TP25
* B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1
* C_B2_1R_V1
* C_B2_1_5R_V1
* C_B2_2R_V1

Inspect their exact existing definitions and parameters. Do not guess what B4, B2, R, buffers or structural levels mean; use the repository definitions.

The existing offline simulator is separate from the live observer. Complete a deterministic, isolated paper-shadow evaluator that can process the existing entry observations and subsequent completed five-minute candles for all seven candidates.

Requirements:

1. Use the same validated input observations and candle paths for comparable candidates.
2. Preserve the original entry timestamp and entry price for each observation.
3. Enforce chronological processing and no lookahead.
4. Apply a stop update only at the exact effective candle boundary specified by the candidate.
5. Never count a target touched after an earlier valid exit as a target hit.
6. Handle missing intervals, incomplete paths, gaps and same-candle stop/target ambiguity explicitly.
7. Never infer intrabar ordering that OHLC data cannot establish.
8. Never fabricate an executable fill from a candle high or low.
9. Keep hypothetical entry, stop, target and exit prices distinct from observed broker quotes and actual fills.
10. Record the exit reason and exact source candle for every simulated outcome.
11. Ensure repeated processing of the same observation or candle is idempotent.
12. Keep the canonical entry engine and all seven experimental candidates separate.
13. Do not let an experimental candidate activate a broker exit or modify the canonical strategy.
14. Persist enough information to reproduce each candidate result from the underlying journal and input artifacts.

The evaluator must produce both per-observation records and an aggregated report for every candidate.

Include the number of evaluated entries, target exits, stop exits, ambiguous outcomes, partial paths, missing paths, experimental session-end exits, unresolved observations and excluded records.

If a candidate cannot be evaluated consistently across the same eligible observations, explain the coverage difference and provide a like-for-like comparison on the shared sample.

Do not silently discard any outcome.

7. Complete L2L evaluation and lifecycle checks

Verify the existing L2L implementation against the canonical definition.

Create or complete deterministic historical replay tests that cover:

* Opening candle selection.
* Red breakdown below Opening Low.
* First subsequent green entry.
* Entry window enforcement.
* Already-breached target skip.
* Stop-loss and target ordering.
* Same-candle ambiguity.
* Missing candles and gaps.
* Incomplete five-minute candles.
* Duplicate candle replay.
* Restart and replay idempotency.
* Rejected out-of-order provider rows.
* No future-data leakage.

Reconcile the eligible entry count and all exit outcomes using the existing artifacts.

Do not introduce additional L2L exit variants unless they already exist and are necessary to reproduce the canonical baseline. This mission is not permission to optimise canonical L2L parameters.

8. Evaluate exit policies using defensible research methods

The objective is not to select a winner at any cost. The objective is to determine whether an exit policy has sufficient evidence to justify further paper observation.

For each Ekalayava candidate, report:

* Number of eligible and evaluated entries.
* Target, stop, ambiguous, partial and unresolved counts.
* Gross points under the explicitly stated point convention.
* Net sensitivity under clearly labelled hypothetical transaction-cost assumptions.
* Average and median outcome.
* Win rate, with the denominator defined.
* Profit factor, only where mathematically meaningful.
* Maximum drawdown and the method used to calculate it.
* Longest losing streak.
* MFE and MAE where the underlying data supports them.
* Holding time and exit-reason distribution.
* Results by CE/PE, ITM rank, entry time and session.
* Training, validation and test results where a defensible chronological split is available.

Prevent data leakage:

1. Split data chronologically.
2. Never select a candidate using the same held-out data on which it is declared successful.
3. Treat previously inspected or repeatedly optimised periods as no longer untouched.
4. Reuse existing declared splits where their provenance is sound.
5. Do not invent a new untouched test period from already inspected data.
6. If there is insufficient data for a reliable out-of-sample conclusion, say so explicitly.

Evaluate performance stability across sessions and market regimes where sample size permits. Report the sample size for every subgroup. Avoid treating many correlated trades from a small number of sessions as independent evidence.

Transaction costs must be handled honestly:

* Use measured costs only when sourced and documented.
* Otherwise report clearly labelled cost-sensitivity scenarios.
* Never describe a hypothetical cost as an actual brokerage fee, spread or fill.
* Keep point returns separate from currency P&L unless the actual contract multiplier, lot size and capital assumptions are known.

A gross-positive candidate must not be called robustly profitable if plausible cost assumptions erase the result or if validation performance is unstable.

Required decision

Classify each candidate as one of:

* REJECTED — INVALID OR UNSAFE SIMULATION
* REJECTED — INSUFFICIENT OR UNSTABLE EVIDENCE
* RESEARCH ONLY — PROMISING BUT UNVALIDATED
* ELIGIBLE FOR FURTHER PAPER OBSERVATION
* NOT EVALUABLE — DATA LIMITATION

Do not classify any candidate as approved for live trading.

If no candidate meets the evidence criteria, the correct conclusion is that no exit policy can yet be selected defensibly. Do not manufacture a winner merely to close the milestone.

Do not change the canonical strategy lifecycle based on these research results.

9. Integrate the seven candidates into an isolated observer shadow workflow

Mission 11 identified this as a partial milestone. Complete as much of the integration as can be implemented and tested offline.

Extend the existing observer only through a separate, deterministic, paper-only shadow-evaluation component. Reuse the existing data acquisition, candle validation, contract-selection, persistence and safety infrastructure.

For every eligible Ekalayava observation, maintain seven separate hypothetical candidate states.

The observer must:

* Record the canonical entry observation independently.
* Feed the same eligible completed candles to each applicable candidate.
* Persist candidate-specific hypothetical stop and target state.
* Apply exit rules at the proper candle boundary.
* Track ambiguous and unresolved states without forcing an exit.
* Make restart/replay deterministic.
* Prevent duplicate signals and duplicate candidate exits.
* Keep candidate metrics separate from canonical engine metrics.
* Keep hypothetical fills and costs null unless there is genuine sourced evidence.
* Never generate broker orders.
* Never use experimental results to alter canonical entry conditions.
* Expose per-candidate state and error information in the existing health/journal mechanism.

If a full observer integration would require changing canonical behavior, weakening safety, or relying on unavailable live information, stop at the safe boundary and document the exact limitation. Do not fake a completed integration.

Add tests proving that every candidate can process an eligible replay in isolation, that candidates cannot affect one another, and that none can submit, modify or cancel an order.

10. Complete journal reconciliation and end-of-session reporting

Mission 11 also identified end-of-session reconciliation as blocked.

Implement a deterministic, offline reconciliation command using the repository’s existing journal schema and actual artifacts. Follow the existing project CLI conventions; do not create a competing framework.

The command must:

1. Read the selected session’s health snapshot and journal.
2. Validate record schemas and stable identities.
3. Detect duplicate records, timestamp inconsistencies, gaps and incomplete candles.
4. Compare persisted observations with persisted strategy and shadow-candidate states.
5. Identify signals with no matching state, states with no matching observation, incomplete paths, missing contracts and unresolved exits.
6. Reconcile per-candidate outcome counts and points against the source records.
7. Report missing quotes, actual fills and transaction costs without fabricating them.
8. Distinguish an absent event from a confirmed event with zero value.
9. Produce a concise machine-readable result and a human-readable terminal summary.
10. Exit non-zero for integrity failures, with a clear error message.
11. Avoid modifying source journal data or silently repairing records.
12. Be safe to rerun and produce deterministic output.

Test the command using synthetic fixtures and the existing local historical artifacts. Include cases for duplicates, missing intervals, malformed records, incomplete paths, conflicting events, ambiguous exits and repeated reconciliation.

If there is no legitimate session journal yet, validate the command using fixtures and existing local artifacts. Do not invent a real-session reconciliation result.

11. Finalise the offline readiness and safety audit

Review the existing authentication, observer, candle loader, contract selector, persistence layer, reconnect logic, journal and execution lock.

Verify:

* Authentication failures do not leak credentials or provider response contents.
* Profile validation fails safely.
* The exact CE/PE ITM2/ITM3 contract selector never substitutes missing ranks.
* Expiry and symbols are validated for the selected trading date.
* The observer rejects incomplete, duplicate or out-of-order candles according to the documented rules.
* Candle timestamps are normalized consistently to the expected timezone.
* Staleness and missing-interval conditions are visible.
* Reconnection is bounded.
* Restarting cannot create duplicate signals or exits.
* Persistence errors cannot be mistaken for healthy operation.
* Graceful shutdown preserves state.
* Only one observer is allowed to use the same state directory at a time.
* The effective safety lock remains EXECUTION_ALLOWED=False and PAPER_ONLY=True.
* The observer and every candidate use read-only market-data interfaces.
* No order-submission or order-modification method is called.
* All tests and reports describe mock coverage as mock coverage, not proof of real-provider behavior.

Perform source-level safety inspection and tests. Do not expose secrets or dump environment variables.

Do not run a continuous observer session tonight. Do not claim real-session freshness, complete live contract availability or real reconnect recovery without actual market-session evidence.

12. Define the exact live-session checks for tomorrow

The remaining live-dependent work must be reduced to a short, actionable checklist.

The checklist must verify:

1. Effective safety flags and successful read-only authentication/profile preflight.
2. Actual selected trading date and expiry.
3. Complete availability of all four exact requested contracts: CE ITM2, CE ITM3, PE ITM2 and PE ITM3.
4. contract_coverage == 4/4 and no missing contracts before treating the feed as complete.
5. Correct completed five-minute candle timestamps.
6. Advancing timestamps and plausible freshness for both NIFTY and each selected option.
7. No unexplained gaps, duplicate events, stale candles or out-of-order data.
8. Journal and health persistence during the session.
9. Correct signal and shadow-state processing on actual incoming data.
10. Safe graceful shutdown and a controlled restart/recovery check if appropriate.
11. End-of-session reconciliation and clear accounting of unresolved records.

If any exact contract is unavailable, record that the relevant strategy coverage is incomplete. Never substitute a different strike or expiry.

Abort the observation if authentication fails, safety flags are incorrect, the opening underlying candle is missing, the health status remains degraded, persistence fails, data becomes unexplainedly stale, or bounded reconnection fails.

Do not enable live execution to overcome any failure.

13. Run the complete test suite and regression checks

After implementing the missing offline work:

* Run the complete existing test suite.
* Run all newly added tests.
* Run static compilation checks.
* Run relevant lint/type checks if the repository already configures them.
* Run the existing CLI help and read-only authentication/profile preflight only if safe and appropriate.
* Recheck the execution lock.
* Search the changed source for any order-submission or modification calls.
* Confirm that canonical strategy definitions and parameters did not change.
* Confirm that historical source artifacts were not overwritten.
* Verify idempotency, deterministic replay and reconciliation.
* Check the Git diff for unintended changes and secrets.

The Mission 11 report previously recorded 136 passing tests. Use the actual final result; do not assume the old count still applies. Fix regressions introduced by this mission before declaring success.

If a test cannot run because a dependency, credential or provider is unavailable, report the exact limitation instead of claiming it passed.

14. Update the existing master report

Update EKALAYAVA_MISSION11_MASTER_REPORT.md in place with a new clearly dated section titled:

Final Offline Strategy Finalisation — 2026-10-13

If the actual date differs, use the real execution date.

Include:

* Baseline commit and final commit.
* Exact changed files and why each changed.
* Test commands and actual results.
* Baseline versus final milestone status.
* Ekalayava results for all seven candidates.
* L2L reconciliation.
* Strategy counts and explicit denominators.
* Target-hit, stop-loss, ambiguous, unresolved, partial and excluded counts.
* Gross performance and appropriately qualified cost sensitivity.
* Chronological split and out-of-sample limitations.
* Any unreconciled differences between earlier reports and current artifacts.
* Shadow integration and reconciliation-command evidence.
* Safety audit and order-path isolation.
* A short tomorrow-only live verification checklist.
* Exact outstanding blockers.
* Git commit and push status only if actually verified.

Preserve older conclusions and historical provenance. Do not erase earlier results merely because newer results differ. Explain the reconciliation.

15. Produce two distinct milestone scorecards

This is mandatory because the project has two different types of goals.

Scorecard A — Software and research milestones

Use the existing Mission 11 milestone list as the baseline. Report the count in each category:

* Fully completed offline.
* Partially completed.
* Blocked by implementation or missing offline evidence.
* Requires actual live-session verification.

Then report:

* Previous fully completed count.
* Number newly completed by this mission.
* Final total completed out of the existing total.
* Remaining milestones.
* Percentage completed, calculated using the existing milestone denominator.
* Exact evidence for every status.

Do not count one milestone twice. If a milestone is split into sub-milestones, retain the original top-level denominator and separately explain the sub-milestones.

A milestone is completed only when its acceptance criteria and tests pass. Merely writing a class, creating a report, or passing a mock test is not sufficient to claim real-provider readiness.

Scorecard B — Strategy performance and target outcomes

For L2L and each of the seven Ekalayava candidates, separately report:

* Eligible entries.
* Evaluated entries.
* Target exits.
* Stop-loss exits.
* Ambiguous outcomes.
* Unresolved and partial paths.
* Experimental session-end exits, if applicable.
* Gross points under the declared convention.
* Net sensitivity under explicitly labelled hypothetical costs.
* Out-of-sample performance where available.
* Whether the evidence supports further paper observation.

Explain the difference between:

1. Milestones achieved.
2. Historical target hits.
3. Qualifying strategy signals.
4. Evidence-backed exit-policy selection.
5. Readiness for supervised paper observation.

Do not report a single combined “target count” that mixes these different quantities.

If the requested results cannot be determined from available artifacts, report UNKNOWN and specify the exact missing evidence.

16. Final completion criteria

Do not finish the task merely because the tests pass.

The offline mission is complete only when:

* All safely achievable implementation milestones are completed.
* The seven-candidate shadow workflow is integrated and tested, or any remaining technical blocker is specifically evidenced and documented.
* L2L behavior remains canonical and regression-tested.
* The end-of-session reconciliation command is implemented and tested offline.
* All candidate results are reproducible.
* The performance comparison includes chronological validation and explicit limitations.
* No exit policy is falsely approved.
* The full test suite passes or remaining failures are clearly isolated and justified.
* Safety flags remain correct.
* No real order has been submitted, modified or cancelled.
* The existing master report contains both scorecards and the live-only checklist.
* Git changes are reviewed, scoped and committed only after verification.

Push to the existing main branch only if repository access is available, tests pass, the diff contains only intended files and the remote state is safe to update. Never force-push, discard other people’s changes or stage market-data/recovery artifacts accidentally. If pushing is unavailable or unsafe, report the exact reason.

17. Required final response

When finished, give me a concise but complete summary in this order:

1. Final milestone count: completed / total, with partial, blocked and live-only counts.
2. Newly completed this mission: exact count and names.
3. L2L results: entry and outcome counts, gross result, validation limitations.
4. Ekalayava results: all seven candidates in one comparison table, including target/stop/unresolved counts and validation status.
5. Best-supported exit decision: name a candidate only if the evidence supports it; otherwise state clearly that no exit is defensibly selected yet.
6. Paper-observation readiness: what is ready offline and what remains unverified.
7. Tests and safety: actual test totals and confirmation that execution remains disabled.
8. Git status: actual commit and push status.
9. Tomorrow-only checklist: exact commands and the live conditions that must pass.

Be evidence-driven and economical with compute. Implement rather than merely recommend. Do not inflate completion counts, do not manufacture profitability, and do not trade.

The desired outcome is maximum legitimate offline completion tonight and a minimal, clearly defined set of live checks tomorrow.
