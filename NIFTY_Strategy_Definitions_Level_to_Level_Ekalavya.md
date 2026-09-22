# NIFTY Trading Research — Complete Strategy Definitions
## Level-to-Level + Ekalavya
### Source of truth for Copilot implementation, backtesting and paper research

**Purpose:** This document is the canonical strategy-definition document for the current NIFTY options research project.

**Critical rule:** Copilot must read this document before changing, rerunning, or interpreting either strategy. Do not infer missing rules from generic trading knowledge. Do not silently change the strategy definitions.

**Execution mode:** Research / historical backtest / paper only.  
**Live order execution:** DISABLED.  
**Do not implement, call, or test order-placement APIs.**

---

# 1. Common Rules

## 1.1 Underlying
- Project scope: **NIFTY only**.
- Do not use BANKNIFTY or SENSEX for the actual NIFTY backtest.
- The attached class examples may contain other indices, but those are visual references for the price-action concept only.

## 1.2 Option selection
- Trade/research only NIFTY options.
- Only **ITM options**.
- Only the **2nd ITM and 3rd ITM** contracts are eligible.
- Do not use OTM contracts.
- Do not use 4th ITM or deeper contracts.
- Evaluate both:
  - CE
  - PE
- The system must not silently exclude one option type.

## 1.3 Timeframe
- Primary timeframe: **5-minute candles**.
- All candle-based decisions must use completed 5-minute candles.
- No look-ahead:
  - A candle's close/open/high/low can only be used after that candle is completed.
  - Do not use future candles to identify a setup, swing, entry, target or stop.

## 1.4 Timezone
- All strategy times are **Asia/Kolkata (IST)**.
- Normalize timestamps before calculating:
  - trading date
  - opening candle
  - entry time
  - hour
  - before/after 10:00 AM
  - holding time

## 1.5 Opening candle
For each trading date, identify the first 5-minute market candle used by the strategy.

The opening candle provides:
- Opening High
- Opening Low

For this project, the opening levels are the levels used in both strategies.

Do not redefine the opening levels using a later candle.

## 1.6 Historical option data
- Option candles must be aligned to the underlying trading date/time correctly.
- Preserve the actual option premium OHLC.
- Do not substitute NIFTY underlying OHLC for option premium OHLC when evaluating an option strategy.
- If required option data is missing, mark the setup/data as unavailable rather than fabricating a signal.

## 1.7 Multiple contracts
The system may evaluate eligible 2nd/3rd ITM CE/PE contracts, but it must avoid accidental duplicate counting of the same underlying event.

Every setup should record at minimum:
- date
- option symbol/contract
- CE/PE
- ITM rank
- entry timestamp
- entry premium
- opening high
- opening low
- target
- SL, if defined
- exit timestamp
- exit premium
- outcome
- MFE
- MAE
- reason for entry/exit

## 1.8 Research safety
- No live order placement.
- No order modification.
- No cancellation.
- No execution API calls.
- `EXECUTION_ALLOWED=false`
- `PAPER_ONLY=true`

---

# 2. STRATEGY 1 — LEVEL-TO-LEVEL

## 2.1 Core concept

Level-to-Level is an opening-range level strategy.

The opening 5-minute candle establishes:
- Opening High = upper level / target
- Opening Low = lower level / setup level

The setup occurs when option premium breaks below the Opening Low with a red candle.

**The FIRST subsequent GREEN 5-minute candle is the entry.**

There is no requirement for another confirmation indicator.

---

## 2.2 Exact sequence

### Step 1 — Opening range
Identify the first 5-minute candle of the trading day.

Store:
- `opening_high`
- `opening_low`

### Step 2 — Red breakdown below Opening Low
After the opening candle, wait for a **red 5-minute candle** whose low goes below the Opening Low.

For a standard candle:
- Red = `close < open`
- Breakdown = candle trades below `opening_low`

The setup is now activated.

### Step 3 — First green candle
After the red breakdown candle, watch subsequent completed 5-minute candles.

