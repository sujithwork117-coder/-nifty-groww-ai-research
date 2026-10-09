MASTER FINALIZATION PROMPT — NIFTY L2L + EKALAYAVA
===================================================

You are the final research, engineering, validation, and paper-trading-readiness agent for this repository.

GOAL
----
We are now close to finalizing the NIFTY trading research system.

Your job is to complete the remaining research for BOTH canonical strategies:

1. LEVEL-TO-LEVEL (L2L)
2. ULTIMATE EKALAYAVA

Use the existing 9-month Jan-Sep 2026 dataset and existing research outputs wherever possible.

IMPORTANT:
DO NOT waste time trying to reconstruct a handful of missing/incomplete contract-days.

If data for a particular day/contract is unavailable, incomplete, or unusable:

    SKIP THAT DAY/CONTRACT CLEANLY
    DO NOT RETRY IT REPEATEDLY
    DO NOT block the research
    MOVE immediately to the next usable trading day/contract.

We care about extracting robust conclusions from the large amount of usable data already available.

Do NOT spend the run chasing perfect dataset completeness.

===================================================
SECTION 1 — ABSOLUTE SAFETY RULES
===================================================

This project remains PAPER-ONLY.

NEVER:
- place a real order
- modify a real order
- cancel a real order
- enable live trading
- introduce broker order APIs
- introduce real execution credentials into source code
- print API secrets
- commit secrets

The system must remain:

    EXECUTION_ALLOWED=false
    PAPER_ONLY=true

Groww market-data APIs may be used read-only.

Any "live" work in this task means:

    LIVE MARKET DATA OBSERVATION
    + LIVE PAPER SIGNAL GENERATION
    + PAPER TRADE JOURNALING

It does NOT mean real-money trading.

===================================================
SECTION 2 — SOURCE OF TRUTH
===================================================

Do NOT silently modify canonical strategy entry definitions.

Read and respect:

NIFTY_Strategy_Definitions_Level_to_Level_Ekalavaya.md

Canonical L2L:

- NIFTY only
- CE and PE
- maximum 2nd/3rd ITM
- 5-minute candles
- Opening first 5-minute high/low
- Premium breaks below Opening Low with a red candle
- FIRST subsequent green 5-minute candle = entry
- Entry at completed green candle close
- No extra confirmation
- No lookahead
- SL = Opening Low - 4 points
- Target = Opening High
- Current execution window: 09:15-11:00
- 5-minute candle remains the signal/entry resolution

Canonical Ekalayava:

- NIFTY only
- CE and PE
- maximum 2nd/3rd ITM
- 5-minute candles
- Opening first 5-minute high/low
- Premium comes below Opening Low
- Reversal/base develops
- Relevant price-action / reversal structure forms
- Swing high forms during recovery
- Premium breaks the swing high
- Entry occurs on the swing-high breakout before Opening High
- No requirement that the entry candle close above Opening High
- Causal swing detection only
- No lookahead
- No unrelated indicators

Do not replace these definitions with a new strategy.

===================================================
SECTION 3 — DATA USAGE POLICY
===================================================

Use the EXISTING downloaded Jan-Sep 2026 data.

Do NOT start a massive new data download unless absolutely required by a missing implementation dependency.

Do NOT repeatedly investigate missing days.

For every research calculation:

IF required underlying/option data exists and is sufficiently complete:
    USE IT.

IF a required contract/day is missing or unusable:
    SKIP IT.
    Record it once in a compact coverage summary.
    Continue.

DO NOT:
- repeatedly retry missing contracts
- stop the entire experiment because of one missing day
- spend the majority of compute trying to improve historical completeness
- fabricate candles
- interpolate missing candles
- fill missing OHLC data
- treat unavailable data as a loss or a win

The purpose is to maximize useful research from the data that DOES exist.

Clearly state coverage in reports, but do not let missing data dominate the run.

===================================================
SECTION 4 — L2L FINAL RESEARCH
===================================================

The existing L2L target-timing research already established:

