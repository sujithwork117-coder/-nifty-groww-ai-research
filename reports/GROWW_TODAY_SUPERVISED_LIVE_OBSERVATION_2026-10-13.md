# Groww Supervised Live Observation — 2026-10-13

## Outcome

**Observer status: NOT RUN.** No continuous observer was started: [Current_guide_3](../Current_guide_3) requires the user to start it manually and only after the read-only and exact-contract gates pass. This session verified one bounded, read-only NIFTY cash-candle request during the NSE regular session; it did not validate an observer session, option contracts, option candles, signals, tickets, or paper positions. No broker order interface was invoked.

## 1. Time and session

- System time checked: **2026-10-13 08:11:06 UTC / 13:41:06 IST**. The market-calendar check at 13:41:18 IST returned a normal NSE session for 2026-10-13, 09:15–15:30 IST. The bounded contract/FNO check began at **13:45:00 IST**, still within that session.
- At the time of the check, the session was still open. The current regular-session close shown by the calendar is 15:30 IST.
- No observer start or stop timestamps exist because the observer was not run.

## 2. Repository state

- Branch: `main`, commit `313f083` (`Document live-market observation procedures`).
- Initial working tree: clean and synchronized with `origin/main`.
- No source code or existing artifacts were modified. This report is the only file added.

## 3. Safety flags and read-only boundary

Effective configuration was read before provider access: `execution_allowed=false`, `paper_only=true`, `kill_switch=false`; no `LIVE_ORDER_SUBMISSION_ENABLED` setting exists in application config, so it remained unset/false. Application-source search found no `LIVE_ORDER_SUBMISSION_ENABLED`, `place_order(`, `modify_order(`, or `cancel_order(` matches. The existing safety tests passed. The request and this report contain no credentials or account identifiers.

`GrowwPaperObserver.__init__` and `run_once`, plus `PaperContractEngine` initialization and `process_candle`, invoke `ExecutionLock`. The authentication factory returns the Groww client to the candle/catalog path. Static inspection of application code found no reachable broker order-submit/modify/cancel implementation. Reconnect recreates the read-only client; it does not change execution flags.

The flags were verified before the provider request. No application/configuration changes were made during the request. No actual order was placed, modified, or cancelled.

## 4. Timestamp/candle fix and bounded provider result

The final-bar fix in `app/paper_observer.py::_completed_session_bars` uses `pd.Timestamp(end) - timedelta(minutes=5)` after clamping to the session end. The regression `test_completed_session_bars_handles_the_final_bar_after_market_close` covers the Python `datetime` end value at 15:35 IST and returns the completed 15:25 candle.

At approximately 13:41 IST, read-only authentication and one bounded Groww NIFTY `CASH` historical-candle request succeeded. Retries were limited to one attempt and an alarm bounded the operation to 22 seconds. The requested interval was 13:30–13:40 IST. The provider returned 3 bars, stamped 13:30, 13:35 and 13:40 IST; response validation accepted OHLC, timestamps were unique and monotonic, and no data was written to disk.

At request time, 13:40 was still an open five-minute bucket. Applying `_completed_session_bars` at 13:41 IST returned only 13:30 and 13:35, excluding the open 13:40 candle. This confirms the live response shape and cutoff for this cash sample; it does not confirm the observer’s entire run path, opening range, or option stream.

A second bounded check used the documented opening-candle request to obtain the 09:15 NIFTY cash opening reference (**22,364.15**) and called the existing expiry/contract selector. Its catalog response selected expiry **2026-10-13** but returned only two exact contracts: `NSE-NIFTY-13Oct26-22300-CE` (CE ITM2) and `NSE-NIFTY-13Oct26-22500-PE` (PE ITM3). CE ITM3 and PE ITM2 were absent; the selector reported `PARTIAL_EXACT_CONTRACT_SET`. It did not substitute strikes or ranks. A source timestamp for the contract catalog was not supplied, so catalog freshness itself remains unverified.

One bounded FNO candle request per returned contract succeeded. Each returned three rows for the short 13:35–13:45 IST interval; after completed-candle filtering at 13:45, the latest complete bar for both was **13:40 IST**. These two fresh option streams do not fill the missing CE ITM3/PE ITM2 slots and do not make the four-contract universe valid.

## 5. Contract and strategy/ticket gates

