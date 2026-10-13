# Ekalayava Mission 11 — Master Report

**Assessment date:** 2026-10-13
**Branch/base:** `main` at `d8c8c420d588508e50733f4272f9c1257dc7d2ec` before Mission 11 changes
**Scope:** Offline implementation, source and safety audit, tests, and read-only authentication/profile preflight. No continuous observer session was started.

## 1. Executive summary

**Mission status: PARTIAL — offline work completed; supervised market-session verification remains open.**

Ready for a supervised, read-only observation attempt:

- Execution remains disabled and paper-only. The effective configuration and `ExecutionLock` were checked.
- Groww authentication and its read-only profile endpoint succeeded in the preflight.
- The observer now reports candle freshness, underlying gaps, exact-contract coverage and selection facts; persists underlying and option OHLC candles with provenance; and exposes journal and reconnect status.
- Completed-candle ordering, duplicate persistence, missing intervals, invalid profile handling, bounded reconnect behavior, restart protection and order-method isolation have regression coverage.
- The existing Ekalayava entry is still observation-only when no exit buffer is configured. Research exits remain separate and experimental.

**Not ready for a claim of live-data or trading readiness.** Real-session freshness, tomorrow's exact contract catalog, signal behavior against market-time data, and live reconnect/recovery are unverified. A repository snapshot from 2026-10-13 showed only two of four requested exact contracts selected at its 13:45 cutoff; CE ITM3 and PE ITM2 were unavailable in that snapshot. Tomorrow's catalog must be checked afresh.

**Live execution: NOT AUTHORIZED.** No order was submitted, modified or cancelled. No exit policy is approved.

## 2. Historical research baseline

The current research reports and artifacts were inspected; historical recovery and optimization were not rerun.

- The 2025 H2 exact-option set has 194 canonical Ekalayava entries: 192 complete paths and 2 partial paths.
- The saved 2026 entry ledger has 253 observations, with 253 exact post-entry paths recovered by the bounded Guide 9 recovery. Recovery does not independently validate every 2026 entry decision.
- The combined candidate ledger contains 447 observations. The seven existing exit candidates were reconciled on the available paths; the separate B2 audit matched 447/447 outcomes, points and exit timestamps.
- `A_B4_OPENING_HIGH_V1` is the descriptive gross leader at +685.55 points (164 targets, 243 stops, 40 experimental session-end exits). Its 2025 training and validation slices were negative (−120.90 and −141.60); the aggregate is not evidence of stable net expectancy.
- `B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1` produced +278.10 gross points. A uniform hypothetical 0.622-point round-trip cost erases this gross result; this is a sensitivity, not a measured cost.
- Historical OHLC does not establish executable fills or intrabar event order. Fees, taxes, spreads, slippage, lot multipliers and account sizing are not reliable historical inputs. The comparisons are retrospective and the 2025 test segment is no longer untouched.

**Decision: no stop-loss/target exit policy is approved.** The positive descriptive candidate results do not justify policy selection or activation.

Source reports:

- [Final evidence and data coverage](EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md)
- [Guide 9 final research execution summary](EKALAYAVA_FINAL_RESEARCH_EXECUTION_SUMMARY.md)
- [Target/stop count reconciliation](EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md)
- [Guide 9 B2 trailing-proxy audit](EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md)
- [Paper-trading readiness and limitations](EKALAYAVA_PAPER_TRADING_READINESS.md)

The repository inventory also reports incomplete 2026 option coverage for Jan–Sep: 561 complete, 1 partial and 178 missing/unselectable of 740 expected contract-days (42,149 of 55,500 expected intervals). No 2022–2025 local intraday dataset was found outside the documented 2025 H2 set.

## 3. Repository changes

Mission 11 changes are limited to these source and regression-test files:

- `app/groww_data.py` — added optional strict chronological validation; session candle fetches now reject provider rows that arrive out of order, while general historical validation retains its existing sort behavior.
- `app/paper_observer.py` — records completed NIFTY and exact-option candles idempotently; adds underlying gap/freshness and per-option freshness status; persists contract-selection timestamp, exact contract list, strike ladder, reference price/candle, catalog observation time and rationale; exposes journal and reconnect status; clears prior-day selection status; and uses bounded reconnect attempts.
- `app/journal.py` — extends the JSONL field schema for candle OHLC/provenance, quote/cost facts and selection metadata. Missing quotes, fills and costs stay null; no values are fabricated.
- `app/groww_auth.py` — removes provider exception text and chained context from authentication failures to avoid leaking sensitive response content.
- `app/main.py` — validates the read-only profile response and no longer prints account segment details.
- Tests: `tests/test_groww_auth.py`, `tests/test_groww_data.py`, `tests/test_paper_observer.py`, and `tests/test_read_only_verification.py`.
- This file is the only new Mission 11 report.

