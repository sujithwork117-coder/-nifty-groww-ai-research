# NIFTY Groww AI Research — Master Execution Plan

## PROJECT PURPOSE

Build a NIFTY-only research, learning, backtesting and paper-trading system using Groww API.

The system must support:

1. Historical market-data collection
2. NIFTY 5-minute analysis
3. NIFTY ITM option analysis
4. Level-to-Level strategy
5. Ekalayava / God-Level strategy
6. Historical backtesting
7. Paper-trade simulation
8. Statistical learning from historical outcomes
9. Chart generation
10. Setup-quality filtering
11. Performance reports
12. Future read-only live monitoring

## ABSOLUTE SAFETY RULES

These rules apply to EVERY step.

- REAL ORDER EXECUTION IS DISABLED.
- EXECUTION_ALLOWED must remain false.
- PAPER_ONLY must remain true.
- KILL_SWITCH must remain available.
- Do NOT implement place_order().
- Do NOT implement modify_order().
- Do NOT implement cancel_order().
- Do NOT send any real trading order.
- Do NOT create an execution pathway.
- Do NOT bypass the safety layer.
- Do NOT weaken or remove safety checks.
- Never print API keys.
- Never print API secrets.
- Never print access tokens.
- Never print TOTP secrets.
- Never commit credentials to Git.
- Never put credentials directly into Python source files.
- Credentials must remain in secure environment variables/secrets.

## STRATEGY RULE

Do not change the original strategy definitions unless explicitly instructed.

==================================================
CURRENT STATUS
==================================================

Completed:

- Project created
- Groww project structure created
- Sample data pipeline created
- Opening-level bug fixed
- pytest configuration fixed
- pytest passing
- Groww authentication configured
- Groww authentication successfully tested
- Execution remains disabled

Current next step:

15B

==================================================
STEP 15B — READ-ONLY GROWW API VERIFICATION
==================================================

OBJECTIVE

Verify that the authenticated Groww client can successfully communicate
with Groww using a READ-ONLY API call.

TASKS

1. Initialize the existing Groww API client.
2. Use the existing secure authentication mechanism.
3. Call the read-only user profile endpoint.
4. Do not expose credentials.
5. Do not call any order API.
6. Confirm:
   - Groww authentication = SUCCESS
   - Read-only API = SUCCESS
   - Order execution = DISABLED
7. Confirm:
   EXECUTION_ALLOWED=false
   PAPER_ONLY=true
8. Run:

   pytest -q

9. Do not modify strategy logic.

SUCCESS CRITERIA

- get_user_profile() succeeds.
- No credentials are printed.
- No order API is called.
- pytest passes.

COMMIT

"Verify Groww read-only API connection"

==================================================
STEP 15C — GROWW HISTORICAL NIFTY DATA
==================================================

OBJECTIVE

Connect the research engine to Groww historical candle data.

TASKS

1. Implement/read the existing historical-data module.
2. Retrieve NIFTY historical candles through Groww.
3. Use 5-minute candles.
4. Convert timestamps safely to Asia/Kolkata.
5. Preserve:
   - timestamp
   - open
   - high
   - low
   - close
   - volume
   - OI where available
6. Do not download option data yet.
7. Save downloaded data locally under:

   data/raw/

8. Avoid duplicate candles.
9. Sort chronologically.
10. Validate:
    - no invalid timestamps
    - OHLC values are valid
    - timestamp ordering is correct
11. Respect Groww historical API request limits.
12. Use chunking/retry logic already present in the project.
13. Do not modify strategy definitions.
14. Do not implement order execution.
15. Run:

    pytest -q

SUCCESS CRITERIA

A real Groww NIFTY 5-minute historical dataset is saved locally
and passes validation.

COMMIT

"Add Groww NIFTY historical data pipeline"

==================================================
STEP 15D — GROWW OPTION CONTRACT DISCOVERY
==================================================

OBJECTIVE

Discover the NIFTY option contracts required by the strategies.

REQUIRED OPTIONS

Underlying:

NIFTY

Option types:

CE
PE

Allowed moneyness:

2nd ITM
3rd ITM

Do NOT use:

- OTM
- 4th ITM
- 5th ITM
- deeper ITM

TASKS

1. Retrieve available NIFTY expiries.
2. Retrieve available NIFTY option contracts.
3. Identify strike prices.
4. For CE:
   ITM strikes are below the NIFTY underlying price.

5. For PE:
   ITM strikes are above the NIFTY underlying price.

6. Rank ITM contracts.
7. Keep only:
   - 2nd ITM
   - 3rd ITM

8. Store contract metadata:

   symbol
   expiry
   strike
   option_type
   ITM_rank