**The first GREEN candle that appears after the red breakdown is the entry trigger.**

Green:
- `close > open`

There is NO requirement for:
- a second green candle
- an EMA
- RSI
- MACD
- volume confirmation
- swing-high confirmation
- another indicator
- a close above Opening Low
- a breakout of another resistance level

### Step 4 — Entry
Enter/paper-enter immediately based on the first completed green candle after the red breakdown.

For backtesting without intrabar look-ahead:
- entry price = close of that completed green candle.

Do not use the candle's future movement after its close to decide whether the entry should have happened.

### Step 5 — Stop-loss
The intended Level-to-Level stop is approximately **3–4 points below the Opening Low**.

Project configuration may use:
- default: **4 points below Opening Low**
- configurable range: 3–4 points

Formula:
`SL = opening_low - configured_sl_points`

Do not replace this with an unrelated indicator or swing stop.

### Step 6 — Target
**Target = Opening High.**

Formula:
`target = opening_high`

### Step 7 — Exit
After entry:
- If target is reached, record TARGET.
- If SL is reached, record SL.
- If both are touched inside the same 5-minute candle and the actual intrabar order cannot be known from OHLC data, record the event as **AMBIGUOUS** rather than pretending to know which was hit first.

The existing research convention is conservative for this case.

---

## 2.3 Level-to-Level timing

The strategy is primarily intended for the morning.

Current project configuration:
- Strategy observation/entry window: approximately **09:15–11:00 IST**
- Particular attention is paid to the period before **10:00 IST**.

Do not expand the entry window without explicit instruction.

---

## 2.4 Level-to-Level decision tree

```text
Opening 5m candle
        |
        +--> Opening High = TARGET
        |
        +--> Opening Low
                |
                v
      Red 5m candle trades below
      Opening Low?
                |
          NO ---+--- wait
                |
               YES
                |
                v
      Setup activated
                |
                v
   Next completed 5m candles
                |
       Is candle GREEN?
          /          \
        NO            YES
        |              |
      WAIT           ENTRY
                       |
                       +--> SL = Opening Low - 3/4
                       |
                       +--> TARGET = Opening High
```

---

## 2.5 Level-to-Level exclusions

Do NOT add:
- EMA conditions
- RSI
- MACD
- VWAP
- volume filters
- option Greeks filters
- volatility filters
- textbook candlestick patterns
- swing-high requirements
- second-candle confirmation
- arbitrary premium targets
- arbitrary fixed-profit filters

The strategy should remain faithful to the defined sequence.

---

# 3. STRATEGY 2 — EKALAVYA

## 3.1 Core concept

Ekalavya is a **reversal + swing-breakout continuation setup**.

The attached Harish sir examples show a common visual structure:

1. Opening High and Opening Low are established.
2. Option premium moves below the Opening Low.
3. A low/reversal develops.
4. Premium begins recovering.
5. A swing high forms during the recovery.
6. Premium breaks the relevant swing high.
7. Entry occurs on that swing-high breakout.
8. The **Opening High is the target**.

The examples show that the trade can continue through the Opening High after entry.

---

## 3.2 Exact sequence

### Step 1 — Opening range
Identify:
- `opening_high`
- `opening_low`

from the first 5-minute candle.

### Step 2 — Premium moves below Opening Low
The eligible option premium must move below the Opening Low.

This is the initial weakness / setup-development phase.

Do not enter merely because the premium crosses below Opening Low.

### Step 3 — Reversal
After moving below Opening Low, the premium must show a reversal/recovery.

The examples demonstrate:
- a low/exhaustion area
- followed by upward recovery
- followed by developing higher structure

The system must not use future candles to declare a reversal.

### Step 4 — Swing high develops
During the recovery, identify a meaningful local/swing high.

This swing high acts as the breakout reference.

The exact swing-detection parameters must be explicit and causal:
- only candles available up to that point may be used;
- no future candle may be used to retroactively identify an entry.