Existing paper engines, exact daily selector, read-only Groww candle endpoints, persistent per-contract state and candidate research simulators were reused. Canonical strategy definitions and candidate parameters were not changed.

**Incomplete:** candidate exits are not run inside the live observer; real quotes/costs are absent; no supported end-of-session journal-reconciliation CLI was found. These limitations are not disguised as completed features.

## 4. Observer readiness

| Capability | Status | Evidence and limitation |
|---|---|---|
| Read-only authentication/profile | **PASS — preflight only** | `.venv/bin/python -m app.main --auth` succeeded and printed authentication/profile success and order execution disabled. It does not prove market data is fresh. |
| Five-minute candle parsing and timezone normalization | **PASS — offline** | Focused regression tests cover parsing and timezone behavior; session data uses completed five-minute bars. |
| Incomplete candle exclusion | **PASS — offline** | Observer tests verify an unfinished bucket is not processed. The final-bar-after-close behavior is covered separately. |
| Provider row ordering | **PASS — offline** | Live-session validation rejects out-of-order provider rows; historical validation keeps its previous sorting behavior. |
| Stale/missing/duplicate stream detection | **PASS — offline** | Freshness ages, underlying and option gap status, idempotent candle records and duplicate counters are exercised with fixtures. Real-session behavior remains unverified. |
| Exact CE/PE ITM2/ITM3 selector | **PASS — selector tests; live availability UNVERIFIED** | The selector uses the earliest non-expired catalog expiry and exact ladder strikes, reports missing ranks, and does not substitute. |
| Recent contract availability evidence | **PARTIAL — dated snapshot only** | `today_replay_data_coverage_2026-10-13.csv` and its opportunity file show two of four contracts selected through 13:45 on 2026-10-13; CE ITM3 and PE ITM2 were absent. This is not tomorrow's catalog. |
| Contract selection audit facts | **PASS — offline recorder** | Health and durable journal now carry selection time, exact symbols/expiry/strike/type/rank, NIFTY 09:15 reference price and candle time, catalog observation time, expected strikes/step and selection rationale. Provider catalog source time is not provided by the API. |
| Freshness and continuity during market hours | **LIVE VERIFICATION REQUIRED** | A bounded past-data check is not evidence of tomorrow's live-session freshness or latency. |
| Reconnect and restart | **PASS — mocked; LIVE VERIFICATION REQUIRED** | Bounded retries, idempotent journal records and state replay are covered offline. Real Groww disconnect/reconnect remains untested. |
| Durable health/journal writes | **PASS — offline** | Health snapshots use atomic replacement; journal records are idempotent JSONL appends with fsync. Operate only one observer per state directory. |
| Graceful operator stop | **PASS — source/tested path** | Ctrl-C handling writes `STOPPED_BY_OPERATOR`; do not use a hard kill as the normal stop method. |

One earlier market-data coverage snapshot is deliberately retained as a warning, not treated as a fixed issue: check tomorrow's `contract_coverage` and `missing_contracts` before interpreting any signal.

## 5. Strategy and shadow engine

### Canonical behavior

- **Level-to-Level:** preserves the completed opening candle range, completed red break below Opening Low, first subsequent completed green entry at close, 09:15–11:00 entry window, existing four-premium-point stop buffer, Opening High target, skip-already-breached behavior, same-candle ambiguity handling and no invented session-end exit.
- **Ekalayava:** preserves the causal swing-high/recovery entry logic and below-Opening-High entry condition. With no configured experimental buffer, the paper engine records observation/MFE/MAE and leaves the lifecycle unresolved; no realized Ekalayava P&L is generated.

No canonical strategy or approved exit lifecycle was added or changed. Unit/regression coverage and prior candle-by-candle replay artifacts cover chronological processing, duplicate/restart protection, no-lookahead entry timing, gap handling and ambiguity.

### Candidate simulator

The seven named exit candidates remain in the isolated offline research simulator and historical reconciliation workflow. Existing tests cover stop/target ambiguity, missing intervals, target-before-later-stop behavior, no reversal after a stop, and trailing-stop activation only after its source candle completes (effective on a later bar). OHLC that cannot establish event order stays ambiguous; a target touched only after exit is not counted as a win.

**PARTIAL:** this does not provide a live-observer shadow run of all seven candidates. The schema can hold stop updates and cost fields, but those candidate paths are not connected to observer execution. This separation is intentional: candidates remain diagnostic and cannot activate a paper-engine or broker exit.

