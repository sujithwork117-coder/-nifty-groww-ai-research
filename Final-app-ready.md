FINAL MISSION — UNIFIED NIFTY RESEARCH + GROWW HISTORICAL DATA + LIVE PAPER OBSERVATION MACHINE

Repository: sujithwork117-coder/-nifty-groww-ai-research, branch main.

I have limited coding-agent credits remaining. Implement this efficiently by reusing the existing application. Do not rebuild working strategy engines, repeat expensive research, download unnecessary datasets, or call external LLMs.

Objective

Deliver one reliable Python entry point, run_research.py, that operates independently of AI coding agents during normal use.

It must support:

1. Offline historical study.
2. Read-only Groww connection and authentication.
3. Historical candle discovery and retrieval for 2024, 2025 and 2026, subject to actual API availability, limits, permissions and returned data.
4. Reproducible historical analysis of Level-to-Level and Ekalayava.
5. Evaluation of all seven existing Ekalayava exit candidates.
6. Supervised live-session paper observation tomorrow.
7. Persistent journals, health monitoring, session reconciliation and final reports.

It must never place, modify or cancel real broker orders.

1. Inspect and reuse the existing implementation

Inspect the actual current repository, Git status, configuration, README, strategy engines, Groww data/authentication modules, contract selector, paper observer, shadow evaluator, reconciliation CLI, historical reports and available datasets.

Reuse the existing implementations, including app/period_research.py, app/paper_observer.py, app/paper_shadow.py, app/paper_reconcile.py and tools/reconcile_paper_session.py, wherever appropriate.

Do not create duplicate engines or conflicting journal formats.

Preserve all canonical strategy definitions, historical artifacts, credentials and existing research results.

2. One entry point and simple terminal commands

Implement run_research.py at the repository root.

Required commands:

* python run_research.py — safe offline default: diagnostics, smoke test, available-data inventory and historical analysis.
* python run_research.py study --years 2024 2025 2026 — historical analysis.
* python run_research.py fetch-history --start YYYY-MM-DD --end YYYY-MM-DD — explicitly requested, bounded, read-only historical data retrieval.
* python run_research.py doctor — environment and safety diagnostics.
* python run_research.py test — full automated test suite.
* python run_research.py smoke-test — offline end-to-end acceptance test.
* python run_research.py auth-check — read-only Groww authentication/profile check.
* python run_research.py live — supervised, read-only market-session observer.
* python run_research.py reconcile --date YYYY-MM-DD — reconcile a completed observer session.
* python run_research.py --help — show all supported commands.

Historical analysis must not require Groww authentication or network access when the required data is already local.

Historical downloads must require an explicit date range, respect documented API limits and permissions, and use only the existing read-only market-data endpoints. Do not make unlimited or redundant API requests.

3. Groww authentication and historical data

Use the existing app/groww_auth.py and app/groww_data.py implementations.

The auth-check command must:

* Verify the existing configured credentials.
* Validate the read-only profile response.
* Avoid printing tokens, secrets or sensitive account details.
* Fail safely if authentication or profile validation fails.

The fetch-history command must:

* Inspect existing local data first.
* Fetch only requested missing intervals where supported.
* Record source, instrument, date range, retrieval time, row count and coverage.
* Validate timestamp order, timezone, duplicate rows, OHLC consistency and five-minute candle completeness.
* Preserve missing intervals as missing.
* Save raw and derived outputs separately with provenance.
* Resume safely without duplicating records.
* Report API restrictions or unavailable historical periods accurately.

Do not assume Groww provides complete historical option candles for all of 2024, 2025 and 2026. Verify what the API actually returns. If a year or contract is unavailable, report the limitation rather than inventing data.

Do not download the entire three-year history automatically on every run. Use explicit fetch requests and incremental retrieval.

4. Historical strategy study

Use the canonical five-minute L2L and Ekalayava implementations without changing their rules.

Evaluate all seven existing Ekalayava candidates using the existing definitions and isolated shadow evaluator.

Report:

