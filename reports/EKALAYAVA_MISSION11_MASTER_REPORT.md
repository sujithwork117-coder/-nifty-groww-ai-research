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

## 11. Final Offline Strategy Finalisation — 2026-10-13

### Outcome

The safely achievable offline work is complete. The seven experimental Ekalayava policies remain **research-only**; none is approved or activated. The canonical engine remains observation-only for Ekalayava, and L2L retains its existing option-premium entry/exit rules. No continuous observer was run for this finalisation and no real-session result is claimed.

Baseline before this mission: `main` at `f3bac63866352515e469684b17b4132697ee16fd`, equal to `origin/main`. This mission starts from the clean pulled baseline and preserves the historical source reports and datasets.

### Changed files

| File | Change |
|---|---|
| `app/paper_shadow.py` | Added an isolated, persisted seven-candidate shadow state machine. It accepts only canonical Ekalayava signals and completed option candles; candidate exits, ambiguity, data gaps, stop-update activation time and null quote/fill/cost fields remain separate from the canonical engine. |
| `app/paper_observer.py` | Advances the separate shadow book on the same validated option bars, initializes it only from canonical signals, persists it per contract/day, and exposes candidate states/errors in health. Shadow failures degrade observer health. |
| `app/paper_reconcile.py` | Added read-only journal/state/health reconciliation for both strategy signal states and all seven candidate states, candle integrity and gaps, candidate outcomes/points, null versus zero points, missing contracts and absent quote/fill/cost evidence. Supports the observer's parent-level health snapshot. |
| `tools/reconcile_paper_session.py` | Added deterministic JSON stdout and human stderr CLI; exits non-zero (`2`) on integrity failures without changing source records. |
| `app/journal.py` | Added candidate identity/state and explicitly hypothetical exit fields to the JSONL schema; actual quote, fill and cost fields remain null. Existing CRLF formatting is preserved. |
| `tests/test_paper_shadow.py` | Covers independent candidate processing, restart/idempotency, trailing-stop timing, ambiguous bars, gaps and invalid candles. |
| `tests/test_paper_observer.py` | Verifies seven candidate states per qualifying mock signal and visible/degraded health on shadow errors. |
| `tests/test_paper_reconcile.py` | Covers deterministic repeated runs, counts, ambiguity, partial paths, duplicate/malformed records, gaps, conflicting exits, zero versus absent points, date-scoped state layout, and CLI failure output. |

No historical data or prior research output was overwritten. Canonical strategy definitions and parameters were not changed. The shadow evaluator neither changes canonical signals nor creates broker instructions.

### Scorecard A — Software and research milestones

The denominator is the **14 top-level milestones** in the Mission 11 matrix above. The Mission 11 baseline had 8 complete, 2 partial, 2 blocked and 2 live-only.

| Final status | Count | Milestones / evidence |
|---|---:|---|
| Fully completed offline | **10** | Original 8: research baseline/reconciliation; canonical behavior preservation; read-only auth/profile preflight; candle ordering/completion; exact contract selection/no substitution; durable journal/restart; order-path isolation; Mission 11 report/delivery. Newly completed: isolated seven-candidate observer shadow workflow (focused observer/shadow tests); deterministic end-of-session reconciliation CLI (fixture tests, help and non-zero failure behavior). |
| Partially completed | **1** | Health/freshness/gaps/reconnect: offline error reporting and mocked bounded reconnect are tested; actual market-time freshness and provider reconnect remain unobserved. |
| Blocked by missing evidence | **1** | Real quote/spread/fill/transaction-cost evidence: no sourced, supervised paper quote/fill/cost dataset exists. |
| Requires actual live-session verification | **2** | Exact four-contract availability, advancing/fresh live candles and signals; real provider reconnect/restart/recovery. |
| **Total** | **14** | **10/14 complete (71.4%)**; 4 remain in the categories above. |

**Previous complete: 8/14. Newly completed in this mission: 2** (seven-candidate observer shadow integration; offline session reconciliation). The completed shadow milestone means the isolated software path is implemented and regression-tested; it does not assert real-provider readiness or strategy approval.

### Scorecard B — Historical strategy outcomes

