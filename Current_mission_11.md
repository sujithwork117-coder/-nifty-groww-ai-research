EKALAYAVA MISSION 11 — COMPLETE ALL NON-LIVE MILESTONES

1. Mission objective

Act as the senior quantitative researcher, Python engineer, trading-systems engineer, test engineer and security auditor for this existing NIFTY options research project.

Complete every feasible milestone that does not require an actual live Indian market session.

I have approximately 40% of my coding-agent credits remaining. Work efficiently and autonomously. Reuse existing code and completed research. Do not repeat finished work without a specific, evidence-backed reason.

The required end state is a repository that is:

* Historically researched and reconciled.
* Correctly implemented for the existing canonical strategies.
* Ready for supervised, read-only market observation.
* Equipped with deterministic shadow paper simulation.
* Restart-safe, observable and recoverable.
* Covered by meaningful automated tests.
* Secure and protected against order execution.
* Documented in ONE comprehensive Mission 11 master report.
* Ready for the remaining live-session verification tomorrow.

Do not merely produce a plan. Inspect the repository, implement feasible missing functionality, run the checks, fix verified defects and document the actual outcome.

Do not promise that every milestone can be completed if the repository or external services prevent it. Finish everything feasible and identify genuine blockers.

2. Existing research: treat this milestone as substantially complete

Inspect the current versions of these reports and related artifacts:

* EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md
* EKALAYAVA_FINAL_RESEARCH_EXECUTION_SUMMARY.md
* EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md
* EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md
* EKALAYAVA_PAPER_TRADING_READINESS.md
* Existing canonical strategy definitions.
* Historical manifests, trade ledgers, reconciliation outputs and test results.

Use the actual repository filenames if suffixes differ.

The current documented baseline includes:

* 194 canonical Ekalayava entries from the second half of 2025.
* 253 saved 2026 entry observations with recovered exact-contract post-entry paths.
* 447 combined recorded observations.
* Seven existing exit-policy candidates reconciled on the available ledger.
* An independent B2 audit that reported 447/447 matching outcomes, points and exit timestamps.
* A previous report of 129 passing tests.
* No approved stop-loss/target policy.

These are prior reported results. Verify existing artifacts and current test state before relying on them.

Do not rerun historical data recovery, expand historical date ranges, purchase data, launch large optimization grids or recreate completed reports unless you discover a concrete defect that requires it.

Do not silently modify historical results. If a reproducibility check finds a discrepancy, investigate and document it.

3. Absolute safety rules

This mission is strictly read-only observation and shadow simulation.

Maintain:

* EXECUTION_ALLOWED=False
* PAPER_ONLY=True

Never submit, modify or cancel broker orders.

Never activate an experimental exit policy.

Never connect shadow stop-loss, target or trailing-stop decisions to a broker order-management path.

Preserve authentication protections, the kill switch, duplicate-signal protection and all other safety controls.

Do not treat an empty account balance as a safety mechanism.

Do not expose credentials, access tokens, API keys or sensitive account details in source code, reports, logs, tests or Git history.

Do not weaken a safeguard to make a test pass. If order-path isolation cannot be verified, fail closed.

Search for all order-submission functions and their callers. Verify that the observer and shadow simulator cannot reach them. Add tests that prove the observation workflow does not invoke order submission.

No live execution is authorized by this prompt.

4. Repository and architecture audit

Inspect the actual repository, current branch, working tree, dependency files, configurations, source code and tests before editing.

Map the existing implementation for:

* Configuration and environment variables.
* Groww authentication and read-only profile access.
* Historical-data loading.
* Live five-minute candle observation.
* Option contract selection.
* Level-to-Level strategy engine.
* Ekalayava strategy engine.
* Feature extraction and price-action analysis.
* Premium and swing analysis.
* Shadow paper-trading engine.
* Stop-loss and target simulation.
* Trade journal and persistent state.
* Reports and dashboard data.
* Logging, reconnection and error handling.
* Market-hours handling.
* Duplicate-signal prevention.
* Kill switch and execution lock.

Reuse existing components wherever they work correctly.

Before making changes, identify the gaps between current functionality and the required end state. Prioritize safety, correctness, persistence, testing and tomorrow’s operation.

