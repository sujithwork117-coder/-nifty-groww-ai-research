# NIFTY L2L and Ultimate Ekalayava Session Replay — 2026-10-13

## Result and completeness

**Overall result: INCOMPLETE — intraday replay only through the last completed 13:45 IST candle.** The environment/calendar check at 13:52 IST showed the NSE normal session was still open (09:15–15:30 IST). The bounded same-day requests completed at 13:53:38 IST with request end 13:50; the 13:50 bucket had not completed and was excluded. No post-13:45 prices or full-day conclusion are available from this replay.

On the two exact contracts returned by the current selector:

- **L2L:** the PE ITM3 path produced a breakdown and first-green candidate, but the entry close (29.35) was already below the canonical stop (85.75), so it was skipped. The CE ITM2 path had no qualifying L2L entry through the cutoff. No valid L2L paper position was opened.
- **Ultimate Ekalayava:** the PE ITM3 path produced a causal entry observation at 10:25 IST. At the cutoff it remained unresolved under the canonical rules (which have no approved exit). Its observed MFE/MAE through 13:45 were +22.65/−34.25 points; Opening High had not been touched. The CE ITM2 path was invalidated because Opening High was reached before an Ekalayava entry.
- **Coverage is partial:** the selector reported CE ITM3 and PE ITM2 missing, and the expiry catalog had no source timestamp. No missing contract, candle, strike, price or signal was invented or substituted.

These are per-contract replay observations, not evidence of real order fills or profitability. **They do not establish the complete day’s opportunity count.**

## 1. Data source, requests, and safety

The prior supervised-observation note is [`GROWW_TODAY_SUPERVISED_LIVE_OBSERVATION_2026-10-13.md`](./GROWW_TODAY_SUPERVISED_LIVE_OBSERVATION_2026-10-13.md). It records earlier same-day cash/catalog checks and the missing CE ITM3 and PE ITM2 slots.

For this replay, today-only data was retrieved from the existing read-only Groww integration (`authenticate`, `get_session_candles`, `get_expiries`/`get_contracts` through `select_daily_itm_contracts`). The request bounds were **2026-10-13 09:15–13:50 IST**:

- NIFTY `CASH` candles.
- One current expiry/contract-catalog lookup, ranked from the actual 09:15 NIFTY cash open.
- `FNO` candles only for the exact contracts returned by the selector: `NSE-NIFTY-13Oct26-22300-CE` (CE ITM2) and `NSE-NIFTY-13Oct26-22500-PE` (PE ITM3).

The request returned 56 rows per available stream. The final row at 13:50 was not complete at retrieval and was excluded, leaving 55 completed candles per stream, from 09:15 through 13:45 IST. Data remained in memory; raw candles were not persisted. No historical backfill, unrelated-date download, optimization grid, observer process, or broker order interface was used.

Effective flags at preflight were `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`, `KILL_SWITCH=false`; the application has no `LIVE_ORDER_SUBMISSION_ENABLED` setting, and it remained unset/false. No order was placed, modified, or cancelled.

## 2. Calendar, identity, and candle quality

The repository calendar identified 2026-10-13 as a normal NSE trading day, 09:15–15:30 IST. Timestamps were converted to Asia/Kolkata. Provider validation checked required columns, timestamp parseability, duplicate timestamps and OHLC consistency; the returned frames were sorted chronologically. The completed-bar filter excluded the still-forming 13:50 candle.

| Stream | Exact identity | Expiry / rank | Raw / complete bars | Completed range IST | Missing intervals from 09:15 | Status |
|---|---|---|---:|---|---:|---|
| Cash | NIFTY | — | 56 / 55 | 09:15–13:45 | 0 | Partial-session data; ongoing session |
| Option | NSE-NIFTY-13Oct26-22300-CE | 2026-10-13 / CE ITM2 | 56 / 55 | 09:15–13:45 | 0 | Exact selector result; catalog freshness timestamp unavailable |
| Option | NSE-NIFTY-13Oct26-22500-PE | 2026-10-13 / PE ITM3 | 56 / 55 | 09:15–13:45 | 0 | Exact selector result; catalog freshness timestamp unavailable |
| Option | Not selected | 2026-10-13 / CE ITM3 | 0 / 0 | — | — | Missing from exact catalog selection; blocked, no substitute |
| Option | Not selected | 2026-10-13 / PE ITM2 | 0 / 0 | — | — | Missing from exact catalog selection; blocked, no substitute |

The actual opening reference was 22,364.15. The selector chose expiry 2026-10-13 and returned only the two identities above, with `PARTIAL_EXACT_CONTRACT_SET`. The source timestamp/freshness of that expiry/contract catalog could not be established. Completeness applies only to the received candles through the cutoff; it does not imply that the full session is complete or that the two missing contracts had no opportunity.

Machine-readable coverage is in [`today_replay_data_coverage_2026-10-13.csv`](./today_replay_data_coverage_2026-10-13.csv).

## 3. Replay method and assumptions

Each available option symbol was replayed independently, in timestamp order, one completed candle at a time, through `app.paper_replay.replay_contract_day` and the existing `PaperContractEngine`. The engine consumes no future candle when producing an earlier signal. It initializes opening high/low from the 09:15 option candle, rejects incomplete bars, suppresses duplicate timestamps, and disables entries on missing intervals.

The replay used the configured strategy version `nifty-paper-v1`.

L2L used canonical rules: first completed option candle for opening range; completed red candle below opening low; first subsequent completed green candle inside the 09:15–11:00 window; entry at its close; stop = opening low −4; target = opening high; skip if entry is at/beyond stop or target. There is no forced EOD exit. Any hypothetical close-based entry or OHLC threshold event is a replay convention, not an assured executable fill. A same-candle stop/target touch is ambiguous.