9. Validate that no OTM contracts are selected.
10. Validate that no deeper-than-3rd-ITM contracts are selected.
11. Run pytest.
12. No execution APIs.

SUCCESS CRITERIA

The system can correctly identify the required NIFTY
2nd-ITM and 3rd-ITM CE/PE contracts.

COMMIT

"Add NIFTY ITM option contract selection"

==================================================
STEP 15E — OPTION HISTORICAL DATA
==================================================

OBJECTIVE

Download historical 5-minute candles for the required NIFTY
ITM option contracts.

TASKS

1. Use contracts discovered in Step 15D.
2. Retrieve historical candles from Groww.
3. Use 5-minute interval.
4. Store each contract's data.
5. Preserve:
   timestamp
   open
   high
   low
   close
   volume
   OI where available

6. Normalize timestamps to Asia/Kolkata.
7. Sort chronologically.
8. Remove duplicates.
9. Validate OHLC.
10. Record:
    underlying
    expiry
    strike
    option_type
    ITM_rank

11. Do not mix different contracts without identifying them.
12. Do not introduce look-ahead bias.
13. Do not implement execution.
14. Run pytest.

SUCCESS CRITERIA

Historical option datasets are available for the required
NIFTY ITM contracts.

COMMIT

"Add historical NIFTY option data pipeline"

==================================================
STEP 15F — DATA QUALITY AND ALIGNMENT
==================================================

OBJECTIVE

Create a reliable dataset for strategy research.

TASKS

1. Align NIFTY underlying and option candles by timestamp.
2. Handle missing candles explicitly.
3. Detect duplicate candles.
4. Detect impossible OHLC relationships.
5. Detect gaps.
6. Identify trading dates.
7. Ensure timestamps are timezone-aware.
8. Prevent future candles from leaking into earlier decisions.
9. Ensure strategy decisions only use information available
   at that candle's timestamp.
10. Generate a data-quality report.

REPORT MUST INCLUDE

- total candles
- trading dates
- missing intervals
- duplicate count
- invalid OHLC count
- contract count
- date range

SUCCESS CRITERIA

The dataset is suitable for chronological backtesting.

COMMIT

"Add historical data validation and alignment"

==================================================
STEP 15G — LEVEL-TO-LEVEL BACKTEST
==================================================

OBJECTIVE

Backtest the exact Level-to-Level strategy.

STRATEGY DEFINITION

Underlying:

NIFTY only

Option:

ITM only

Allowed:

2nd ITM
3rd ITM

Interval:

5-minute

PRIMARY TIME:

09:15–11:00

HIGH ALERT PERIOD:

09:15–10:00

OPENING LEVEL

Use the opening 5-minute candle.

Opening levels:

opening_high
opening_low

ENTRY SEQUENCE

1. Opening 5-minute candle establishes levels.
2. Option premium moves below opening_low.
3. Wait.
4. A COMPLETED green 5-minute candle appears.
5. Entry is triggered.
6. Paper entry price = close of the completed green candle.

STOP LOSS

SL = opening_low - configured SL points.

Default:

4 points

The configuration must allow:

3 points
4 points

TARGET

Target = opening_high.

IMPORTANT

Do not add:
- RSI
- MACD
- VWAP
- Supertrend
- EMA filters
- volume filters
- arbitrary AI filters

unless explicitly requested later.

The deterministic strategy must remain intact.

BACKTEST OUTPUT

For every setup:

- date
- timestamp
- option symbol
- expiry
- strike
- option type
- ITM rank
- entry price
- opening high
- opening low
- stop loss
- target
- exit timestamp
- exit price
- outcome
- points gained/lost
- time to target/SL
- entry hour
- entry minute
- before_10 flag

If both SL and target are touched within the same
5-minute candle and intrabar order cannot be determined:

mark:

AMBIGUOUS_SL_FIRST

Do not assume target was reached first.

SUCCESS CRITERIA

The backtester produces deterministic Level-to-Level
historical results without look-ahead bias.

COMMIT

"Add Level-to-Level historical backtest"

==================================================
STEP 15H — EKALAYAVA BACKTEST
==================================================

OBJECTIVE

Backtest the Ekalayava / God-Level strategy.

STRATEGY DEFINITION

Underlying:

NIFTY only

Option:

ITM only

Allowed:

2nd ITM
3rd ITM

Interval:

5-minute

OPENING LEVELS

Use opening 5-minute:

opening_high
opening_low

SEQUENCE

1. Premium comes down toward/lower area.
2. Reversal develops.
3. A swing high can form later.
4. Premium breaks the relevant swing high.
5. A COMPLETED 5-minute candle closes above opening_high.
6. Price action is evaluated as supporting context.

IMPORTANT