- 361 setups
- 203 resolved
- 58 targets
- 145 SL
- 157 skipped
- 1 ambiguous
- target rate approximately 28.6% among resolved
- 14/58 targets in first 5m
- 25/58 within 10m
- 34/58 within 15m
- 39/58 within 30m
- 49/58 within 60m
- 57/58 within 90m
- one around 110-115m

DO NOT simply rerun the same report.

Use the existing results.

Perform the FINAL L2L validation needed for paper-trading readiness.

Specifically:

A. Verify canonical entry logic in code.

B. Verify:
   opening candle
   red breakdown
   first subsequent green candle
   entry at completed candle close

C. Verify:
   no same-candle lookahead
   no future candle leakage
   no accidental second-green entry
   no duplicate signals

D. Keep:
   SL = Opening Low - 4
   Target = Opening High

E. Analyze target behavior using the existing 9-month results.

Do NOT change the entry timeframe.

Do NOT conclude that every trade should automatically be held 90 minutes.

Instead document:

- fast target behavior
- median target timing
- target timing distribution
- late target behavior
- behavior by CE/PE
- behavior by ITM2/ITM3
- behavior by entry time
- behavior by month where sample size allows

The purpose is to understand post-entry behavior, not overfit a timeout.

Also explicitly handle the previously identified edge case where the entry is already at/above the target.

That must NOT be incorrectly treated as a normal profitable target event.

Create/update a final L2L report:

reports/L2L_FINAL_VALIDATION.md

and, if the repository uses JSON research artifacts:

reports/L2L_FINAL_VALIDATION.json

Save the important numerical conclusions into:

RESEARCH_STATE.md

===================================================
SECTION 5 — EKALAYAVA FINAL 9-MONTH RESEARCH
===================================================

THIS IS THE MOST IMPORTANT REMAINING RESEARCH TASK.

Use the existing Jan-Sep 2026 Ekalayava data.

We have approximately 9 months of observed Ekalayava setups.

Do NOT stop because some individual contract-days are missing.

Use every valid Ekalayava setup available.

We need to FINALIZE the practical Ekalayava exit model.

Research BOTH:

1. STOP LOSS
2. TARGET

---------------------------------------------------
5A — EKALAYAVA STOP-LOSS RESEARCH
---------------------------------------------------

The intended Ekalayava SL concept is NOT:

- Opening Low
- arbitrary fixed rupee stop
- automatically below the breakout candle
- random percentage stop

The intended concept is:

    protective SL below the relevant price-action / reversal structural low

Use the 9-month dataset to determine the most robust executable structural-low definition.

For each Ekalayava setup, identify causally available structure before/at entry.

Study candidate structural anchors such as:

- reversal/base low
- lowest low of the causal reversal structure
- last meaningful swing low before breakout
- breakout candle low
- other structurally justified causal lows already represented in the strategy logic

DO NOT use future candles to define the SL.

For each candidate:

calculate, where data permits:

- entry price
- structural low
- distance from entry to structural low
- MAE after entry
- MFE after entry
- whether the structural low was subsequently revisited
- whether price reached Opening High
- whether candidate SL would have been hit before Opening High
- time to SL
- time to Opening High
- excursion distributions
- side: CE/PE
- ITM2/ITM3
- entry-time bucket
- monthly behavior

Then compare candidate structural definitions.

The objective is NOT to select the candidate with the best backtest result blindly.

The objective is to find a STRUCTURALLY CORRECT and CAUSALLY EXECUTABLE SL definition that:

- matches the actual Ekalayava price-action concept
- can be implemented live on completed 5-minute candles
- does not use future information
- is reasonably robust across the 9 months
- avoids unnecessary stop-outs
- remains understandable and auditable

---------------------------------------------------
5B — EKALAYAVA STOP BUFFER
---------------------------------------------------

After identifying the structural anchor, investigate the required protective buffer.

Do NOT arbitrarily choose a buffer.

Study the data.

Where appropriate compare a small set of sensible buffers around the structural low.

For example, only if supported by the data:

- exact structural low
- small fixed-point buffer
- volatility/structure-relative buffer

