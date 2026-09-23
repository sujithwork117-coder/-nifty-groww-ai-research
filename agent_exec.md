You are working inside my existing repository:

nifty-groww-ai-research

I want you to upgrade the existing ResearchAgent into a GENUINE AI-DRIVEN
SELF-THINKING RESEARCH AGENT and then run ONE REAL, BOUNDED DEMONSTRATION
using the latest completed trading week available in the repository.

The purpose is to prove that the agent can actually reason, research,
interpret results and decide what to investigate next.

Do NOT fake AI reasoning.

============================================================
1. FIRST: INSPECT THE EXISTING PROJECT
============================================================

Before changing anything, inspect:

- app/research_agent.py
- app/research_state.py
- app/config.py
- all existing research/backtest modules
- strategy implementation
- data loading modules
- PROJECT_STATE.md
- RESEARCH_PLAN.md
- EXPERIMENT_LOG.md
- ERROR_LOG.md
- STRATEGY_VERSIONS.md
- NEXT_TASK.md
- existing tests
- existing reports
- available historical datasets

Understand the existing architecture before modifying it.

Do NOT unnecessarily rewrite the deterministic research engine.

The deterministic Python research/backtesting engine must remain responsible
for calculations and actual experiment execution.

The AI layer must sit ABOVE that engine.

============================================================
2. NON-NEGOTIABLE SAFETY
============================================================

Keep:

EXECUTION_ALLOWED=false
PAPER_ONLY=true

There must be NO:

- live trading
- order placement
- order modification
- order cancellation
- broker execution
- automated financial transactions

Groww access must remain READ-ONLY.

Do not add any order execution functionality.

============================================================
3. BUILD A REAL AI REASONING LAYER
============================================================

The current ResearchAgent is only an orchestration wrapper.

Upgrade it into a genuine AI research agent that can actually call a
configurable LLM.

Create a clean provider abstraction such as:

LLMProvider

or an equivalent interface.

The provider must support:

- configurable AI provider
- configurable model
- API key through environment variables
- configurable generation settings where appropriate

NEVER hard-code API keys.

NEVER commit secrets.

NEVER create fake/hard-coded AI responses.

If no AI provider is configured, the program must clearly report that
configuration is missing.

============================================================
4. THE REAL AI RESEARCH LOOP
============================================================

Implement a bounded autonomous loop:

OBSERVE
↓
READ PROJECT STATE
↓
UNDERSTAND STRATEGY + DATA
↓
GENERATE HYPOTHESIS
↓
SELECT EXPERIMENT
↓
RUN DETERMINISTIC BACKTEST
↓
ANALYZE RESULTS
↓
COMPARE WITH BASELINE
↓
SEND RESULTS TO LLM
↓
AI INTERPRETATION
↓
DECIDE:
    ACCEPT
    REJECT
    NEED_MORE_DATA
    INVESTIGATE
↓
GENERATE NEXT RESEARCH QUESTION
↓
PERSIST MEMORY
↓
STOP

The agent must have hard limits:

- max experiments
- max failures
- max retries
- max runtime

For the first real demonstration, use:

MAX EXPERIMENTS = 1

The purpose of the demo is to prove the AI loop works, not to perform a
massive optimization run.

============================================================
5. WHAT MAKES THIS A REAL AI AGENT
============================================================

The AI must genuinely perform these tasks:

1. Generate a hypothesis.
2. Decide what experiment to run.
3. Read the experiment result.
4. Interpret the result.
5. Decide whether the hypothesis is supported.
6. Decide whether the evidence is insufficient.
7. Propose the next research question.

The AI response must actually be used by the program.

Do NOT generate predetermined hypotheses in Python.

Do NOT hard-code conclusions.

Do NOT call a deterministic rule engine "AI".

============================================================
6. PERSISTENT RESEARCH MEMORY
============================================================

Integrate with the existing ResearchState and research documentation.

The agent should remember:

- previous experiments
- hypotheses
- experiment results
- conclusions
- rejected hypotheses
- accepted hypotheses
- insufficient-data findings
- strategy versions
- errors
- proposed next experiments

Preserve the existing files:

PROJECT_STATE.md
RESEARCH_PLAN.md
EXPERIMENT_LOG.md
ERROR_LOG.md
STRATEGY_VERSIONS.md
NEXT_TASK.md

Do not create an incompatible second memory system.

============================================================
7. STRATEGY LEARNING / EVOLUTION
============================================================

The AI IS ALLOWED to propose changes to the trading strategy.

This is intentional.

Do NOT artificially restrict it to only evaluating the existing rules.

However, it must NEVER overwrite the canonical baseline.

Maintain:

baseline-v1

as the permanent baseline.

Any experimental modification must become a new version, for example:

experimental-v2
experimental-v3

etc.

Every proposed strategy change must contain:

- hypothesis
- exact rule change
- reason for change
- baseline comparison
- results
- out-of-sample validation where possible
- robustness assessment
- decision:
  ACCEPT
  REJECT
  NEED_MORE_DATA

Do not optimize solely for target-hit percentage.

Consider:

- setup count
- valid/skipped/ambiguous
- target hits
- SL hits
- points
- average points
- median points
- expectancy
- MFE
- MAE
- holding time
- drawdown
- losing/winning streaks
- CE vs PE
- ITM rank
- entry time
- market regime/date behaviour

If data is insufficient, the correct conclusion is:

NEED_MORE_DATA

Do not manufacture certainty.

============================================================
8. PRESERVE THE CANONICAL STRATEGIES
============================================================

LEVEL_TO_LEVEL:

- NIFTY only
- 5-minute candles
- opening first 5-minute high/low
- premium below opening low
- red candle trades/breaks below Opening Low
- FIRST subsequent green 5-minute candle = entry
- entry at close of completed green candle
- no extra confirmation
- SL = opening low - configurable points
- default SL offset = 4 points
- target = opening high

EKALAYAVA:

- opening high/low
- premium falls below opening low
- low/reversal develops
- recovery
- swing high forms during recovery
- premium breaks swing high
- entry on causal swing-high breakout before opening high
- target = opening high
- no requirement for entry candle to close above opening high
- no mandatory textbook candle
- no extra indicators
- causal swing detection only

Do NOT invent an Ekalayava SL rule if one is not already defined.

============================================================
9. NO LOOKAHEAD BIAS
============================================================

This is mandatory.

The agent must verify:

- entry uses only information available at entry time
- completed candles only
- no future candle used for setup detection
- causal swing detection
- no future data leakage
- outcome candles occur only after entry

If an experiment violates this:

STOP IT.

Mark it INVALID.

Do not use its result for learning.

============================================================
10. DATA VALIDATION
============================================================

Before running the real weekly experiment, inspect the available data.

Check:

- NIFTY underlying coverage
- option coverage
- timestamps
- timezone
- duplicate candles
- missing intervals
- invalid OHLC
- contract eligibility
- alignment between underlying and option data
- data gaps
- lookahead safety

Do not silently fill missing market data.

If coverage is inadequate, report:

INSUFFICIENT DATA

instead of pretending the experiment is valid.

============================================================
11. REAL DEMO — LATEST COMPLETED TRADING WEEK
============================================================

THIS IS THE IMPORTANT PART.

After the AI layer and tests are complete, run ONE REAL AI-DRIVEN
research experiment using the LATEST COMPLETED TRADING WEEK available
in the repository.

Do NOT assume a specific date.

First inspect the available historical data and determine:

- latest available trading date
- latest fully completed Monday-Friday trading week
- whether sufficient NIFTY data exists
- whether sufficient option data exists
- whether the week has enough usable data for the experiment

Select the latest COMPLETED week with sufficient data.

Document exactly which dates were selected and why.

Do NOT use an incomplete current week.

Do NOT fabricate missing data.

============================================================
12. REAL WEEKLY EXPERIMENT
============================================================

For this ONE real experiment:

Start from:

baseline-v1

Do NOT modify baseline-v1 before running it.

The AI should inspect the research context and generate a falsifiable
hypothesis.

For example, it may investigate relationships involving:

- CE vs PE
- ITM 2 vs ITM 3
- entry time
- setup quality
- strategy behaviour
- market regime

BUT DO NOT hard-code the hypothesis.

The AI itself must generate the hypothesis based on the available context.

Then:

1. AI generates hypothesis.
2. AI selects the experiment.
3. Python deterministic engine executes it.
4. Results are returned to the AI.
5. AI interprets results.
6. AI decides:
   ACCEPT
   REJECT
   NEED_MORE_DATA
   INVESTIGATE
7. AI proposes the next research question.
8. Persist everything.

============================================================
13. CHRONOLOGICAL VALIDATION
============================================================

If the selected week contains enough data:

Use a chronological development/validation split where possible.

Do NOT randomly shuffle time-series data.

The AI must clearly distinguish:

IN-SAMPLE / DEVELOPMENT

from

OUT-OF-SAMPLE / VALIDATION

If the validation portion is too small:

explicitly report:

INSUFFICIENT OUT-OF-SAMPLE DATA

Do not pretend that a tiny validation set proves anything.

============================================================
14. REAL EXPERIMENT OUTPUT
============================================================

The experiment should report at minimum:

- selected week
- date range
- dataset used
- strategy version
- hypothesis
- setup count
- valid setups
- skipped setups
- ambiguous setups
- target hits
- SL hits
- average points
- median points
- MFE
- MAE
- holding time
- drawdown
- streaks
- CE results
- PE results
- ITM 2 results
- ITM 3 results
- entry-time results
- data quality
- lookahead validation
- development results
- validation results where possible

============================================================
15. AI RESULT INTERPRETATION
============================================================

Send the actual experiment results to the LLM.