### Order isolation

`ExecutionLock` passed with `EXECUTION_ALLOWED=False`, `PAPER_ONLY=True`, `KILL_SWITCH=False`. The source scan of `app/` and `tools/` found no `place_order`, `modify_order`, `cancel_order`, `submit_order` or `create_order` calls. A regression test asserts no place/modify/cancel order methods in application source; an observer test uses mocked methods to check that the observation workflow does not invoke order submission.

## 6. Tests and security

Executed on Python 3.14.2 using the workspace `.venv`:

```text
/workspaces/-nifty-groww-ai-research/.venv/bin/python -m pytest -q tests/test_paper_observer.py tests/test_journal.py tests/test_groww_auth.py tests/test_groww_data.py tests/test_read_only_verification.py tests/test_safety_audit.py tests/test_safety.py
28 passed

/workspaces/-nifty-groww-ai-research/.venv/bin/python -m pytest -q
136 passed

/workspaces/-nifty-groww-ai-research/.venv/bin/python -m compileall -q app tests
passed

/workspaces/-nifty-groww-ai-research/.venv/bin/python -m app.main --auth
Groww authentication: SUCCESS
Groww read-only profile: SUCCESS
Order execution: DISABLED

/workspaces/-nifty-groww-ai-research/.venv/bin/python -m app.main --help
passed
```

Safety-lock verification also passed with the effective configuration shown above. The order-call scan returned no matches. The changed `app/journal.py` uses repository-existing CRLF line endings; plain `git diff --check` flags the CR byte on added lines. The CRLF-aware check passed:

```text
git -c core.whitespace=cr-at-eol diff --check
passed
```

No test failures remain. The 136-test result is the current run; older research reports' 129-test result is historical, not the current suite count. Mocked tests do not establish real market feed freshness. No secrets were intentionally added, authentication errors suppress provider response text, and profile/account segment details are not printed. No real order API call was made.

## 7. Tomorrow's operating instructions

All commands below are for the current Linux workspace. Re-run the preflight on the day of observation; a prior successful profile check does not guarantee tomorrow's market data.

### Pre-market safety and authentication

```sh
/workspaces/-nifty-groww-ai-research/.venv/bin/python -c 'from app.config import CFG; from app.safety import ExecutionLock; print(f"EXECUTION_ALLOWED={CFG.execution_allowed}; PAPER_ONLY={CFG.paper_only}; KILL_SWITCH={CFG.kill_switch}"); ExecutionLock(CFG).assert_paper_only(); print("ExecutionLock=PASS")'
/workspaces/-nifty-groww-ai-research/.venv/bin/python -m app.main --auth
```

Both commands were executed successfully in this workspace. The first must show execution disabled and paper-only true. If the lock fails or authentication/profile fails, **do not start the observer**.

### Fresh feed and exact contract coverage

There is no separate verified live-feed preflight command. Start the supervised observer only during the session, keep its terminal visible, and inspect the resulting health snapshot before treating any output as a signal. Confirm `health` is healthy, `contract_coverage` is `4/4`, `missing_contracts` is empty, the selected expiry/symbols are for that trading date, and underlying/option candle ages and latest timestamps advance. If any exact rank is absent, it was not monitored; do not substitute another strike/expiry.

The 2026-10-13 partial snapshot showed only 2/4 exact contracts, so tomorrow's coverage must be checked rather than presumed.

### Start, inspect, stop and restart

Start only in a supervised market session:

```sh
/workspaces/-nifty-groww-ai-research/.venv/bin/python -m app.paper_observer
```

This exact entry point is derived from the module's `__main__`; it starts the continuous observer and has **not** been run tonight. It must remain read-only and visible.

In a second terminal, inspect the health snapshot and the current session journal (replace `YYYY-MM-DD` with the session date):

```sh
cat data/paper_observer/observer_health.json
tail -n 50 data/paper_observer/YYYY-MM-DD/paper_journal.jsonl
```

The snapshot includes authentication, health, exact contract coverage/selection metadata, candle ages/timestamps, gaps, signals, duplicate/invalid counters, journal status, reconnect attempts, errors and safety flags. Journal entries retain observed candles and observer/strategy events; quotes, fills and costs remain null until actual sourced evidence exists.

Stop safely with **Ctrl-C** in the observer terminal. The CLI persists `STOPPED_BY_OPERATOR`; do not use `kill -9` or start a second observer on the same state directory. If a supervised restart is necessary, confirm the first process has stopped and health/journal are intact, then run the same start command. Deterministic state plus idempotent journal identities prevent replayed bars/signals from being written as duplicates; live-session recovery still requires verification.