All points below are **gross option-premium points**, not currency P&L. No actual transaction costs or executable fills are available. For the Ekalayava comparisons, each hypothetical cost scenario subtracts the stated per-round-trip cost from each of the 447 resolved outcomes; the scenarios are sensitivities, not fee estimates. The 447 denominator is 194 exact 2025 H2 entries plus 253 saved 2026 entry observations. The 2025 set has 192 complete and 2 partial paths; the saved 2026 set has 253 exact recovered paths. The saved 2026 entries were not all independently redetected. Candidate totals include both 2025 partial source paths; the existing ledger reports 447/447 simulated outcomes, with zero unresolved and zero excluded outcomes.

#### L2L — canonical Opening-High policy

The reproduced baseline is 361 setups: 203 eligible entries, 57 targets, 145 stops, 1 ambiguous outcome and 0 unresolved outcomes; 158 setups were skipped (157 already at/below stop and 1 already at/above target). The 202 resolved trades sum to **+237.45 option-premium points**, with 250.05 maximum drawdown on the equal-unit chronological resolved-event sequence. One skipped target-already-reached entry is not counted as a target. Under purely hypothetical round-trip costs of 0.5 and 1.0 premium points per resolved trade, the net sensitivity is +136.45 and +35.45 points, respectively; these are not measured fees or fill costs. The break-even uniform cost is about 1.18 points per resolved trade. The underlying NIFTY is used for contract selection/reference; the strategy's opening range, entry, stop, target and reported points are from the selected **option premium** candles. No forced session-end exit is introduced.

The existing chronological summaries vary by period: Jan–Jun 2026 +134.85 (n=147 resolved), Jul–Aug +81.40 (n=41), and incomplete Sep +21.20 (n=14). The baseline does not report a per-entry partial-path count (**UNKNOWN**); the separate coverage inventory records 1 partial and 178 missing/unselectable contract-days out of 740 expected, which is not a count of affected trades. Missing option coverage can suppress setups; Sep ends before the full requested period. These retrospective, coverage-dependent figures and the absence of measured costs do not establish robust net expectancy or live readiness.

#### Ekalayava — seven fixed candidate policies

`Evaluated` is the policy replay count, not the number of real paper trades. All 447 rows received a reported terminal simulation outcome; no candidate had an ambiguous terminal result, unresolved result or excluded entry in the fixed ledger. The two partial source paths remain flagged as partial/unverifiable input evidence for each policy.

| Candidate | Eligible / evaluated | Target | Stop | Ambiguous | EOD* | Unresolved | Partial paths | Gross points | Net @ 0.5 points/trade | Net @ 1.0 point/trade | 2025 Nov–Dec gross (n=69) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `A_B4_OPENING_HIGH_V1` | 447 / 447 | 164 | 243 | 0 | 40 | 0 | 2 | +685.55 | +462.05 | +238.55 | +167.25 |
| `A_B4_TP25_V1` | 447 / 447 | 197 | 232 | 0 | 18 | 0 | 2 | −1,476.05 | −1,699.55 | −1,923.05 | +148.20 |
| `A_STRUCTURAL_TROUGH_B4_TP25` | 447 / 447 | 281 | 160 | 0 | 6 | 0 | 2 | −440.14 | −663.64 | −887.14 | −7.36 |
| `B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1` | 447 / 447 | 112 | 331 | 0 | 4 | 0 | 2 | +278.10 | +54.60 | −168.90 | +1.25 |
| `C_B2_1R_V1` | 447 / 447 | 190 | 239 | 0 | 18 | 0 | 2 | −1,740.85 | −1,964.35 | −2,187.85 | +76.95 |
| `C_B2_1_5R_V1` | 447 / 447 | 154 | 265 | 0 | 28 | 0 | 2 | −1,289.90 | −1,513.40 | −1,736.90 | +118.22 |
| `C_B2_2R_V1` | 447 / 447 | 127 | 282 | 0 | 38 | 0 | 2 | −1,151.50 | −1,375.00 | −1,598.50 | +172.70 |

*EOD means experimental session-end exits; it is not part of canonical Ekalayava behavior. Candidate counts, target touches and simulated exits are not additive across policies.

The already-preserved [Guide 8 candidate counts](./ekalayava_guide8_candidate_counts.csv) and [per-observation outcomes](./ekalayava_guide8_candidate_trade_outcomes.csv) contain the existing split, subgroup, win-rate, mean/median, profit-factor, drawdown, streak, holding-time, MFE/MAE and exit-reason detail; the [Guide 9 B2 audit](./EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md) has the explicit B2 path and excursion diagnostics. These are the same historical populations and definitions summarized here, not newly generated or independently re-collected measurements.

