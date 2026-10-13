TASK: FULL TRADING-DAY REPLAY — NIFTY L2L AND ULTIMATE EKALAYAVA — 13 OCTOBER 2026

Analyse the complete NIFTY trading session for 13 October 2026 to determine whether the canonical Level-to-Level (L2L) or Ultimate Ekalayava strategies produced valid opportunities.

This is a bounded, data-driven replay task. Do not start the live observer or place real orders.

1. Inspect existing evidence first

Read the report:

GROWW_TODAY_SUPERVISED_LIVE_OBSERVATION_2026-10-13.md

Inspect the existing repository, strategy definitions, candle datasets, journals and replay implementation. Reuse existing components and tests; do not rebuild the project.

The earlier Groww checks established:

* NIFTY cash data was accessible.
* The opening reference was 22,364.15.
* CE ITM2 and PE ITM3 were returned by the contract selector.
* CE ITM3 and PE ITM2 were missing.
* The catalog’s source timestamp was unavailable.
* Only a short interval of option candles was verified.
* No complete observer session or live strategy signals were recorded.

These results do not establish whether today’s strategies had opportunities.

2. Data policy

Use only 13 October 2026 data relevant to the requested session.

First inspect existing local data. If required data is missing, use only the existing documented, read-only Groww market-data interface to retrieve today’s bounded session data, provided the API supports it.

Do not download unrelated historical data, search for unavailable older datasets, run broad historical backfills or repeat optimization grids.

Required data, where available:

* NIFTY underlying five-minute candles from the opening session through the close.
* Option candles for the exact selected NIFTY expiry and CE/PE ITM2/ITM3 contracts.
* Instrument identity, timestamps and enough OHLC data to evaluate the strategy rules.
* Actual session boundaries and data freshness.

Do not assume that the expiry or contract mapping observed at 13:45 was necessarily the correct mapping for the entire session without verification.

Never fabricate, interpolate or silently substitute missing candles, contracts, strikes or prices.

If any required data cannot be obtained, analyse the available subset and label the overall result INCOMPLETE. Do not claim full-day four-contract coverage.

3. Data-quality validation

Before replaying either strategy:

* Verify Asia/Kolkata timestamps.
* Verify the actual trading session and candle boundaries.
* Exclude incomplete candles.
* Remove or flag duplicate and out-of-order timestamps.
* Identify missing five-minute intervals.
* Verify OHLC validity.
* Check contract identity, expiry and strike mapping.
* Report coverage separately for each instrument.
* Prevent future data from influencing past signals.

Do not treat a missing candle as evidence that no opportunity occurred.

4. Replay canonical L2L

Use the existing canonical rules without modification.

1. The first completed five-minute candle establishes Opening High and Opening Low.
2. A completed red candle breaks below Opening Low.
3. Enter on the first subsequent completed green five-minute candle, at its close.
4. Entry window: 09:15–11:00 IST.
5. Stop-loss: Opening Low minus four premium points.
6. Target: Opening High.
7. Skip entry if the entry price is already at or beyond the target.
8. Do not introduce a forced end-of-day exit or arbitrary holding timeout.
9. Treat same-candle stop/target ambiguity explicitly.

Replay each eligible CE/PE ITM2/ITM3 contract independently where data is sufficient.

For every candidate setup, record:

* Contract and strategy version.
* Opening High/Low.
* Breakdown timestamp and price.
* First qualifying green-candle timestamp and close.
* Entry eligibility.
* Entry, stop and target prices.
* Whether the target or stop was reached after entry.
* Exit classification and any ambiguity.
* Missing-data or skipped-entry reason.

Do not combine signals from different contracts into one fictional trade.

5. Replay Ultimate Ekalayava

Use the canonical entry definition:

1. Establish the opening range from the first completed five-minute candle.
2. Observe the premium trading below Opening Low.
3. Identify the subsequent recovery/base.
4. Form a swing high using only information available at that time.
5. Identify entry on a breakout of that swing high before Opening High.
6. Do not require the entry candle to close above Opening High.

Use causal swing-high detection. Never use future candles to confirm an earlier signal.

The canonical exit lifecycle remains unresolved. Do not invent a stop-loss, target, trailing stop or forced exit.

Report:

* Valid setup and entry signals.
* Contract identity and timestamps.
* Swing-high reference and breakout evidence.
* Subsequent maximum favourable excursion (MFE).
* Subsequent maximum adverse excursion (MAE).
* Whether Opening High was later touched.
* Whether the available data is sufficient to evaluate the event.

An Opening High touch is not automatically a winning trade. Keep exit-policy experiments separate from canonical results.

6. Distinguish opportunities from completed outcomes

Use separate categories:

* Valid setup.
* Valid entry signal.
* Invalid or skipped setup.
* Data-blocked setup.
* Stop reached.
* Target reached.
* Ambiguous same-candle outcome.
* Unresolved at session end.
* Experimental exit-policy result.

Do not assume that a theoretical entry would have filled at the candle close in a real market. Label close-based entries and OHLC-based exits as replay assumptions.

Where the data cannot establish event order, report ambiguity instead of choosing the favourable outcome.

7. Performance and opportunity summary

For L2L, where complete data supports it, calculate:

* Setup count and valid entry count.
* Skipped-entry counts and reasons.
* Target, stop and ambiguous outcomes.
* Gross points under the canonical rules.
* Profit factor, if mathematically meaningful.
* Maximum chronological drawdown and longest losing streak, if a consistent trade sequence can be established.
* Results separately by CE/PE and ITM rank.
* Data coverage and unresolved cases.

For Ekalayava, report setup counts, valid entries, MFE/MAE and observed price events. Do not report canonical profitability without an approved and validated exit policy.

Do not present gross points as net profit. Do not invent brokerage, slippage, spreads, quantities, fills or capital assumptions.

8. Independent verification

Use the existing replay engine and add or run focused tests for:

* Opening-range initialization.
* L2L first-green entry.
* L2L entry-window boundaries.
* Causal Ekalayava swing-high detection.
* Incomplete-candle exclusion.
* Duplicate signals.
* Missing option candles.
* Same-candle ambiguity.
* Session-end unresolved positions.

Check the actual replay outputs against a small number of manually traceable candle sequences.

Do not rerun historical optimization or change canonical strategy parameters.

9. Save the report

Create:

TODAY_FULL_SESSION_L2L_EKALAYAVA_REPLAY_2026-10-13.md

Include:

1. Data sources and exact files/API requests used.
2. Coverage by instrument and time range.
3. Missing data and contract-selection limitations.
4. L2L opportunity timeline.
5. Ekalayava opportunity timeline.
6. Each candidate entry and its subsequent observed outcome.
7. Separate CE/PE and ITM-rank summaries.
8. Explicit replay and fill assumptions.
9. Test commands and actual results.
10. Whether the session is sufficiently complete to draw conclusions.
11. The single most useful next step.

Save any additional machine-readable replay output using existing project conventions without overwriting historical results.

10. Safety and final response

Keep:

* EXECUTION_ALLOWED=false
* PAPER_ONLY=true
* LIVE_ORDER_SUBMISSION_ENABLED=false

Do not submit, modify or cancel orders. Do not start an unattended observer.

At completion, answer:

* Did L2L produce valid opportunities today?
* Did Ekalayava produce valid opportunities today?
* At what timestamps and in which verified contracts?
* What happened to each candidate afterward?
* Which results are conclusive versus data-blocked?
* Was the complete session covered?
* What should be tested next?

Do not claim that the system learned a profitable strategy from a single day’s replay.