Do not perform a wholesale rewrite.

5. Canonical strategy definitions

A. Level-to-Level

Preserve the existing canonical definition and implementation:

* The first completed five-minute candle establishes the Opening High and Opening Low.
* A completed red candle breaks/trades below the Opening Low.
* The first subsequent completed green candle is the entry at its close.
* Entry window is 09:15–11:00 IST.
* Stop-loss is Opening Low minus four premium points.
* Target is Opening High.
* Preserve the documented skip-entry rule when entry is already at or beyond target.
* Preserve existing ambiguity handling and avoid introducing unsupported forced end-of-session exits.

Verify that the implementation is causal and agrees with its existing tests.

B. Ekalayava

Preserve the existing canonical Ekalayava entry logic:

* The first completed five-minute candle establishes the opening range.
* Premium breaks below the Opening Low.
* The subsequent recovery/reversal structure is evaluated chronologically.
* A causally valid swing high is identified.
* Entry is considered on the completed-candle swing-high breakout before reaching Opening High.
* The entry candle does not have to close above Opening High.
* Price-action interpretation must remain part of the analysis; do not require a rigid textbook candle pattern if the canonical rule does not require one.

Use only information available at the decision timestamp.

Do not change canonical entry rules to improve historical profitability. Do not add indicators or new entry filters during this mission.

If a verified defect exists, correct it minimally, document it and add a regression test.

6. Read-only market-data pipeline

Complete all offline-verifiable checks and repairs.

Verify:

* Authentication/profile checks use read-only capabilities.
* Data requests use the intended five-minute interval.
* Timezones and timestamp types are normalized consistently.
* Candle ordering is deterministic.
* Only completed candles can produce confirmed signals.
* The current incomplete candle is never treated as a completed candle.
* Stale, missing, duplicate and out-of-order data are detected.
* Session boundaries and holidays are handled correctly.
* Reconnects cannot silently duplicate candles or signals.
* Invalid or mismatched data cannot silently become valid input.
* Errors are logged without revealing credentials.
* The process can stop and restart without corrupting prior observations.

Use recorded fixtures and mocks for offline tests.

Do not claim that mocked tests prove actual live-data freshness. Mark real-session behaviour as UNVERIFIED until tested tomorrow.

7. Option contract selection

Inspect and test the exact contract-selection logic for:

* CE ITM2.
* CE ITM3.
* PE ITM2.
* PE ITM3.

For each selected contract, capture:

* Exact trading symbol.
* Expiry.
* Strike.
* CE or PE.
* ITM rank.
* Selection timestamp.
* Underlying/reference premium.
* Data-source timestamp.
* Quote/candle freshness.
* Selection rationale.

Never substitute a different strike or expiry silently.

Handle missing contracts explicitly. The observer may continue collecting valid available data if that is safe, but the report must show missing coverage and must not claim the missing contract was monitored.

Do not assume the previous contract-coverage problem has been fixed. Verify the code and report the actual status.

Live-session availability and freshness must remain UNVERIFIED until checked tomorrow.

8. Deterministic shadow paper-trading engine

Inspect and complete the isolated research/shadow simulator.

Preserve these candidate definitions exactly as they currently exist:

* A_B4_OPENING_HIGH_V1
* A_B4_TP25_V1
* A_STRUCTURAL_TROUGH_B4_TP25
* B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1
* C_B2_1R_V1
* C_B2_1_5R_V1
* C_B2_2R_V1

Do not select a winner or change parameters.

The simulator must:

* Process candles chronologically.
* Never use future data.
* Use the documented stop and target formulas.
* Apply trailing updates at the correct next-candle boundary.
* Prevent multiple exits for one position.
* Distinguish target exits, stop exits, ambiguous events, end-of-session exits and unresolved observations.
* Never count a target touched after exit as a winning trade.
* Handle gaps and incomplete paths honestly.
* Preserve the canonical entry decision separately from exit-policy experiments.
* Record gross points separately from costs and net results.

Where OHLC data cannot establish intrabar event ordering, classify the outcome as ambiguous rather than assuming a favourable result.