Ask it to reason about:

- whether the hypothesis was supported
- what evidence supports the conclusion
- what evidence contradicts it
- whether the result could be caused by insufficient data
- whether the result appears robust
- whether a strategy modification is justified
- what should be tested next

The AI must not claim statistical certainty from a small sample.

The AI must be allowed to say:

"I don't know."

"Insufficient data."

"Needs more validation."

"Do not change the strategy."

These are valid research conclusions.

============================================================
16. STRATEGY MODIFICATION
============================================================

For THIS FIRST REAL WEEKLY DEMO:

DO NOT automatically promote any strategy change to production/baseline.

The AI may:

- propose a strategy modification
- create an experimental strategy version
- explain the modification

But baseline-v1 must remain unchanged.

Any experimental change must be clearly marked experimental.

Do not execute live trades.

============================================================
17. SELF-REPAIR
============================================================

If the experiment encounters a code/data error:

1. Capture the error.
2. Diagnose it.
3. Determine whether it is:
   - code
   - data
   - configuration
   - insufficient data
   - invalid experiment
4. Attempt a bounded repair if appropriate.
5. Re-run only within limits.
6. Record the repair.

Do not retry indefinitely.

Do not silently alter strategy rules just to make the experiment succeed.

============================================================
18. TESTS
============================================================

Add tests for:

- LLM provider
- missing API configuration
- hypothesis generation
- experiment selection
- result interpretation
- next research question
- persistent state
- bounded autonomous loop
- error handling
- safety checks
- baseline preservation
- strategy versioning
- no-lookahead validation

Use a mocked/fake LLM in tests.

Tests must NOT require a real paid API.

Run the entire test suite.

Fix failures before the real weekly demo.

============================================================
19. CLI
============================================================

Provide a CLI similar to:

python -m app.research_agent --autonomous

Support bounded options such as:

--max-experiments
--max-failures
--dry-run
--status

For the real demo, use:

--max-experiments 1

Do not run multiple experiments.

============================================================
20. AI PROVIDER CONFIGURATION
============================================================

Use environment variables.

Do not commit credentials.

If the configured provider requires an API key and none exists:

STOP before the real demo.

Print exactly what configuration is missing.

Do NOT fake an AI response.

Do NOT substitute deterministic text.

============================================================
21. FINAL DEMO REPORT
============================================================

After the real weekly experiment finishes, print:

========================================
REAL AI RESEARCH AGENT DEMO REPORT
========================================

AI PROVIDER:
AI MODEL:
REAL LLM CALL SUCCESSFUL: YES/NO

LATEST COMPLETED WEEK:
START DATE:
END DATE:

DATA QUALITY:
NIFTY COVERAGE:
OPTION COVERAGE:
MISSING DATA:
LOOKAHEAD CHECK:

HYPOTHESIS GENERATED BY AI:

EXPERIMENT SELECTED BY AI:

EXPERIMENT ID:

BASELINE RESULTS:

EXPERIMENT RESULTS:

AI INTERPRETATION:

AI DECISION:

STRATEGY CHANGE PROPOSED:
YES/NO

IF YES:
EXPERIMENTAL VERSION:
DESCRIPTION:

OUT-OF-SAMPLE VALIDATION:
SUFFICIENT / INSUFFICIENT

NEXT RESEARCH QUESTION GENERATED BY AI:

PERSISTENT STATE UPDATED:
YES/NO

FILES UPDATED:

TOTAL AUTONOMOUS STEPS:

DEMO SUCCESS:
YES/NO

============================================================
22. FINAL SECURITY / INTEGRITY CHECK
============================================================

Before finishing:

1. Run all tests.
2. Confirm EXECUTION_ALLOWED=false.
3. Confirm PAPER_ONLY=true.
4. Confirm no order APIs exist.
5. Confirm Groww remains read-only.
6. Confirm no secrets were committed.
7. Confirm baseline-v1 was not overwritten.
8. Confirm the LLM was actually called.
9. Confirm the LLM response affected the research decision.
10. Confirm the real latest completed week was used.
11. Confirm the experiment was bounded to ONE experiment.
12. Confirm persistent research state was updated.
13. Show all files changed.
14. Show the final git commit hash if a commit was created.

IMPORTANT:

Do NOT tell me that the system is a "self-thinking AI agent" merely because
the Python program runs.

It is only considered successful if:

REAL LLM CALL
        ↓
AI HYPOTHESIS
        ↓
AI EXPERIMENT SELECTION
        ↓
REAL HISTORICAL DATA
        ↓
DETERMINISTIC BACKTEST
        ↓
REAL RESULTS
        ↓
LLM INTERPRETATION
        ↓
AI DECISION
        ↓
NEXT RESEARCH QUESTION
        ↓
PERSISTENT MEMORY

actually happens.

Do not run a large multi-week optimization.

Run exactly ONE real bounded experiment on the latest completed trading week
with sufficient data.