Do NOT over-optimize dozens of values.

The goal is robustness, not curve fitting.

If the data does NOT justify a precise numerical buffer:

say so explicitly.

In that case, define the canonical SL anchor clearly and leave the buffer as a controlled implementation parameter rather than pretending the research proved an exact number.

---------------------------------------------------
5C — EKALAYAVA TARGET RESEARCH
---------------------------------------------------

Study the Ekalayava target behavior over the full usable Jan-Sep dataset.

The natural target concept is the Opening High.

Measure:

- number of Ekalayava entries
- number reaching Opening High
- percentage reaching Opening High
- MFE
- MAE
- distance from entry to Opening High
- time to Opening High
- time buckets:
  0-5m
  5-10m
  10-15m
  15-30m
  30-60m
  60-90m
  >90m

Also study:

- CE vs PE
- ITM2 vs ITM3
- 09:15-09:59
- 10:00-10:59
- later entries if any
- monthly distribution

IMPORTANT:

Do NOT call "touched Opening High" a win unless a valid SL/target lifecycle has been simulated.

Clearly distinguish:

TARGET TOUCH / TARGET REACH
from
RESOLVED WIN.

---------------------------------------------------
5D — FULL EKALAYAVA EXIT SIMULATION
---------------------------------------------------

Once the most defensible structural SL definition has been identified, perform a bounded retrospective simulation.

For each valid Ekalayava entry:

ENTRY:
    causal swing-high breakout entry

TARGET:
    Opening High

SL:
    recommended causal structural low
    + only the evidence-supported protective buffer

Resolution:

- TARGET if target is reached first
- SL if stop is reached first
- AMBIGUOUS if both are touched within the same 5-minute candle and ordering cannot be known
- OPEN/UNRESOLVED if the available session/data ends before resolution

Do NOT invent intrabar ordering.

Use OHLC limitations correctly.

Report:

- total entries
- resolved
- target
- SL
- ambiguous
- unresolved
- target rate among resolved
- average winner
- average loser
- expectancy in premium points if meaningful
- median winner
- median loser
- max consecutive losses
- drawdown
- MFE
- MAE
- holding time
- target timing
- stop timing

Also show the distribution monthly.

Do NOT call premium points "rupee P&L" unless position size and actual execution costs are explicitly modeled.

===================================================
SECTION 6 — EKALAYAVA ROBUSTNESS / OVERFITTING CHECK
===================================================

Do NOT optimize Ekalayava to one month.

Use chronological analysis.

Prefer:

Jan-Mar
Apr-Jun
Jul-Sep

and monthly breakdowns.

Look for:

- whether the structural SL behavior persists
- whether target behavior persists
- whether one month dominates the apparent performance
- whether the recommended SL works across different market regimes
- whether results collapse when one strong month is removed

If sample sizes are small, explicitly state that.

Do NOT manufacture confidence.

===================================================
SECTION 7 — FINAL STRATEGY COMPARISON
===================================================

Create a final comparison between:

L2L
vs
Ekalayava

Include:

- setups
- resolved trades
- target rate
- SL rate
- unresolved
- average winner
- average loser
- expectancy if valid
- max consecutive losses
- drawdown
- median holding time
- target timing
- stop timing
- CE/PE behavior
- ITM2/ITM3 behavior
- monthly stability
- data coverage

Clearly distinguish:

OBSERVATIONAL METRICS
from
FULLY RESOLVED TRADE METRICS.

Do not claim profitability from incomplete/unresolved Ekalayava data.

===================================================
SECTION 8 — LIVE PAPER OBSERVER READINESS
===================================================

After research, inspect the current live/read-only observer code end-to-end.

We want to be READY FOR LIVE PAPER TRADING.

The observer must implement:

1. Market session detection
2. 09:15 opening 5-minute candle
3. NIFTY opening high/low
4. Daily expiry determination
5. Exact option selection
6. CE/PE
7. ITM2/ITM3
8. Exact Groww symbol
9. 5-minute candle retrieval
10. Completed-candle enforcement
11. Canonical L2L engine
12. Canonical Ekalayava engine
13. Paper trade engine
14. Paper SL/target evaluation
15. Trade journal
16. Duplicate-signal prevention
17. Restart/recovery
18. API reconnect handling
19. Missing candle handling
20. Market-hours handling
21. Logging
22. Kill switch
23. No real-order path

CRITICAL:

The live engine MUST NOT evaluate an unfinished 5-minute candle as if it were completed.

===================================================
SECTION 9 — L2L LIVE LOGIC
===================================================

Ensure L2L live logic is STATEFUL.

Correct state sequence:

OPENING CANDLE
    ↓
RED CANDLE BREAKS BELOW OPENING LOW
    ↓
WAIT
    ↓
FIRST SUBSEQUENT GREEN 5M CANDLE
    ↓
ENTRY AT COMPLETED CANDLE CLOSE
    ↓
PAPER SL / TARGET

Do NOT use the incorrect shortcut:

    current candle low < opening low
    AND current candle is green

That is NOT sufficient.

Prevent duplicate entries.

One setup should generate at most one L2L entry.

===================================================
SECTION 10 — EKALAYAVA LIVE LOGIC
===================================================

Implement the finalized Ekalayava research result causally.

Required conceptual sequence:

OPENING HIGH/LOW
    ↓
PREMIUM BREAKS BELOW OPENING LOW
    ↓
REVERSAL / BASE
    ↓
CAUSAL PRICE-ACTION STRUCTURE
    ↓
SWING HIGH
    ↓
SWING-HIGH BREAKOUT
    ↓
ENTRY BEFORE OPENING HIGH
    ↓
PAPER STRUCTURAL SL
    +
PAPER TARGET = OPENING HIGH

No future candles may be used to decide:

- swing high
- structural low
- entry
- SL

If the research concludes that a particular structural definition is safest, implement exactly that definition and document it.

===================================================
SECTION 11 — PAPER JOURNAL
===================================================

Ensure every paper trade records at minimum:

- date
- timestamp
- strategy
- CE/PE
- ITM rank
- expiry
- strike
- exact option symbol
- NIFTY price
- option entry price
- Opening High
- Opening Low
- entry candle timestamp
- SL
- target
- exit timestamp
- exit price
- exit reason
- holding time
- MFE
- MAE
- data-quality flag
- model/strategy version

For Ekalayava also record:

- structural SL anchor
- structural low price
- buffer
- swing-high level
- breakout candle

===================================================
SECTION 12 — DATA GAP HANDLING
===================================================

This is a HARD requirement.

If one option contract/day is missing:

SKIP IT.

If one contract/day has insufficient data:

SKIP IT.

Continue processing all other available days.

Do not repeatedly retry.

Do not block finalization.

Do not fabricate data.

At the end report:

    usable sessions
    skipped sessions
    missing-data sessions

but KEEP THE RESEARCH MOVING.

===================================================
SECTION 13 — TESTING
===================================================

Run the complete existing test suite.

Add/update tests for:

- L2L first-green sequence
- completed 5m candle requirement
- no lookahead
- duplicate protection
- L2L SL
- L2L target
- Ekalayava swing breakout
- Ekalayava structural SL
- Ekalayava target
- ambiguous same-candle outcome
- missing-data skip behavior
- restart/recovery
- paper-only safety
- exact contract selection
- ITM2/ITM3 selection
- expiry selection

All tests must pass.

===================================================
SECTION 14 — RESEARCH STATE
===================================================

Update:

RESEARCH_STATE.md

with the FINAL numerical findings.

It must clearly contain:

L2L:
- final sample
- target/SL statistics
- target timing
- important edge cases
- final interpretation

EKALAYAVA:
- final sample
- target-touch statistics
- resolved target/SL statistics if simulated
- recommended structural SL definition
- recommended buffer if supported
- target behavior
- holding-time behavior
- MFE/MAE
- robustness
- limitations

DATA:
- usable coverage
- skipped coverage
- concise missing-data summary

READINESS:
- paper-trading status
- known limitations
- safety status