If the existing implementation uses a fixed swing window, report the exact rule before changing it.

### Step 5 — Swing-high breakout
The premium breaks the identified swing high.

This is the Ekalavya entry trigger.

**IMPORTANT:**
Do NOT require the premium to already close above the Opening High for entry.

The Opening High is the TARGET, so requiring entry above it would invalidate the target relationship.

### Step 6 — Entry
For a conservative 5-minute backtest:
- enter/paper-enter when the completed 5-minute candle confirms the swing-high breakout according to the chosen causal breakout rule.

The exact implementation must be reported before changing it if it is not already defined.

Do not fabricate an intrabar entry price.

### Step 7 — Target
**Target = day Opening High.**

Formula:
`target = opening_high`

This target is the upper opening-range level shown in the class examples.

### Step 8 — Stop-loss
**The attached examples do not provide enough explicit information to establish a precise numeric Ekalavya SL rule.**

Therefore:
- DO NOT invent a fixed ₹/point SL.
- DO NOT automatically use Opening Low as the SL.
- DO NOT automatically use the reversal low as the SL.
- DO NOT automatically use a swing low as the SL.

First audit the existing implementation and report its current Ekalavya SL logic.

If a precise SL rule is subsequently supplied, add it as an explicit versioned rule.

Until then, Ekalavya SL must be marked **UNDEFINED / REQUIRES RULE**, rather than silently fabricated.

---

# 4. Ekalavya decision tree

```text
Opening 5m candle
        |
        +--> Opening High = TARGET
        |
        +--> Opening Low
                |
                v
       Premium moves BELOW
       Opening Low
                |
                v
          LOW / REVERSAL
                |
                v
       Recovery develops
                |
                v
       SWING HIGH FORMS
                |
                v
      Premium BREAKS that
          SWING HIGH
                |
                v
             ENTRY
                |
                +--> TARGET = Opening High
                |
                +--> SL = NOT YET DEFINED
```

---

# 5. Critical distinction between the two strategies

## Level-to-Level

```text
Opening Low breakdown
        ↓
RED candle
        ↓
FIRST GREEN candle
        ↓
ENTRY
        ↓
Opening High = TARGET
```

## Ekalavya

```text
Opening Low breakdown
        ↓
Reversal / low
        ↓
Recovery
        ↓
Swing High
        ↓
Swing-high breakout
        ↓
ENTRY
        ↓
Opening High = TARGET
```

**Do not merge these entry conditions.**

Level-to-Level does NOT require swing-high breakout.

Ekalavya DOES require the reversal/swing-breakout structure.

---

# 6. Important correction to the previous Ekalavya implementation

Any implementation that defines Ekalavya as:

```text
premium below Opening Low
        ↓
reversal
        ↓
completed candle CLOSES ABOVE Opening High
        ↓
ENTRY
        ↓
TARGET = Opening High
```

is incorrect for this strategy definition.

Why:
- the Opening High is the target;
- if entry is only allowed after the candle closes above Opening High, the target has already been crossed.

The intended structure is:

```text
premium below Opening Low
        ↓
reversal
        ↓
swing high
        ↓
break swing high
        ↓
ENTRY BEFORE Opening High
        ↓
Opening High = TARGET
```

---

# 7. Backtesting requirements

For BOTH strategies, the backtest must report separately:

## Level-to-Level
- total candidates
- valid setups
- skipped setups
- ambiguous setups
- target hits
- SL hits
- target rate
- SL rate
- average points
- median points
- average holding time
- MFE
- MAE
- entry time distribution
- before/after 10:00 distribution
- CE vs PE
- ITM2 vs ITM3
- trading-date distribution
- reason for skipped setup

## Ekalavya
- total candidates
- valid setups
- invalid/incomplete setups
- entry count
- target hits
- SL outcomes ONLY if an explicit SL rule exists
- MFE
- MAE
- time to Opening High
- entry time
- CE vs PE
- ITM2 vs ITM3
- trading-date distribution
- reversal/swing characteristics
- false breakout count
- cases where Opening High was not reached
- cases where Opening High was reached before/after entry
- exact entry-to-target distance

