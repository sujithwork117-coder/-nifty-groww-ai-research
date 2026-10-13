MASTER TASK: L2L + EKALAYAVA EXECUTION AUDIT, OPTIMIZED TARGET-HIT ANALYSIS, AND READ-ONLY GROWW VALIDATION

1. Project context and objective

Work inside the existing nifty-groww-ai-research repository on the current branch.

The objective is to independently verify the existing research, audit execution assumptions, calculate exactly how many targets were hit under the baseline and previously tested optimization policies for both strategies, fix confirmed safe defects, and determine whether the Groww observer is ready for supervised, read-only paper validation.

Do actual repository work. Do not merely produce a generic assessment or repeat previous reports without checking the underlying evidence.

Read the existing strategy definitions, research reports, source code, trade-level CSVs, summary outputs, configurations, journals, provider integration, and tests before making changes.

Previously reported results to verify independently

L2L baseline

* 361 setups.
* 203 entries.
* 57 target exits.
* 145 stop-loss exits.
* 1 ambiguous trade.
* 158 skipped setups.
* 202 resolved trades.
* +237.45 gross points.
* Reported maximum chronological drawdown: 250.05 points.
* Reported longest losing streak: 23.

Existing L2L target experiments

* Previously tested target levels include TP100, TP75, TP50, and TP25, with existing stop-loss variants and combined policies.
* TP100 represents the Opening High target in the existing experiment definitions; verify this from the implementation.
* TP50 with the existing SL4 configuration reportedly generated +254.65 gross points over the full period but failed the reported July–August validation comparison.
* Do not assume these reported values are correct until reconciled against the existing artifacts.

Ekalayava

* 253 observed entries.
* 109 Opening High touches in the previously reported observations.
* Existing experimental exit-policy results include multiple stop anchors, buffers, target levels, and a trailing-stop candidate.
* No canonical Ekalayava exit lifecycle has been approved.
* Do not classify the 109 Opening High touches as wins or realized target exits.

Existing environment and data

* Historical research coverage reportedly ends on September 29, 2026.
* September 2026 is incomplete if the source data confirms this.
* The previously requested July–December 2025 data is unavailable locally.
* No additional historical data downloads are authorized.
* The earlier test run reported 53 passing tests; rerun the actual tests and report their current results.

Treat all these figures as starting points to investigate, not guaranteed facts.

2. Non-negotiable safety constraints

These requirements override all other tasks.

* EXECUTION_ALLOWED=false
* PAPER_ONLY=true
* No live order placement.
* No order modification or cancellation.
* Never invoke an order-submission endpoint, including for testing.
* Do not enable live trading.
* Do not expose API keys, tokens, cookies, or other credentials in logs, terminal output, reports, exceptions, or committed files.
* Do not change canonical strategy rules without a separately documented and explicitly approved specification.
* Do not download additional historical market data.
* Do not chase unavailable July–December 2025 data.
* Do not retrieve 2022–2024 data.
* Do not run another full optimization grid.
* Do not run continuous or unattended live-market monitoring.
* Do not repeatedly retry unavailable providers or endpoints.
* Do not invent missing candles, fills, prices, test results, or provider responses.
* Do not silently substitute a contract, expiry, strike, candle, or missing observation.
* Do not commit or push changes unless explicitly requested.

Verify the safety flags before and after the work.

If any critical safety invariant fails, stop execution-related testing and report the defect.

3. Phase A — Repository inventory and reproducibility

Inspect the actual implementation and existing research artifacts.

Locate and inspect:

* Canonical L2L strategy definition.
* Canonical Ekalayava entry definition.
* Existing Ekalayava exit experiments.
* Opening-range and opening-candle calculations.
* Five-minute candle construction and completion logic.
* Entry-signal generation.
* Contract, expiry, strike, CE/PE and ITM2/ITM3 selection.
* Stop-loss and target simulation.
* Existing target and stop optimization outputs.
* Trade-level ledgers and summary CSVs.
* Research report generation scripts.
* Historical candle loaders and locally available datasets.
* Groww authentication and provider adapter.
* Observer startup and polling or streaming logic.
* Signal journal and paper-trading journal.
* Configuration and execution safety guards.
* Existing tests, fixtures, dependency versions and documented commands.