The existing chronological slices do not establish a robust winner. For example, `A_B4_OPENING_HIGH_V1` is the aggregate gross leader, but the previously reported 2025 Jul–Aug training and Sep–Oct validation segments were −120.90 and −141.60, before +167.25 in the already-inspected Nov–Dec segment and +780.80 on the saved 2026 ledger. B2's +278.10 gross aggregate falls to +54.60 at a hypothetical 0.5-point cost and −168.90 at 1 point; its previously reported validation and incomplete-September periods were negative. The 2025 test, candidate selection and 2026 ledger have all been inspected; none is an untouched holdout. Costs, bid/ask, spread, slippage and real fills are not measured.

**Per-policy evidence classification: `RESEARCH ONLY — PROMISING BUT UNVALIDATED`** for the two gross-positive aggregates; `REJECTED — INSUFFICIENT OR UNSTABLE EVIDENCE` for the other five. None is eligible for exit approval or live trading. The seven rows contain historical signal observations only; this mission produced **zero real-session qualifying signals**. The four signals in observer tests are mock fixtures, not market observations.

### Observer shadow and session-reconciliation verification

The observer processes shadow bars separately from `PaperContractEngine`, using the same exact validated option stream; it initializes candidate states only after a canonical Ekalayava signal, records candidate-specific hypothetical levels/outcomes and keeps quote/fill/cost fields null. Stop changes from the lower-low proxy become active only on the following completed candle. Same-bar stop/target ambiguity and data gaps remain explicit. No continuous observer was started.

Command:

```sh
./.venv/bin/python -m tools.reconcile_paper_session data/paper_observer/YYYY-MM-DD
```

It reads the date-scoped journal and state files plus the observer health snapshot (stored one directory above by the current observer), detects signal/state mismatches, duplicate IDs/timestamps, out-of-order candles, five-minute gaps, incomplete paths and duplicate/conflicting terminal outcomes, and reports per-candidate counts/points and absent quotes/fills/costs. JSON is printed to stdout; the concise summary goes to stderr; integrity failures return exit status 2. Repeated fixture runs are deterministic and read-only. **No real observer session journal exists in `data/paper_observer`; therefore no real-session reconciliation result is claimed.**

### Tests and safety

Executed with workspace Python 3.14.2:

```text
pytest -q tests/test_paper_shadow.py tests/test_paper_reconcile.py tests/test_paper_observer.py tests/test_journal.py
28 passed

pytest -q
151 passed

python -m compileall -q app tests tools
passed

Pylance syntax checks: app/paper_shadow.py, app/paper_reconcile.py,
tests/test_paper_shadow.py, tests/test_paper_reconcile.py
no syntax errors

python -m tools.reconcile_paper_session --help
passed

ExecutionLock: EXECUTION_ALLOWED=False, PAPER_ONLY=True
passed
```

The existing report artifacts were used for historical reconciliation; no large simulation or data retrieval was repeated. No lint/type-check configuration was found beyond the repository's pytest setup. The source changes introduce no order API path. A read-only authentication/profile preflight was **not** repeated during this offline finalisation; repeat it tomorrow before observation. No order was submitted, modified or cancelled.

### Tomorrow-only supervised checks

Run only during the next market session, with the terminal visible:

```sh
./.venv/bin/python -c 'from app.config import CFG; from app.safety import ExecutionLock; print(f"EXECUTION_ALLOWED={CFG.execution_allowed}; PAPER_ONLY={CFG.paper_only}; KILL_SWITCH={CFG.kill_switch}"); ExecutionLock(CFG).assert_paper_only()'
./.venv/bin/python -m app.main --auth
./.venv/bin/python -m app.paper_observer
```

Before interpreting a signal, verify the actual session date/expiry, exact CE ITM2, CE ITM3, PE ITM2 and PE ITM3 symbols, `contract_coverage == "4/4"`, and empty `missing_contracts`. Confirm a completed 09:15 NIFTY opening bar, advancing and fresh five-minute timestamps for NIFTY and every selected option, no unexplained gaps/duplicates/stale/out-of-order events, healthy status, persisted health/journal, and seven candidate states per canonical Ekalayava signal. If any exact contract is absent, record incomplete coverage—never substitute.

Stop with Ctrl-C; confirm `STOPPED_BY_OPERATOR`, state and journal persistence, and (only after the observer has stopped) run:

```sh
./.venv/bin/python -m tools.reconcile_paper_session data/paper_observer/YYYY-MM-DD
```

Treat any failed safety/auth check, missing opening NIFTY candle, non-4/4 coverage, persistent degraded health, unexplained staleness/gap, persistence error or exhausted reconnect limit as an abort. A supervised observation is still paper-only and does not approve any exit lifecycle.

### Remaining blockers and delivery

The remaining work is exactly one offline-evidence blocker (real sourced quote/fill/cost observations) and two live-only milestones (actual date/contract/feed/signal verification and real provider reconnect/recovery); freshness/reconnect implementation remains partially complete until those observations exist. No candidate exit is selected. Readiness means the isolated software is prepared for a supervised read-only attempt **if** tomorrow's abort gates pass; it is not evidence of current live data quality or trading authorization.

The implementation and initial finalisation-report commit `9776fd0f40f9b106c5c5f9f4018440725e526fa8` was pushed to `origin/main` by a normal fast-forward from the verified baseline. This final delivery-status update is a report-only follow-up; its commit and the final `HEAD == origin/main` check are recorded in the task completion summary. No market-data or recovery artifacts were staged.

## 8. Terminal-first entry point (2026-10-13)

Added root-level `run_research.py` as the single offline-first command surface.
With no subcommand it verifies the paper-only lock, runs a synthetic seven-policy
shadow/reconciliation acceptance check, inventories local timestamped CSVs and
summarizes existing research evidence. It does not authenticate, request market
data, or start the observer. Explicit subcommands provide `doctor`, `test`,
`smoke-test`, `auth-check`, `study`, bounded `fetch-history`, supervised `live`,
and date-based `reconcile`.

`fetch-history` rejects invalid, over-31-day and out-of-recent-window requests
before authentication; it stores raw payloads separately from normalized data,
filters returned candles to the requested dates and session intervals, and
marks coverage complete only when all expected five-minute bars for supported
sessions are present. Empty responses remain partial. Raw Groww payloads and
generated reports are ignored by Git. Only mocked Groww responses were used to
test this path; no real authentication or historical request was made.

The 2026-10-13 terminal validation on Python 3.14.2:

```text
python run_research.py
PASS — offline safety, shadow/reconciliation smoke, data inventory and evidence summary

python run_research.py doctor
PASS — ExecutionLock; EXECUTION_ALLOWED=False; PAPER_ONLY=True; no network or observer

python run_research.py smoke-test
PASS — 7 candidate states, 7 target exits, canonical reconciliation integrity

python run_research.py test
157 passed

python run_research.py fetch-history --start 2025-01-01 --end 2025-01-14
Rejected before authentication; request was outside the supported recent history window

Order API source scan
No order-submission method calls found in app/, tools/, or run_research.py
```

Added six focused runner tests for CLI dispatch, mixed-timezone inventory,
request-range rejection, mocked history filtering/coverage, empty-response
handling and request grouping. Pylance reports no errors; compile validation
passed. The test and compile commands did not contact Groww.

**Not verified:** Groww auth/profile, real market-data retrieval, and `live`
observer operation were not run. The NSE calendar only establishes 2026
sessions. Use `python run_research.py` for the safe default; authentication,
fetching and supervised observation require explicit commands. `live` remains
paper-only and is not live-trading or strategy-exit approval.

### Follow-up verification — 2026-10-13

The pushed terminal workflow was subsequently checked from the synchronized
Windows checkout. `python run_research.py auth-check` succeeded for Groww
authentication and the read-only profile response; no credential or profile
values were displayed. The offline default and study commands completed, the
seven-candidate smoke/reconciliation acceptance test passed, and the complete
suite passed (**157 tests**). `compileall` and `doctor` passed with
`EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`, and `ExecutionLock` satisfied.
No historical data was fetched and no observer or order function was run.

The local CSV inventory still contains 2026-01-01 through 2026-09-29 only.
The saved 2025 H2 reports provide aggregate research evidence for 194 canonical
Ekalayava entries (192 complete paths, 2 partial), but the H2 raw manifest and
datasets are absent from this checkout; no 2025 L2L baseline is available.
2024 remains unavailable. The saved 2026 coverage audit reports 13,783 NIFTY
bars, 42,149 option bars, 561 complete and 1 partial contract-days, 178
missing/unselectable contract-days, and 112 fully usable / 55 partial / 18
unusable days. These are existing artifacts, not fresh downloads.