Do NOT report a misleading "accuracy" number unless the numerator and denominator are clearly defined.

---

# 8. Data-quality requirements

Before accepting results:
- Verify Asia/Kolkata timestamps.
- Verify the opening 5-minute candle for every date.
- Verify option contract identity.
- Verify CE/PE.
- Verify ITM rank.
- Verify chronological ordering.
- Verify no duplicate candles.
- Verify OHLC validity.
- Verify missing-data periods.
- Do not fabricate missing candles.
- Do not use future candles for setup detection.
- Do not use future data to define a swing high or reversal.

---

# 9. Charts required for validation

For representative setups, generate charts showing:
- Opening High
- Opening Low
- option premium candles
- breakdown below Opening Low
- reversal
- swing high (Ekalavya)
- entry
- target
- SL if defined
- exit
- timestamps

Charts are for validation and visual audit. They are not themselves a substitute for causal backtest logic.

---

# 10. Learning / AI requirements

The learning system must learn from **historical events**, not from future information.

Useful features include:
- entry time
- CE/PE
- ITM rank
- premium at entry
- distance from Opening Low
- distance to Opening High
- reversal depth
- swing size
- breakout strength
- candle body/range
- wick/rejection characteristics
- MFE
- MAE
- time to target
- market/underlying context

Training must be chronological:
- older observations → training
- later observations → validation

Do not randomly shuffle time-series events for the primary validation.

Do not allow the model to select trades using information that would not have been available at entry.

The AI may identify historical patterns and estimate setup quality, but the deterministic strategy rules remain the source of truth until explicitly changed.

---

# 11. What Copilot MUST do before rerunning

Before changing or rerunning either strategy:

1. Read this entire document.
2. Inspect the current implementation.
3. Compare current code against this document.
4. Report every mismatch.
5. Do NOT silently fix ambiguous rules.
6. Do NOT modify Level-to-Level while auditing Ekalavya, or vice versa.
7. Preserve the no-order-execution safety lock.
8. Run relevant tests after approved changes.
9. Only then rerun the appropriate historical backtest.

---

# 12. Current unresolved item

### Ekalavya SL

The attached visual examples establish the reversal/swing-breakout/Opening-High-target structure, but they do not provide enough explicit information to define a precise numerical stop-loss.

Therefore this is intentionally left unresolved.

**Do not invent it.**

The next research step should be:
- inspect the existing Ekalavya SL implementation;
- show it to the user;
- compare it with the class examples;
- only change it when a clear rule is established.

---

# 13. Final canonical definitions

### LEVEL-TO-LEVEL

**NIFTY → ITM2/ITM3 → CE/PE → 5-minute**

Opening High/Low from first 5-minute candle.

**Red candle trades below Opening Low → first subsequent completed GREEN candle → ENTRY.**

**SL = Opening Low − 3 to 4 points (default project configuration: 4).**

**TARGET = Opening High.**

No extra indicators or confirmation conditions.

---

### EKALAVYA

**NIFTY → ITM2/ITM3 → CE/PE → 5-minute**

Opening High/Low from first 5-minute candle.

**Premium moves below Opening Low → low/reversal → recovery → swing high forms → premium breaks swing high → ENTRY.**

**TARGET = Opening High.**

**SL = not yet established from the supplied class examples; do not invent one.**

No requirement that entry candle closes above Opening High.

---

# 14. Non-negotiable safety

This entire project is currently:

**HISTORICAL RESEARCH + BACKTESTING + PAPER TRADING ONLY.**

Never:
- place an order
- modify an order
- cancel an order
- enable execution
- add an order API call
- remove the paper-only safety lock

Required state:

```text
EXECUTION_ALLOWED=false
PAPER_ONLY=true
KILL_SWITCH=false
```

End of canonical strategy definition.