Create an inventory recording:

* File path.
* Purpose.
* Canonical strategy, experimental research, infrastructure or reporting classification.
* Existing tests.
* Known limitations.
* Whether modification is necessary.

Use the current repository environment and dependency versions. Avoid broad dependency upgrades or unrelated refactoring.

Run the existing targeted test suite and record the exact commands, exit codes, and actual results. Do not assume the earlier 53 tests still pass.

4. Phase B — Independently reconcile L2L baseline results

Recalculate the existing L2L baseline from the underlying trade-level data.

Verify:

* Total eligible setups.
* Valid entries.
* Skipped setups and reason codes.
* Target exits.
* Stop-loss exits.
* Ambiguous trades.
* Unresolved or incomplete trades.
* Resolved-trade count.
* Gross points.
* Average gross points per valid entry.
* Average gross points per resolved trade.
* Profit factor and its precise formula.
* Maximum chronological drawdown.
* Longest consecutive losing streak.
* Available CE/PE, ITM-rank and entry-time distributions.

Ensure the trade categories reconcile without double-counting.

Check whether the reported 202 resolved trades agree with the actual classifications. Explain any discrepancy.

Use chronological ordering for drawdown and losing streak calculations.

Do not treat skipped setups as losing trades. Do not include unresolved trades in resolved-trade P&L.

Do not count a single trade more than once.

Produce a reconciliation table containing:

Metric	Previously reported	Recalculated	Difference	Evidence	Explanation

If a value cannot be independently recalculated because required fields are absent, label it NOT VERIFIABLE.

5. Phase C — Audit L2L execution semantics

Inspect the current implementation of every relevant event and fill rule.

C1. Stop-loss gaps

For a long option trade with stop price S, verify:

* What happens if the next candle opens below S.
* Whether the current simulator fills at S despite the opening price being below S.
* Whether the candle open, low, stop level and assumed fill price are recorded.
* Whether stop triggering and simulated execution are represented separately.
* Whether only five-minute OHLC is available.

Document the difference between a theoretical stop-price fill and a conservative gap-aware fill.

If five-minute OHLC is the only evidence, explain that using the candle open is a conservative candle-level proxy, not proof of the real-world fill price.

C2. Target gaps

For target price T, inspect what happens if a candle opens above T.

Document whether the current simulator fills at T, at the open, or according to another rule.

Do not introduce a favorable fill assumption without evidence and approval.

C3. Same-candle ambiguity

When a candle’s high reaches the target and its low reaches the stop:

* Inspect the current classification.
* Determine whether finer-grained data already exists locally.
* Never infer which level was reached first from OHLC alone.
* Preserve unresolved ordering as ambiguous unless valid existing evidence resolves it.

C4. Entry candle

Verify:

* Entry occurs at the intended completed five-minute candle close.
* Earlier price movement inside the entry candle is not treated as a post-entry exit.
* The first eligible exit candle is the next completed candle.
* Pre-entry highs and lows do not create fictitious exits.

C5. Missing or malformed data

Test handling of:

* Missing candles.
* Duplicate timestamps.
* Out-of-order timestamps.
* Invalid OHLC relationships.
* NaN and non-finite prices.
* Incomplete candles.
* Internal candle gaps.
* Wrong contracts attached to trades.
* Timezone-naive timestamps.
* Repeated timestamps across sessions.

Never forward-fill an option premium to manufacture a stop or target event.

C6. Session and terminal behavior

Document current market-close handling.

Do not introduce a forced end-of-day exit or maximum holding period into canonical L2L simply because it appears reasonable.

6. Phase D — Propose a fill specification without silently changing canonical behavior

Create a separate proposed execution specification.

For each proposed rule, document:

* Existing behavior.
* Proposed behavior.
* Reason for the proposal.
* Required source fields.
* Impact on target counts.
* Impact on stop counts.
* Impact on gross P&L.
* Effect on ambiguous and unresolved classifications.
* Whether the change affects the canonical strategy or only the execution simulator.
* Tests required before adoption.

Cover:

1. Stop-loss trigger and gap-through fills.
2. Target gaps.
3. Same-candle stop/target ambiguity.
4. Missing candle handling.
5. Entry-candle exclusion.
6. Terminal-session behavior.
7. Unfilled and unresolved trades.

Do not silently adopt the proposed rules.

If exit-bar OHLC is unavailable in historical records, check whether the required candles already exist locally. If they do not, state that the historical recalculation is blocked.

Do not download data.

You may create isolated synthetic fixtures to demonstrate the difference between fill rules, but label them as examples, not historical performance.

7. Phase E — Audit Ekalayava entries and experimental exits

Keep Ekalayava separate from L2L.

E1. Verify entry mechanics

Compare the actual implementation with the documented entry definition:

1. The first completed five-minute candle defines Opening High and Opening Low.
2. Premium trades below Opening Low.
3. Recovery/base formation occurs after the breakdown.
4. A causally formed swing high is identified.
5. Entry occurs when the premium breaks the swing high before Opening High.
6. Entry does not require the breakout candle to close above Opening High.

Inspect actual trade records and code.

Check for lookahead, including:

* Future candles used to identify a swing high.
* Swing points confirmed using bars that were not complete at the time.
* Retrospective signals that could not have been known at entry.
* Future price data used in strike or expiry selection.

Report the number of records verified, rejected, and unverifiable.

E2. Audit existing experimental exits

Inspect existing outputs without rerunning the full grid.

Verify each existing policy’s:

* Stop anchor.
* Buffer.
* Target level.
* Post-entry candle handling.
* Gap-through handling.
* Same-candle ambiguity handling.
* Missing-data handling.
* Terminal exit behavior.
* Trailing-stop update timing.

For the existing trailing-stop candidate, determine whether the lower-low rule is causal and whether the updated stop is applied only from the next candle.

Do not silently replace the existing trailing rule with a different swing-low algorithm.

Do not classify an Opening High touch as a realized win.

Do not approve a canonical Ekalayava exit rule in this phase.

8. Phase F — Statistical integrity and report correctness

Inspect existing metrics and reporting code for:

* Duplicate trade rows.
* Summary rows counted as trades.
* Incorrect CE/PE or ITM-rank attribution.
* Inconsistent units.
* Incorrect profit factor formulas.
* Drawdown calculated using shuffled or nonchronological rows.
* Missing sessions treated as zero-signal sessions.
* Incomplete sessions treated as complete.
* Target touches classified incorrectly as exits.
* Missing exits omitted without disclosure.
* Skipped setups included in trade performance.
* Gross points described as net profit or investment returns.
* Backtest observations mixed with paper-observer results.

Explicitly distinguish gross points from net returns. Do not imply that brokerage, exchange fees, taxes, spreads, slippage, position sizing or capital requirements are accounted for unless the existing system demonstrably models them.

Preserve original research artifacts. Document every regenerated output.

9. Phase G — Exact optimized target-hit analysis for L2L

This is a mandatory deliverable, not an optional recommendation.

Use the existing baseline, target optimization CSVs, combined-policy results and trade-level ledgers. Inspect the implementation to verify each policy definition.

Do not rerun the full optimization grid.

G1. Policies to evaluate

Include the canonical L2L baseline:

* Opening High target.
* Opening Low −4 points stop-loss.
* Canonical entry rules.

Then evaluate all previously tested target policies and existing combinations, including the available TP100, TP75, TP50 and TP25 variants and existing stop-loss combinations.

Verify the actual target calculation and stop rules from code. Do not assume policy names alone establish their semantics.

G2. Exact target-hit counts

For each existing policy, report:

* Eligible setups.
* Valid entries.
* Target touches, if independently measurable.
* Simulated target exits.
* Stop-loss exits.
* Ambiguous outcomes.
* Unresolved outcomes.
* Skipped setups and reason codes.
* Complete and incomplete post-entry paths.
* Target-exit rate among valid entries.
* Target-hit rate among complete paths where measurable.
* Target-exit rate among resolved trades.
* Gross points.
* Average gross points per entry.
* Average gross points per resolved trade.
* Profit factor.
* Maximum chronological drawdown.
* Longest losing streak.

For every percentage, provide the numerator and denominator.

Do not use a single denominator for all metrics. Explicitly distinguish:

* All eligible setups.
* Valid entries.
* Complete post-entry paths.
* Resolved trades.

Use the existing documented execution rule to count a target exit. Do not count an ambiguous same-candle stop/target event as a confirmed target exit.

G3. Baseline comparison

For every existing candidate, calculate:

* Difference in target exits versus baseline.
* Difference in target-exit rate in percentage points.
* Difference in stop-loss exits.
* Difference in ambiguous outcomes.
* Difference in unresolved outcomes.
* Difference in gross points.
* Difference in maximum drawdown.
* Difference in longest losing streak.

Identify separately:

1. The candidate with the highest target-exit count.
2. The candidate with the highest target-exit rate.
3. The candidate with the best gross performance under the existing validation evidence.

These may be different policies. Do not combine them into a single winner.

10. Phase H — Exact optimized target-hit analysis for Ekalayava

This is also mandatory.

Inspect the existing Ekalayava exit-policy grid and saved outputs. Do not rerun the full grid.

Include every previously evaluated policy that has sufficient recorded evidence. Verify the actual stop anchor, buffer, target percentage and execution rules.

H1. Separate three event types

Report the following independently:

1. Target touch

The available candle data indicates that the target price was reached.

2. Simulated target exit

The existing policy’s execution rules allow the target exit to be recorded, accounting for the policy’s stop rules, ambiguity and missing-data behavior.

3. Real-world fill

Not established by historical candle simulation.

Never report a target touch as a win automatically.

H2. Exact metrics per policy

For each existing policy, report:

* Total eligible entries.
* Entries with complete post-entry candle paths.
* Target touches.
* Simulated target exits.
* Stop-loss exits.
* Same-candle ambiguous outcomes.
* Terminal exits where permitted by that experimental policy.
* Unresolved or incomplete paths.
* Target-touch rate among eligible entries.
* Target-touch rate among complete paths.
* Simulated target-exit rate among eligible entries.
* Simulated target-exit rate among resolved trades.
* Gross points.
* Average gross points per eligible entry.
* Average gross points per resolved trade, where meaningful.
* Profit factor, where meaningful.
* Maximum chronological drawdown.
* Longest losing streak.

Use explicit numerators and denominators.

If historical exit assumptions are defective or unresolved, mark affected counts provisional.

H3. Compare against the reference

Compare each existing Ekalayava candidate with the available observation/reference baseline.

Because the canonical exit lifecycle is unresolved, do not invent a canonical baseline P&L.

If no comparable baseline exit count exists, say so. You may compare the experimental policies with each other while keeping the distinction clear.

Report:

* Difference in target touches.
* Difference in simulated target exits.
* Difference in hit rate.
* Difference in gross points.
* Difference in drawdown.
* Difference in losing streak.
* Difference in ambiguous and unresolved outcomes.

Group policies by actual stop anchor, buffer and target level.

Identify separately:

1. Highest target-touch count.
2. Highest simulated target-exit count.
3. Highest simulated target-exit rate.
4. Best gross performance under existing validation evidence.

Do not select a canonical strategy based on the largest number of target touches or target exits alone.

11. Phase I — Chronological validation of target-hit improvements

Use the existing train/validation split and saved results. Do not rerun the full optimization grid.

Verify actual data coverage before assigning a period label.

Where available, report metrics separately for:

* Existing training period.
* Existing July–August 2026 validation period.
* September 2026 diagnostic period, marked incomplete if source coverage confirms incompleteness.

For every baseline and existing candidate, report:

* Eligible entries.
* Complete paths.
* Target touches.
* Simulated target exits.
* Target-hit rate.
* Stop-loss exits.
* Ambiguous outcomes.
* Unresolved outcomes.
* Gross points.
* Maximum drawdown.
* Longest losing streak.

Show whether an apparent target-hit improvement persists in validation or is concentrated in the training period.

Do not call a period an independent holdout if it was used for candidate selection.

Do not claim robustness solely because a candidate has more target hits or a higher target-hit rate.

If the existing outputs do not support a period-specific count, mark it NOT VERIFIABLE instead of rerunning an unauthorized optimization or inventing missing values.

12. Phase J — Segment target-hit results

Where reliable labels exist, break down the baseline and existing candidates by:

* CE versus PE.
* ITM2 versus ITM3.
* Entry-time bucket.
* Month or existing chronological period.

For each segment report:

* Sample size.
* Complete paths.
* Target touches.
* Simulated target exits.
* Target-hit rate.
* Stop-loss exits.
* Ambiguous outcomes.
* Unresolved outcomes.
* Gross points.

Use the same policy definition and comparable denominator within each comparison.

Do not infer missing contract labels.

Flag small sample sizes and incomplete coverage. Do not claim statistical significance unless a suitable analysis has actually been performed.

13. Phase K — Target-count data-quality safeguards

Before reporting optimized target counts:

* Deduplicate using the correct signal or trade identifier.
* Verify that each trade has at most one terminal exit.
* Confirm the actual target calculation for each policy.
* Exclude pre-entry candles.
* Verify whether the target level was known at entry.
* Check same-candle stop/target handling.
* Check gaps through stop and target levels.
* Identify missing and incomplete candle paths.
* Keep ambiguous and unresolved outcomes separate.
* Verify chronological ordering.
* Use consistent counting definitions where policies are comparable.
* Do not silently convert missing values to zero.
* Do not treat skipped setups as entries.
* Do not count repeated candle touches as multiple target exits for the same trade.

For Ekalayava, keep target touches distinct from simulated target exits.

For L2L, keep canonical target exits distinct from experimental target-touch observations.

If a count cannot be calculated from existing artifacts, report NOT VERIFIABLE and name the missing source fields or files.

14. Phase L — Required target-analysis output files

Create:

1. TARGET_HIT_ANALYSIS_L2L_EKALAYAVA_2026-10-13.md
2. target_hit_policy_period_summary.csv
3. target_hit_baseline_comparison.csv
4. target_hit_data_quality_summary.csv

Save these under the repository’s existing reports/output directory, following its naming conventions if necessary.

Required fields for the machine-readable results

Include, where supported:

* strategy
* policy_id
* policy_description
* stop_policy
* target_policy
* target_level
* period
* eligible_setups
* eligible_entries
* complete_paths
* target_touches
* target_exits
* stop_exits
* ambiguous_count
* unresolved_count
* skipped_count
* target_hit_numerator
* target_hit_denominator
* target_hit_rate
* gross_points
* average_points_per_entry
* average_points_per_resolved_trade
* profit_factor
* max_drawdown
* longest_losing_streak
* data_coverage_status
* metric_status
* limitations

Use genuinely missing values where a metric is unavailable. Do not replace missing data with zero.

Document every metric definition and denominator.

The report must include the actual numeric baseline-versus-candidate comparison for both strategies wherever the evidence permits.

15. Phase M — Observer architecture and readiness audit

Inspect the Groww observer to determine whether it can safely collect completed five-minute market observations without placing orders.

M1. Authentication and provider access

* Inspect existing authentication and documented API capabilities.
* Never expose credentials.
* Verify access only using existing documented read-only operations.
* Do not invent provider endpoints.
* Do not assume the account or API plan supports streaming or historical data without evidence.
* Avoid repeated retries.
* If credentials or provider access are unavailable, report the blocker.

M2. Read-only enforcement

Trace the observer’s reachable call paths.

Verify that:

* Observer startup cannot call an order-submission function.
* Observer cannot modify or cancel orders.
* Paper simulation is isolated from provider order interfaces.
* Safety flags are checked at appropriate boundaries.
* Unsafe configurations fail closed.
* Reconnects cannot change execution mode.
* Logs and journals identify the system as read-only and paper-only.

If order-related functions exist, inspect whether the observer can reach them. Do not invoke them to test this.

Do not claim a hard execution lock based only on configuration values; inspect the code boundary.

M3. Exact contract selection

Verify existing NIFTY CE/PE ITM2/ITM3 selection:

* Correct underlying.
* Correct documented expiry-selection rule.
* Correct reference price and strike calculation.
* Correct ITM rank for both CE and PE.
* Correct option-contract identity.
* Rejection of stale option-chain data.
* Rejection of expired or invalid contracts.
* No silent substitution when ITM2 or ITM3 is unavailable.
* Consistent contract identity across reconnects unless the documented selection rules require a new selection.