Do not leave important numerical results only inside an ignored terminal output.

===================================================
SECTION 15 — REPORTS THAT MUST BE SAVED
===================================================

This is mandatory.

Create/update and COMMIT all relevant reports.

At minimum:

reports/L2L_FINAL_VALIDATION.md

reports/L2L_FINAL_VALIDATION.json

reports/EKALAYAVA_FINAL_RESEARCH.md

reports/EKALAYAVA_FINAL_RESEARCH.json

reports/STRATEGY_FINAL_COMPARISON.md

reports/PAPER_TRADING_READINESS.md

If existing report naming conventions differ, preserve the repository convention, but make sure BOTH L2L AND EKALAYAVA reports are clearly present.

DO NOT finish with only the L2L report.

The final GitHub repository must visibly contain the Ekalayava research report.

===================================================
SECTION 16 — GIT REQUIREMENTS
===================================================

Before committing:

1. Check git status.
2. Check changed files.
3. Confirm no secrets are staged.
4. Confirm:
      .env
      secrets.txt
      API keys
      API secrets
   are ignored.
5. Run tests.
6. Verify reports exist.
7. Verify RESEARCH_STATE.md is updated.
8. Verify paper-only safety remains enabled.

Then:

git add appropriate files
git commit with a clear finalization message
git push origin main

DO NOT merely tell me that changes are ready.

Actually push the legitimate completed work to:

    origin/main

After pushing, verify:

    git status
    git log -1
    remote branch/state

===================================================
SECTION 17 — DO NOT WASTE COMPUTE
===================================================

You already have substantial historical research.

DO NOT:

- rerun unchanged L2L target-timing research
- redownload the entire dataset
- repeatedly chase missing days
- optimize hundreds of SL values
- brute-force indicators
- create random strategy variations
- change the canonical entry rules
- use an LLM for every candle
- build real order execution
- wait indefinitely for incomplete data

Spend compute ONLY where it materially advances finalization:

1. Ekalayava structural SL research
2. Ekalayava target/SL retrospective simulation
3. L2L final validation/edge-case cleanup
4. live paper observer correctness
5. tests
6. documentation/reports
7. git commit/push

===================================================
SECTION 18 — FINAL DECISION STANDARD
===================================================

At the end, classify each strategy:

L2L:
    READY FOR LIVE PAPER OBSERVATION
or
    NOT READY — list exact blocker(s)

Ekalayava:
    READY FOR LIVE PAPER OBSERVATION
or
    READY FOR OBSERVATION ONLY
or
    NOT READY — list exact blocker(s)

Do NOT use "live trading ready" to mean real-money execution.

We want:

    LIVE MARKET DATA
    +
    PAPER SIGNALS
    +
    PAPER SL/TARGET
    +
    JOURNAL
    +
    ZERO REAL ORDERS

===================================================
SECTION 19 — FINAL OUTPUT TO ME
===================================================

When completely finished, give me a concise final report containing:

1. What was completed
2. L2L final results
3. Ekalayava final results
4. EXACT recommended Ekalayava SL logic
5. EXACT Ekalayava target logic
6. Ekalayava target rate
7. Ekalayava SL rate
8. Ekalayava average winner/loser if valid
9. Ekalayava holding-time/target-time findings
10. L2L target timing conclusion
11. Whether 90-minute observation/holding is justified
12. Paper-trading readiness for each strategy
13. Tests passed
14. Reports created
15. Git commit hash
16. Confirmation that changes were pushed to origin/main

MOST IMPORTANT:

DO NOT STOP AFTER L2L.

DO NOT FINISH UNTIL THE EKALAYAVA RESEARCH HAS ALSO BEEN COMPLETED OR A CLEAR TECHNICAL BLOCKER IS IDENTIFIED.

DO NOT HIDE Ekalayava results in terminal output.

SAVE THEM TO REPORT FILES.

PUSH BOTH STRATEGY REPORTS TO GITHUB MAIN.

Use the existing data intelligently.
Skip unavailable days.
Move forward.
Finish the system.
===================================================