Shadow candidates must remain diagnostic only. They must never control broker orders or activate an unapproved paper-engine exit lifecycle.

9. Persistent trade journal and recovery

Complete the observation recorder using the repository’s existing storage conventions.

Persist at least:

* Observation ID and timestamp.
* Strategy and canonical setup ID.
* Exact contract and expiry.
* CE/PE and ITM rank.
* Opening High and Opening Low.
* Breakdown and recovery timestamps.
* Swing-high timestamp and price.
* Entry timestamp and hypothetical entry price.
* Structural trough.
* Candidate version and initial stop/target.
* Completed five-minute candle path.
* Each hypothetical stop update and its activation timestamp.
* Hypothetical exit timestamp, price and reason.
* Quotes, spreads, fill assumptions and costs, including their provenance.
* Data gaps, invalid data, ambiguous events and unresolved classifications.
* Observer health, errors and reconnection events.

Ensure:

* Idempotent writes.
* No duplicate signals after restart.
* No duplicate exits.
* Safe recovery from an interrupted write.
* Explicit separation of observed facts from simulated outcomes.
* No fabricated quote, fill or cost information.

Retain all qualifying observations, including losses, ambiguous events and incomplete paths.

10. Operational readiness and monitoring

Complete all offline-verifiable monitoring and operating procedures.

The observer must expose useful status information for:

* Authentication.
* Data-source health.
* Latest candle timestamp.
* Candle freshness.
* Missing intervals.
* Contract coverage.
* Signal counts.
* Duplicate and invalid events.
* Journal persistence.
* Reconnection state.
* Kill-switch state.
* Error counts.

Ensure that:

* Failures are visible.
* Missing critical data causes an explicit warning or safe abort.
* Reconnects are bounded and do not create duplicates.
* Shutdown is graceful.
* State recovery is deterministic.
* The operator can stop the process immediately.
* Logs are useful but do not contain secrets.

Do not claim unattended or persistent execution unless it is actually implemented and tested.

Do not automatically start a background process tonight and imply that it will be monitoring tomorrow.

11. Tests and independent verification

Inspect existing tests first and add tests only where coverage is missing.

Required test areas:

* Completed versus incomplete candles.
* Timestamp types and timezone conversion.
* Stale and missing data.
* Duplicate and out-of-order candles.
* Exact expiry, strike and contract selection.
* Missing CE/PE ITM2/ITM3 coverage.
* Causal swing-high detection.
* No-lookahead strategy processing.
* Strategy session boundaries.
* Duplicate-signal protection.
* Restart and persistence recovery.
* Trailing-stop activation timing.
* Same-candle stop/target ambiguity.
* Exactly-once exits.
* Shadow/broker separation.
* Authentication failure and fail-closed behaviour.
* Kill switch.
* Order-submission prevention.

Execute:

1. Focused regression tests.
2. Full repository test suite.
3. Syntax/compilation checks.
4. Configuration and safety-lock checks.
5. Secret-leak checks appropriate to the repository.
6. git diff --check.

Record the actual commands, pass/fail counts and failures.

Investigate failures instead of hiding, skipping or weakening tests. Do not claim that any check passed unless it was executed.

If a real session or external credential is needed for a check, label it UNVERIFIED rather than faking success.

12. Security and repository hygiene

Check:

* Safety defaults.
* Order-endpoint call graph.
* Secrets in tracked files and newly generated output.
* Sensitive logging.
* Dependency completeness.
* Unrelated file modifications.
* Unexpected changes to canonical strategy definitions.
* Accidental generated files.
* Test fixtures that contain sensitive information.

Do not print secret values during inspection.

Do not change external account settings or rotate credentials without authorization.

13. GitHub delivery

Inspect the current branch, working tree and remote before editing.

Keep changes restricted to the mission and necessary verified fixes.

Review the final diff and staged files for:

* Secrets.
* Unrelated changes.
* Altered canonical rules.
* Removed safeguards.
* Generated artifacts that should not be tracked.

Run required tests before committing.

If all appropriate checks pass and GitHub is already configured, commit the work and push to the existing main branch.

Do not force-push, overwrite unrelated work, bypass failing checks or commit credentials.