A textbook candle pattern is NOT mandatory.

The system must not invent a target because no target
was specified in the original strategy.

For the initial research version, record:

- setup occurrence
- entry timestamp
- entry price
- option contract
- opening high
- opening low
- swing high
- breakout timestamp
- confirmation timestamp
- subsequent MFE
- subsequent MAE

Do not invent exit rules.

SUCCESS CRITERIA

The system identifies Ekalayava setups without
adding conditions that were not specified.

COMMIT

"Add Ekalayava historical setup analysis"

==================================================
STEP 15I — HISTORICAL LEARNING ENGINE
==================================================

OBJECTIVE

Allow the system to learn from historical setups.

IMPORTANT

"Learning" means statistical learning from historical data.

It does NOT mean memorizing charts.

TASKS

For every historical setup calculate:

- MFE
- MAE
- entry time
- entry hour
- entry minute
- before 10 AM
- after 10 AM
- weekday
- option type
- ITM rank
- volatility context
- premium movement
- candle structure
- rejection characteristics
- breakout characteristics
- time to target where applicable
- false breakout indicators
- outcome

SPLIT

Use chronological split.

Example:

70% earliest data = training

30% latest data = validation

Never randomly shuffle time-series data for the
main validation experiment.

LEARNING MODEL

A baseline model may be used to estimate setup quality.

The model must NOT directly execute trades.

The deterministic risk engine remains authoritative.

The model may classify:

- stronger historical setup
- weaker historical setup
- ambiguous setup

Do not claim the model is profitable simply because
training accuracy is high.

SUCCESS CRITERIA

Out-of-sample validation results are produced.

COMMIT

"Add chronological historical learning engine"

==================================================
STEP 15J — SETUP QUALITY ANALYSIS
==================================================

OBJECTIVE

Determine which historical conditions were associated
with different outcomes.

ANALYZE

1. Before 10 AM vs after 10 AM
2. CE vs PE
3. 2nd ITM vs 3rd ITM
4. Entry time
5. Day of week
6. Volatility
7. Premium distance from opening level
8. Reversal size
9. Swing-high characteristics
10. Candle structure
11. Rejection characteristics
12. False breakouts
13. Time to target
14. MAE
15. MFE

Do not produce a single "best strategy" score.

Produce factual statistics and distributions.

SUCCESS CRITERIA

The report clearly shows which conditions had
different historical outcomes without overclaiming.

COMMIT

"Add setup quality analysis"

==================================================
STEP 15K — CHART GENERATION
==================================================

OBJECTIVE

Generate visual charts for historical setups.

FOR EACH SELECTED SETUP SHOW

- NIFTY price
- option premium
- opening high
- opening low
- entry
- SL where applicable
- target where applicable
- swing high
- breakout
- exit
- relevant candles

Use 5-minute candles.

Charts should be saved under:

data/reports/charts/

Create charts for:

- Level-to-Level examples
- successful setups
- failed setups
- ambiguous setups
- Ekalayava setups
- false breakouts

Do not modify strategy logic.

SUCCESS CRITERIA

Charts can visually explain why each setup was
classified the way it was.

COMMIT

"Add historical setup chart generation"

==================================================
STEP 15L — PAPER TRADING ENGINE
==================================================

OBJECTIVE

Run the strategies as hypothetical trades.

NO REAL ORDERS.

For each paper trade record:

- signal
- entry
- stop
- target
- exit
- P&L
- duration
- reason for exit
- strategy
- contract
- ITM rank

The paper engine must enforce:

EXECUTION_ALLOWED=false

PAPER_ONLY=true

If either condition is violated, stop immediately.

SUCCESS CRITERIA

Paper trades are generated and journaled without
sending any Groww order.

COMMIT

"Add paper trading engine"

==================================================
STEP 15M — PAPER JOURNAL AND REPORTING
==================================================

OBJECTIVE

Create a complete research report.

REPORT SHOULD INCLUDE

1. Total setups
2. Valid setups
3. Skipped setups
4. Ambiguous setups
5. Target hits
6. SL hits
7. Average points
8. Median points
9. Maximum favorable excursion
10. Maximum adverse excursion
11. Average holding time
12. Entry-time distribution
13. Before/after 10 AM comparison
14. CE/PE breakdown
15. 2nd/3rd ITM breakdown
16. Strategy breakdown
17. False breakout count
18. Data quality statistics

Do not fabricate missing statistics.

SUCCESS CRITERIA

A reproducible report is generated from the historical
and paper-trading datasets.

COMMIT

"Add research reporting"

==================================================
STEP 15N — READ-ONLY LIVE MARKET MONITOR
==================================================

OBJECTIVE