### End-of-session and aborts

No supported automated end-of-session reconciliation CLI was verified. Preserve `observer_health.json`, the date-scoped JSONL journal and terminal output; do not invent a reconciliation result. A future analysis must classify missing, ambiguous and unresolved records without fabricating prices or costs.

Abort/stop and do not interpret signals when safety settings fail, profile authentication fails, the opening underlying candle is missing, health remains degraded, candle ages/gaps are unexplained, the exact contract set is incomplete, persistence reports an error, or reconnect attempts reach the configured limit. Never respond to a data failure by enabling orders or substituting contracts.

## 8. Paper-observation protocol

For each observation retain the date and stable setup/event identity, exact symbol/expiry/strike/type/rank, selection time and rationale, reference NIFTY candle, opening range, breakdown/recovery/swing/entry facts, complete observed five-minute OHLC path, freshness and gaps, and all ambiguous/unresolved outcomes. Record each hypothetical candidate and its assumptions separately from canonical entry and observed facts. Capture quotes, spreads, fill assumptions and costs only with real source and retrieval provenance; null is correct when unavailable.

Shadow candidates remain offline diagnostics unless a separately reviewed, isolated paper-only integration is explicitly implemented. A stop update is effective only at its documented next-candle boundary. No candidate is approved by accumulating observations.

Continue a consecutive predeclared observation horizon of **at least 100 qualifying signals over at least 60 trading sessions, whichever takes longer**. This is an observation horizon, not a profitability guarantee, statistical approval threshold, exit-policy selection rule, or authorization to trade. Retain losses, partial paths, missing contracts, ambiguities and interrupted sessions.

## 9. GitHub status

- **Branch:** `main`.
- **Base before Mission 11 changes:** `d8c8c420d588508e50733f4272f9c1257dc7d2ec`; `origin/main` matched this base at the initial delivery check.
- **Implementation commit:** `9156edc` (`Complete Mission 11 observer hardening`), containing the source changes, tests and initial version of this report; pushed to `origin/main`.
- **Report delivery:** this final delivery-status update is included in a separate report-only follow-up commit, also pushed to `origin/main`.
- **Scope:** nine modified application/test files plus this single report; ignored market-data/recovery artifacts are not to be staged.
- **Delivery blockers:** none known; remote `main` was verified at the expected base before push.

## 10. Final milestone matrix

| Milestone | Status | Basis / remaining condition |
|---|---|---|
| Existing research baseline and seven-candidate reconciliation | **COMPLETED** | Inspected current reports/artifacts; no historical recovery or retuning repeated. No exit approved. |
| Canonical L2L and Ekalayava behavior preserved | **COMPLETED** | Existing definitions/engines reused; current full tests pass; no canonical rule changes. |
| Read-only auth/profile preflight | **COMPLETED** | Real read-only authentication/profile call succeeded; no market session implied. |
| Five-minute candle ordering/completion validation | **COMPLETED** | Offline tests cover completed buckets, timestamps and out-of-order provider rows; real feed remains unverified. |
| Exact daily option contract selection and no-substitution | **COMPLETED** | Selector and regression tests verify exact ladder/missing-rank behavior; today's actual catalog availability is a separate live check. |
| Durable candle/selection journal and restart idempotency | **COMPLETED** | Offline persistence, duplicate and recovery tests pass; real-session restart remains unverified. |
| Health, freshness, gaps, error visibility and bounded reconnects | **PARTIAL** | Offline status and mocked reconnect are implemented; real-session freshness/reconnect remains unverified. |
| Seven-candidate shadow execution inside observer | **PARTIAL** | Isolated deterministic historical candidate simulator exists and is tested; observer integration is not implemented and no broker/engine exit is activated. |
| Real quote/spread/fill/cost evidence | **BLOCKED** | Requires sourced supervised paper quote/fill data; no such evidence is available from this offline run. |
| Automated end-of-session reconciliation | **BLOCKED** | No supported CLI/workflow was verified; preserve journal for later explicit analysis. |
| Order-path isolation and safety lock | **COMPLETED** | Effective lock passed; source scan and tests show no order submission path. |
| Real-session contract availability/freshness/signal behavior | **LIVE VERIFICATION REQUIRED** | Must be checked in tomorrow's supervised read-only session; 2026-10-13 snapshot had 2/4 contracts. |
| Real-session reconnect/recovery | **LIVE VERIFICATION REQUIRED** | Mock coverage is not evidence of actual provider behavior. |
| Mission 11 report and GitHub delivery | **COMPLETED** | The implementation/report and report-only status-update commits are pushed to `origin/main`; final branch and clean-worktree checks follow. |