Ekalayava used the existing causal swing rule and recorded an entry observation only when a later completed candle broke and closed above the previously observed swing high, before reaching opening high. No canonical stop or exit was added. MFE/MAE are OHLC excursions from post-entry completed candles through 13:45 only.

## 4. L2L results by verified contract

### CE ITM2 — NSE-NIFTY-13Oct26-22300-CE

Opening High/Low were **194.65 / 63.80**. Through 13:45 there was no qualifying completed red opening-low breakdown followed by a subsequent qualifying first-green entry within the entry window. Thus the verified subset had no L2L setup/entry for this contract through the cutoff.

### PE ITM3 — NSE-NIFTY-13Oct26-22500-PE

Opening High/Low were **216.05 / 89.75**.

| Event | IST | Evidence |
|---|---|---|
| Red breakdown | 09:20 | Completed red candle traded below opening low. |
| First subsequent green / candidate entry | 09:55 | Completed green close at **29.35**. |
| Canonical stop / target | — | Stop **85.75**; target **216.05**. |
| Entry classification | 09:55 | **Skipped: `SKIPPED_SL_ALREADY_BREACHED`**, because 29.35 ≤ 85.75. No paper position was opened. |

The observed candidate is not a valid entry under the canonical stop rule. No realized outcome or P&L is assigned.

The other two exact ITM ranks were unavailable, so these contract-specific results do not establish a whole-universe L2L count. Counts by verified data: one candidate first-green signal skipped, zero valid entries, zero stops/targets/ambiguous exits, zero resolved trades. Profit factor, drawdown and losing streak are not meaningful with no resolved L2L trade.

## 5. Ultimate Ekalayava results by verified contract

### CE ITM2 — NSE-NIFTY-13Oct26-22300-CE

Opening High/Low were **194.65 / 63.80**. The replay reached the opening-high level before a causal Ekalayava entry could form (`TARGET_REACHED_BEFORE_ENTRY`). No canonical Ekalayava entry was emitted for this contract through the cutoff.

### PE ITM3 — NSE-NIFTY-13Oct26-22500-PE

Opening High/Low were **216.05 / 89.75**.

| Event | IST | Evidence |
|---|---|---|
| Opening-low breakdown | 09:20 | Completed candle traded below opening low. |
| Saved causal swing high | 10:20 | Reference **36.15**, formed using prior completed bars only. |
| Structural trough before breakout | 09:55 | Lowest observed sequence low **26.15** through the bar before breakout; descriptive, not an adopted stop. |
| Breakout / entry observation | 10:25 | Completed candle broke and closed above 36.15; close **43.55**, still below opening high 216.05. |
| Excursions through cutoff | Through 13:45 | MFE **+22.65**, MAE **−34.25** premium points. |
| Opening-high observation | Through 13:45 | No touch recorded. |
| Canonical lifecycle | As of 13:45 | **Unresolved**; no canonical stop, target exit or realized P&L. |

This is a valid canonical entry observation on the verified contract stream, not a completed trade. It remained unresolved at the partial-session cutoff. Later same-day movement after 13:45 is unknown here.

CE ITM3 and PE ITM2 are data-blocked, not “no signal.” Exit-policy experiments are not used to relabel the canonical Ekalayava observation as a win or loss.

Machine-readable per-contract opportunity records are in [`today_replay_opportunities_2026-10-13.csv`](./today_replay_opportunities_2026-10-13.csv).

## 6. Independent tests and manual trace

Command:

```text
/workspaces/-nifty-groww-ai-research/.venv/bin/python -m pytest -q tests/test_live_listener.py tests/test_paper_replay.py tests/test_paper_observer.py tests/test_paper_backtest.py tests/test_paper_engine.py tests/test_contract_selection.py tests/test_groww_data.py tests/test_nse_calendar.py tests/test_journal.py tests/test_safety_audit.py tests/test_safety.py
52 passed in 1.44s (exit code 0)
```

The selected tests cover opening-range initialization, L2L first-green entry and prefix replay without future leakage, Ekalayava causal swing breakout, final/incomplete-candle exclusion, duplicates/restart, missing option data/gaps, same-candle ambiguity, session-end unresolved state, exact contract selection, journal recovery, and execution safety. The live replay was also manually checked against the returned per-contract engine state: PE ITM3 L2L candidate entry 29.35 versus stop 85.75 was skipped; PE ITM3 Ekalayava used the 10:20 swing value 36.15 and emitted only at the later 10:25 breakout.

## 7. Conclusion, limitations, and next step

As of the available data cutoff, the verified PE ITM3 had one L2L candidate that was invalid under the canonical stop and one valid Ekalayava entry observation that remained unresolved. The verified CE ITM2 had no valid entry for either strategy through cutoff (L2L had no qualifying breakdown sequence; Ekalayava was invalidated when Opening High preceded entry). The two unselected ITM ranks are blocked, not negative results.

The **complete 13 October session was not covered**: the session was active during retrieval; candles after 13:45 were not yet complete/available; two exact option ranks were missing; and the catalog did not expose a freshness timestamp. No full-session strategy conclusion, profitability claim, or canonical Ekalayava P&L is justified.

No proposed order ticket was built or validated; no order was sent. No paper position was journaled. The replay used the in-memory strategy engine and the two available option streams only; no journal or historical research file was overwritten.

**Single most useful next step:** after the 15:30 IST session close, request only 13 October’s completed session candles again through the documented read-only interface, re-run exact contract selection without substituting missing ranks, and complete the full-day replay only for contracts with verified identities and adequate complete data. If CE ITM3/PE ITM2 remain unavailable or catalog freshness cannot be established, keep the full-universe result explicitly incomplete.