Monitor live NIFTY and option prices without trading.

TASKS

1. Connect to Groww live market data.
2. Monitor required instruments.
3. Build completed 5-minute candles.
4. Calculate strategy conditions.
5. Generate paper-only signals.
6. Write signals to the journal.

MUST NOT

- place orders
- modify orders
- cancel orders
- submit orders
- request order execution

Every signal must clearly state:

EXECUTION = DISABLED

SUCCESS CRITERIA

The system can observe the market and generate
paper signals without trading.

COMMIT

"Add read-only live paper monitor"

==================================================
STEP 15O — LIVE PAPER SIGNAL VALIDATION
==================================================

OBJECTIVE

Compare live paper signals with subsequent market
movement.

For every live signal record:

- signal timestamp
- contract
- entry
- opening levels
- SL
- target where applicable
- subsequent price
- hypothetical result
- MFE
- MAE

Do not execute any order.

SUCCESS CRITERIA

Live signals can be evaluated after the fact.

COMMIT

"Add live paper signal evaluation"

==================================================
STEP 15P — ANTI-OVERFITTING VALIDATION
==================================================

OBJECTIVE

Ensure the learning system does not simply overfit
historical data.

TASKS

1. Chronological train/validation split.
2. No future information in features.
3. No future candles used to generate earlier signals.
4. Test multiple historical periods.
5. Compare training vs validation performance.
6. Track setup counts.
7. Flag insufficient sample sizes.
8. Avoid excessive parameter optimization.
9. Do not tune repeatedly against the validation period.

REPORT:

- training statistics
- validation statistics
- sample size
- feature set
- model version
- date range

SUCCESS CRITERIA

The system explicitly reports potential
overfitting rather than hiding it.

COMMIT

"Add anti-overfitting validation"

==================================================
STEP 15Q — FINAL SAFETY AUDIT
==================================================

OBJECTIVE

Perform a complete execution-safety audit.

SEARCH THE ENTIRE REPOSITORY FOR:

place_order
modify_order
cancel_order
EXECUTION_ALLOWED
PAPER_ONLY

Confirm:

EXECUTION_ALLOWED=false

PAPER_ONLY=true

Confirm there is no reachable execution path.

Check:

- no credentials committed
- no credentials printed
- no hard-coded secrets
- no accidental order calls
- no execution bypass
- kill switch works
- tests pass

Run:

pytest -q

SUCCESS CRITERIA

All tests pass and execution remains disabled.

COMMIT

"Complete paper-only safety audit"

==================================================
STEP 15R — FINAL RESEARCH RUN
==================================================

OBJECTIVE

Run the complete research pipeline on the selected
historical period.

PIPELINE

1. Load historical NIFTY data.
2. Load historical option data.
3. Validate data.
4. Identify contracts.
5. Run Level-to-Level.
6. Run Ekalayava.
7. Generate setup statistics.
8. Run learning analysis.
9. Generate charts.
10. Generate paper journal.
11. Generate final research report.
12. Run safety tests.

NO LIVE ORDERS.

NO REAL EXECUTION.

SUCCESS CRITERIA

A complete reproducible research package is produced.

Expected outputs:

data/reports/
data/reports/charts/
data/processed/
logs/

COMMIT

"Complete NIFTY research pipeline"

==================================================
FINAL PROJECT STATE
==================================================

The project should eventually support:

HISTORICAL DATA
      |
      v
DATA VALIDATION
      |
      v
CONTRACT SELECTION
      |
      v
FEATURE ENGINEERING
      |
      +----------------------+
      |                      |
      v                      v
LEVEL-TO-LEVEL          EKALAYAVA
      |                      |
      +----------+-----------+
                 |
                 v
          PAPER BACKTEST
                 |
                 v
          HISTORICAL LEARNING
                 |
                 v
          SETUP QUALITY
                 |
                 v
              CHARTS
                 |
                 v
          RESEARCH REPORT
                 |
                 v
       READ-ONLY LIVE MONITOR
                 |
                 v
          PAPER SIGNALS ONLY

REAL ORDER EXECUTION:

                DISABLED
                    |
                    v
             EXECUTION_ALLOWED
                  FALSE
                    |
                    v
                PAPER_ONLY
                   TRUE

==================================================
COPILOT EXECUTION RULE
==================================================

When asked to execute a step:

1. Read this entire file.
2. Execute ONLY the requested step.
3. Do not jump to future steps.
4. Do not change strategy definitions.
5. Do not implement order execution.
6. Preserve all safety locks.
7. Run relevant tests.
8. Report:
   - files changed
   - what was implemented
   - tests executed
   - test results
   - data generated
   - any issues
9. Wait for explicit instruction before moving
   to the next step.