* Available data and coverage by year.
* Eligible signals and evaluated entries.
* Target exits, stop exits, ambiguous outcomes, partial paths and unresolved outcomes.
* Gross points under the documented point convention.
* Drawdown, losing streak and other metrics only where the data supports them.
* Results by year, CE/PE, ITM rank and entry time where sample sizes permit.
* Clearly labelled hypothetical transaction-cost sensitivity.
* Chronological training/validation/test results only where the split is defensible.
* Missing periods, conflicts with previous reports and unresolved discrepancies.

Do not count the same entry repeatedly as a new signal merely because it is evaluated under seven candidate exits.

Do not select an exit policy solely because it has the highest aggregate gross points. None is automatically approved for live trading.

5. Supervised live mode for tomorrow

The live command must use the existing app.paper_observer.py and run only after all mandatory preflight checks pass.

Before startup:

1. Verify the current trading date and relevant session calendar.
2. Verify EXECUTION_ALLOWED=False.
3. Verify PAPER_ONLY=True.
4. Pass the existing execution safety lock.
5. Pass read-only Groww authentication and profile checks.
6. Verify the selected expiry and exact requested contracts.
7. Confirm that all four requested contracts are available: CE ITM2, CE ITM3, PE ITM2 and PE ITM3.
8. Confirm that the observer can retrieve the completed opening NIFTY candle and valid five-minute option candles.

During the session:

* Process completed five-minute candles only.
* Preserve chronological ordering and timezone correctness.
* Record NIFTY and option candle freshness and gaps.
* Persist strategy observations, candidate states, health information and errors.
* Keep all seven Ekalayava shadow candidates separate from canonical strategy state.
* Maintain durable state and duplicate/restart protection.
* Use bounded reconnects.
* Expose missing contracts and degraded health clearly.
* Never substitute another strike or expiry.
* Never fabricate fills, quotes, costs or missing candles.

The process must remain visible and supervised. It must not automatically start overnight or run indefinitely outside its intended session.

If any required contract is missing, health is degraded, authentication fails, the opening candle is absent, persistence fails or the reconnect limit is exhausted, stop or degrade safely and report the reason.

No real order-submission code may be added.

6. End-of-session reconciliation

After a live session, the existing reconciliation command must report:

* Actual observations and canonical signals.
* Shadow candidate outcomes.
* Missing and duplicate records.
* Data gaps and incomplete paths.
* Ambiguous and unresolved outcomes.
* Health and reconnect incidents.
* Missing quote, fill and transaction-cost evidence.
* Final output file locations.

It must be deterministic, read-only and safe to rerun.

7. Single-command historical workflow

The default python run_research.py command must run the offline workflow only.

It must:

* Perform safety diagnostics.
* Run a bounded smoke test.
* Inventory local data for 2024–2026.
* Run supported historical analysis.
* Produce timestamped JSON and Markdown reports.
* Print the summary and exact output paths.

It must not fetch network data or start the live observer by default.

8. Tests and delivery

Run:

* The complete existing test suite.
* The new offline smoke test.
* Compilation checks.
* The execution safety lock.
* The historical analysis on the data actually available locally.
* Mocked observer and reconciliation tests.
* A source audit confirming no order-submission path exists.

Do not claim mocked tests prove live Groww reliability.

Fix regressions introduced by this mission and rerun the affected tests and complete suite. Do not claim zero possible errors.

Update the README with copy-pasteable commands and troubleshooting instructions. Update the existing master report with actual implementation, test, data coverage and safety evidence.

Do not stage credentials, private market data or recovery artifacts. Commit and push only if checks pass and the remote can be updated safely. Never force-push.

9. Final response

Report:

* Files changed.
* Actual tests passed.
* Exact historical coverage available for each year.
* Whether Groww authentication was actually tested.
* Whether requested historical downloads succeeded or were limited.
* The exact command for historical study.
* The exact command for tomorrow’s live paper observation.
* Required live-session checks and abort conditions.
* Safety-lock status.
* Verified commit/push status.

Implement and verify the working application. Do not return only a plan.