If a conflict, authentication issue or failed test blocks delivery, preserve the changes and report the exact blocker.

14. One master report only

Create exactly one new comprehensive human-readable Mission 11 report:

EKALAYAVA_MISSION11_MASTER_REPORT.md

Do not create separate Mission 11 implementation summaries, launch checklists, readiness reports or daily-report templates.

Keep source code, tests, necessary machine-readable data and existing historical reports in their proper locations. The restriction on one report applies to new Mission 11 documentation, not to necessary software artifacts.

The master report must contain:

Section 1 — Executive summary

* Completion status.
* What is ready for tomorrow.
* Remaining blockers.
* Explicit live-execution status.

Section 2 — Historical research baseline

* Existing data coverage.
* Recovered paths.
* Candidate counts and gross results.
* Why no exit policy is approved.
* References to existing research reports.

Section 3 — Repository changes

* Files modified and created.
* Verified defects and fixes.
* Existing components reused.
* Incomplete work.

Section 4 — Observer readiness

* Authentication and read-only access.
* Five-minute data handling.
* Contract selection.
* Freshness and continuity.
* Reconnection and restart.
* PASS, FAIL, BLOCKED or UNVERIFIED status for each capability.

Section 5 — Strategy and shadow engine

* Confirmation of canonical rules.
* Causality and no-lookahead tests.
* Candidate simulation.
* Stop-update timing.
* Ambiguity and post-exit target handling.
* Broker/order isolation.

Section 6 — Tests and security

* Exact commands.
* Focused and full-suite results.
* Compilation and diff checks.
* Safety-lock verification.
* Failures and untested cases.

Section 7 — Tomorrow’s operating instructions

* Pre-market checks.
* Exact preflight commands.
* Read-only authentication check.
* Fresh-data and contract-coverage checks.
* Exact observer start command.
* Health/log inspection commands.
* Safe-stop and recovery commands.
* End-of-session reconciliation.
* Abort conditions.

Every command must be derived from the actual repository and verified where possible. Do not invent commands or claim they work without testing.

Section 8 — Paper-observation protocol

* Required observations.
* Shadow simulation.
* Missing/ambiguous data treatment.
* Minimum of 100 qualifying signals over at least 60 trading sessions, whichever takes longer.
* Statement that this is an observation horizon, not a profitability guarantee or approval rule.

Section 9 — GitHub status

* Branch.
* Changed files.
* Commit hash.
* Push status.
* Delivery blockers.

Section 10 — Final milestone matrix

For every milestone, mark:

* COMPLETED — implementation and required offline verification genuinely finished.
* PARTIAL — some components are implemented but others remain.
* BLOCKED — a concrete dependency prevents completion.
* LIVE VERIFICATION REQUIRED — only a real market session can verify it.

Do not mark a milestone complete merely because a document says it is complete. Inspect the implementation and evidence.

15. Tomorrow’s live milestone must remain separate

Do not claim that tonight’s work completes:

* Real-session data freshness.
* Actual market-session contract availability.
* Real-time signal behaviour.
* Live-session reconnect and recovery.
* Real-world quote/spread behaviour.

These remain for tomorrow’s supervised, read-only session.

The observer must not submit orders during that session.

16. Credit-efficient execution order

Prioritize:

1. Safety and order-path isolation.
2. Critical observer defects.
3. Contract selection and data integrity.
4. Persistence, restart and recovery.
5. Shadow simulator correctness.
6. Automated tests.
7. Security and repository hygiene.
8. Tomorrow’s verified operating commands.
9. Single master report.
10. GitHub delivery.

Do not spend credits repeating successful historical recovery or creating unnecessary documentation.

If the budget becomes constrained, finish safety, testing, persistence and launch-critical items before cosmetic improvements.

Continue through all feasible tasks in this run. Do not stop after creating the gap list.

17. Final response

When finished, give a concise but complete summary of:

* Milestones completed.
* Milestones partial or blocked.
* Tests actually run and their results.
* Safety verification.
* Master report path.
* Exact preflight/start/stop commands.
* Commit and push status.
* The capabilities that still require tomorrow’s live market session.

The system must remain strictly read-only, research-only and paper-only. No exit policy is approved and no live execution is authorized.