- **Option-chain/contract catalog:** PARTIAL. The read-only expiry/catalog selector ran using the actual 09:15 underlying open. It returned only CE ITM2 and PE ITM3; CE ITM3 and PE ITM2 are missing. Catalog source timestamp/freshness is unavailable.
- **Option candles:** PARTIAL. Actual FNO candles arrived for the two selected contracts and both had a completed 13:40 IST bar at 13:45. No FNO candle was retrieved for either missing rank.
- **L2L:** canonical implementation and synthetic/replay tests were inspected/exercised, but no live option signal was observed. No opening option range, breakdown, entry, stop or target can be reported.
- **Ekalayava:** causal behavior has offline test coverage, but no live option signal was observed. No live swing-high/breakout observation can be reported. Its canonical exit remains undefined.
- **Proposed order tickets:** NOT SUPPORTED by a ticket builder in the application source search. Quantity/order type/risk/fill values are not inferred or invented; no ticket was created or validated.
- **Paper lifecycle and stop/target monitoring:** NOT RUN. No paper entry, hypothetical fill, exit, or broker-accepted order exists from this check.

The missing live option identity and option-candle validation are a critical gate; the observer was not started, and no signal or ticket was manufactured to demonstrate functionality.

## 6. Journal, persistence, and shutdown

Configured observer paths, from `GrowwPaperObserver`, are `data/paper_observer/<trading-date>/paper_journal.jsonl`, per-contract hashed JSON state files under the same date directory, and `data/paper_observer/observer_health.json`. No observer journal/state was created or modified by this bounded request; persistence is supported only by existing tests in this task. A process check found no `app.paper_observer` process running. There was no observer to stop, so clean observer shutdown is **NOT RUN**, not a pass.

## 7. Tests

Command actually run:

```text
/workspaces/-nifty-groww-ai-research/.venv/bin/python -m pytest -q tests/test_safety.py tests/test_safety_audit.py tests/test_paper_observer.py tests/test_contract_selection.py tests/test_paper_replay.py tests/test_journal.py tests/test_config_secrets.py
23 passed in 6.47s (exit code 0)
```

This covers the final-bar regression, mocked exact contract selection and observer restart/deduplication, L2L/Ekalayava replay behavior, journal persistence, configuration-secret handling, and safety checks. The live-data cutoff was additionally checked with `_completed_session_bars` against 13:30/13:35/13:40 timestamps at 13:41 IST; the 13:40 bucket was excluded. No full repository suite was run for this time-sensitive check.

## 8. Status matrix

| Item | Status | Evidence / blocker |
|---|---|---|
| Read-only safety | PASS | Effective execution flags, static order-call search, `ExecutionLock` boundaries, and safety tests. |
| Groww authentication | PASS | One bounded authentication succeeded; credential values were not displayed. |
| NIFTY market-data access | PASS | Actual in-session NIFTY CASH request returned three validated bars. |
| Option-chain access | PARTIAL | Catalog lookup returned a partial set; source freshness timestamp unavailable. |
| CE ITM2 selection | PARTIAL | Exact CE ITM2 symbol selected with a fresh completed FNO candle; catalog source freshness timestamp is unavailable. |
| CE ITM3 selection | BLOCKED | Exact current expiry/instrument and chain freshness not verified. |
| PE ITM2 selection | BLOCKED | Exact current expiry/instrument and chain freshness not verified. |
| PE ITM3 selection | PARTIAL | Exact PE ITM3 symbol selected with a fresh completed FNO candle; catalog source freshness timestamp is unavailable. |
| Completed five-minute candles | PASS | Actual request included the still-open 13:40 bucket; observer filter excluded it at 13:41 and retained 13:30/13:35. |
| Asia/Kolkata handling | PASS | System clock/calendar and returned timestamps were IST; completed-bar cutoff checked in IST. |
| L2L signal correctness | PARTIAL | Offline canonical replay/tests passed; no live option stream or signal. |
| Ekalayava signal correctness | PARTIAL | Offline causal replay/tests passed; no live option stream or signal. |
| Proposed-ticket validation | BLOCKED | No ticket builder and no verified option contract/quantity/order metadata; none created. |
| Paper lifecycle | NOT RUN | No live option signal or validated ticket; no simulated live paper order. |
| Stop/target monitoring | NOT RUN | No paper position was opened. |
| Journal persistence | PARTIAL | Existing journal/recovery tests passed; this live connectivity sample did not write observer journal records. |
| Clean shutdown | NOT RUN | Observer was not started; no observer process remains. |
| Live-session verification | PARTIAL | One actual in-session cash-data request and cutoff check succeeded; no supervised observer or FNO session. |

## 9. Changed files, risks, and next action

Changed files: this report only. No historical data was downloaded or saved, no optimization was run, and no source behavior or strategy rules were changed.

Remaining risks: CE ITM3 and PE ITM2 are missing from the returned catalog; catalog source freshness is unknown; no FNO candles exist for the two absent slots; no live signals, tickets, paper lifecycle, journal round trip, or supervised shutdown were validated. No conclusion about trading performance or execution readiness follows from these candle checks.

**Single safest next action:** keep the observer stopped for this session because the required exact four-contract universe is incomplete. Before a supervised run in a later session, use the documented read-only path to verify a fresh catalog containing all four exact CE/PE ITM2/ITM3 instruments and completed FNO candles for each.