Do not alter approved contract-selection rules without documenting the defect.

M4. Five-minute candle integrity

Verify:

* Asia/Kolkata timezone handling.
* Correct five-minute candle boundaries.
* Completed-candle-only signal processing.
* No duplicate candle processing.
* Missing candles detected, not synthesized.
* Stale feed distinguished from a quiet market.
* Opening-range state preserved correctly across restart.
* Backfilled and live candles are not double-counted.

If candle completion is inferred rather than explicitly supplied by the provider, document the mechanism and its limitations.

M5. Recovery and persistence

Audit:

* Authentication expiry.
* Network disconnection.
* Rate limits.
* Empty or malformed responses.
* Delayed candles.
* Duplicate events after reconnect.
* Restart during an open paper position.
* Restart between signal detection and journal persistence.
* Storage failure or corruption.

Use bounded retries with backoff where appropriate.

On reconnect:

* Reconcile the latest completed candle before processing new signals.
* Deduplicate using stable signal identifiers.
* Restore opening range, signal state and paper positions from persisted state.
* Never reconstruct missing prices by guessing.
* Never submit an order.

If recovery is unsafe, stop processing the affected instrument/session and record the reason.

16. Phase N — Automated tests

Add or update focused tests for confirmed defects and critical invariants.

At minimum cover:

1. L2L opening range.
2. L2L qualifying red breakdown.
3. First subsequent green-candle entry.
4. Entry-window boundaries.
5. Stop-loss and target calculations.
6. Skip when entry is at or beyond target.
7. Same-candle ambiguity.
8. Stop gap-through handling.
9. Target gap handling.
10. Exclusion of entry-candle excursions.
11. Missing candles.
12. Duplicate signal suppression.
13. Completed-candle-only processing.
14. Exact CE/PE ITM2/ITM3 selection.
15. No silent contract fallback.
16. Asia/Kolkata boundaries.
17. Restart recovery.
18. Reconnect idempotency.
19. Observer isolation from order submission.
20. Unsafe configuration fails closed.
21. Ekalayava swing-high causality.
22. Ekalayava trailing-stop timing.
23. Trade-ledger reconciliation.
24. Chronological drawdown and losing-streak calculation.
25. Target-hit numerator and denominator calculations.
26. No double-counting of target exits.
27. Distinction between target touch and simulated target exit.
28. Correct handling of incomplete paths.
29. Correct period-specific target counts.
30. Correct CE/PE and ITM-rank segmentation where supported.

Use deterministic synthetic candles for edge cases and label them as synthetic tests, not historical performance evidence.

Run the existing targeted test suite, new tests and existing static checks where available.

Record exact commands, actual pass/fail counts, skipped tests, exit codes and errors.

Never claim a test passed unless it was actually executed.

17. Phase O — Supervised read-only Groww integration test

Proceed only if the local audit establishes a safe read-only path.

Prepare a bounded, supervised test that:

* Uses the existing provider integration.
* Reads only the minimum market data needed to test connectivity and candle handling.
* Does not run unattended.
* Does not submit, modify or cancel orders.
* Does not start a continuous strategy loop.
* Uses explicit timeouts and retry limits.
* Records sanitized diagnostics.
* Stops cleanly on timeout, stale data, safety violations or user interruption.

Where safely available, verify:

1. Authentication outcome.
2. Read-only provider request.
3. Selected contract identity.
4. Candle timestamps and completion.
5. Duplicate suppression.
6. Missing-data detection.
7. Disconnect/reconnect behavior.
8. Journal persistence and recovery.
9. Safety flags before and after the run.
10. Confirmation that no order interface was called.

Do not deliberately disrupt a production connection if doing so risks the account or other running applications. Use mocked failures for unsafe-to-induce scenarios.

If credentials or network access are unavailable, finish the offline checks and mark live integration as BLOCKED or NOT RUN. Do not claim mocked tests are live verification.

18. Phase P — Observer readiness decision

Use only these status values:

* PASS
* FAIL
* BLOCKED
* NOT TESTED
* NOT APPLICABLE

Provide a readiness matrix for:

* Read-only enforcement.
* Contract selection.
* Candle completion.
* Timezone and calendar.
* Duplicate prevention.
* Persistence and restart recovery.
* Missing/stale data.
* Reconnect behavior.
* Signal journal integrity.
* Paper simulation.
* Kill switch and operational stop behavior.

Do not declare the observer ready if a critical safety, contract-selection, candle-integrity or persistence check fails or remains unverified.

19. Phase Q — Change management

Keep all changes small, auditable and evidence-based.

Before changing code:

* Identify the exact defect.
* Identify affected functions, files and tests.
* Explain why the fix does not silently alter canonical strategy rules.

After changing code:

* List every modified file.
* Explain each change.
* Run relevant tests.
* Record remaining failures.
* Preserve original research evidence.
* Document regenerated outputs.

Do not commit or push changes.

Do not alter canonical L2L:

* First completed five-minute candle defines Opening High/Low.
* Qualifying red breakdown below Opening Low.
* First subsequent green candle is the entry.
* Entry window 09:15–11:00 IST.
* Stop = Opening Low −4 points.
* Target = Opening High.
* No invented forced end-of-day or time-based exit.

Keep Ekalayava experimental exits separate until a canonical exit specification is explicitly approved.

20. Final report requirements

Create:

EXECUTION_AUDIT_AND_READONLY_OBSERVER_READINESS_2026-10-13.md

Include:

1. Executive summary.
2. Repository inventory.
3. Independently reconciled L2L baseline.
4. Ekalayava entry and exit audit.
5. Execution-model defects and proposed fill specification.
6. Historical evidence availability.
7. Exact fixes implemented.
8. Test commands and actual results.
9. Groww connectivity outcome or exact blocker.
10. Read-only safety evidence.
11. Observer readiness matrix.
12. Files changed.
13. Remaining risks.
14. The single recommended next action.

Reference relevant filenames, functions, test names and output rows.

Create the separate target-hit analysis report and CSV outputs specified in Phase L.

Mandatory numerical conclusions

In the target-hit report, answer these questions separately for L2L and Ekalayava:

1. What is the baseline target-exit count?
2. Which previously tested policy has the highest target-exit count?
3. Exactly how many target exits did that policy produce?
4. What is the absolute difference in target exits versus baseline?
5. What is the percentage-point difference in target-hit rate?
6. What is the denominator for that rate?
7. Did gross performance improve or deteriorate?
8. Did drawdown or the losing streak worsen?
9. Did the apparent improvement persist in the existing validation period?
10. How many outcomes are ambiguous, unresolved or unobservable?
11. How many target touches did not qualify as simulated target exits?
12. Is the evidence sufficient to justify further paper-only testing?

For Ekalayava, if the canonical baseline has no defined exit lifecycle, explicitly state that a canonical baseline target-exit count is unavailable. Compare existing experimental policies without fabricating one.

For L2L, distinguish the canonical Opening High target from alternative experimental targets.

If the existing evidence cannot support an exact number, say NOT VERIFIABLE and explain what is missing. Do not guess, infer from aggregate gross P&L, or rerun the full optimization grid.

21. Completion criteria

The task is complete only when:

* Baseline metrics have been independently reconciled wherever possible.
* Every existing target policy with sufficient data has an explicit target-hit count.
* Target touches and simulated target exits are distinguished.
* Baseline-versus-candidate differences are calculated.
* Existing validation-period target results are reported.
* Ekalayava experimental exits remain separate from its canonical entry definition.
* Execution-model defects are documented and confirmed safe defects are fixed.
* Automated tests have actually been run.
* Read-only safety boundaries have been inspected and tested.
* Groww integration is either verified safely or marked blocked/not run.
* Reports and machine-readable outputs are generated.
* Missing evidence is disclosed.
* No new historical data was downloaded.
* No full optimization grid was rerun.
* No live order was submitted, modified or cancelled.
* Live execution remains disabled.

Finish with a concise decision summary containing:

* What was verified.
* What was fixed.
* Exact baseline and optimized target counts for each strategy where verifiable.
* Which optimization, if any, deserves further paper-only evaluation.
* Which findings remain uncertain.
* The single safest next action.

Do not claim that the strategy is profitable, robust or live-ready merely because tests pass or target-hit counts increase.
