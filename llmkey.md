export RESEARCH_LLM_PROVIDER=groq
export RESEARCH_LLM_MODEL=openai/gpt-oss-20b
export RESEARCH_LLM_API_KEY='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'
use the abobe llm key and configure llm
You are working inside my existing private GitHub repository:

nifty-groww-ai-research

I want you to BUILD, VERIFY, and RUN a genuine AI-driven autonomous research agent for my NIFTY options research system.

IMPORTANT:
Do not merely create a deterministic wrapper called an "AI agent".
The agent must make REAL LLM calls to Groq, use the LLM's outputs to drive the research process, execute deterministic Python research, send the actual results back to the LLM, obtain an actual interpretation, and persist the complete research cycle.

At the end of this task, I want ONE REAL, BOUNDED AI research experiment to have been completed.

============================================================
PHASE 1 — INSPECT THE EXISTING PROJECT FIRST
============================================================

Before changing anything, inspect the existing repository thoroughly.

Inspect at minimum:

- app/research_agent.py
- app/research_state.py
- app/config.py
- all strategy modules
- all backtesting/research modules
- data loading modules
- Groww integration
- tests
- PROJECT_STATE.md
- RESEARCH_PLAN.md
- EXPERIMENT_LOG.md
- ERROR_LOG.md
- STRATEGY_VERSIONS.md
- NEXT_TASK.md
- existing reports
- data/raw
- data/runs

Understand the existing architecture.

Do NOT unnecessarily rewrite working deterministic research code.

The deterministic Python engine must remain responsible for:

- loading data
- validating data
- setup detection
- entry calculation
- target/SL calculation
- backtesting
- numerical calculations
- MFE
- MAE
- holding time
- drawdown
- streak calculations
- statistical summaries

The AI layer must sit above this deterministic engine.

============================================================
PHASE 2 — SAFETY IS NON-NEGOTIABLE
============================================================

This project is RESEARCH ONLY.

The following must remain:

EXECUTION_ALLOWED=false
PAPER_ONLY=true

There must be NO:

- live trading
- order placement
- order modification
- order cancellation
- automated financial transactions

Groww must remain READ-ONLY.

Do not implement order execution.

Do not add any code that can place a live order.

If existing code contains execution functionality, do not enable it.

The AI agent must NEVER be able to change these safety flags automatically.

============================================================
PHASE 3 — REAL GROQ LLM
============================================================

A Groq API key is already configured securely in the Codespace environment.

DO NOT ask me to paste the key.

DO NOT print the key.

DO NOT write the key to any file.

DO NOT commit the key.

DO NOT put it into Git.

Read it only from:

RESEARCH_LLM_API_KEY

Use:

RESEARCH_LLM_PROVIDER=groq

RESEARCH_LLM_MODEL=openai/gpt-oss-20b

If these variables are already configured, use them.

If they are not configured, report the exact missing configuration and STOP rather than faking an LLM response.

Create a clean provider abstraction.

For example:

LLMProvider
GroqProvider

The rest of the research agent should not be tightly coupled to raw HTTP calls.

The LLM provider should return structured information where possible.

============================================================
PHASE 4 — REAL AI AGENT
============================================================

The current ResearchAgent is NOT sufficient if it only does:

start_experiment()
run()
return result

Upgrade it into a genuine AI-driven research agent.

The AI agent must be capable of:

1. OBSERVING project state
2. READING previous research
3. UNDERSTANDING available data
4. UNDERSTANDING canonical strategy rules
5. GENERATING a research hypothesis
6. SELECTING a bounded experiment
7. EXECUTING deterministic Python research
8. READING the actual experiment results
9. SENDING the actual results back to the LLM
10. INTERPRETING the evidence
11. DECIDING what the evidence supports
12. GENERATING the next research question
13. PERSISTING everything

The LLM must actually influence the research process.

Do NOT hard-code:

- the hypothesis
- the experiment decision
- the interpretation
- the final decision
- the next research question

Do NOT create fake AI responses.

Do NOT write something like:

return "CE performs better"

and call that AI.

The response must actually come from the configured Groq model.

============================================================
PHASE 5 — AGENT ARCHITECTURE
============================================================

Implement a clear architecture similar to:

ResearchAgent
    |
    +-- ResearchMemory
    |
    +-- LLMProvider
    |       |
    |       +-- GroqProvider
    |
    +-- ResearchPlanner
    |
    +-- ExperimentRunner
    |
    +-- ResultAnalyzer
    |
    +-- SafetyValidator
    |
    +-- ReportWriter

You may adapt this to the existing project architecture rather than creating unnecessary duplicate classes.

The agent should have explicit stages:

OBSERVE
HYPOTHESIZE
PLAN
EXPERIMENT
ANALYZE
DECIDE
MEMORIZE

============================================================
PHASE 6 — PERSISTENT MEMORY
============================================================

Use the existing research-state infrastructure.

The AI agent must remember previous research through persistent repository state.

It should read existing:

PROJECT_STATE.md
RESEARCH_PLAN.md
EXPERIMENT_LOG.md
ERROR_LOG.md
STRATEGY_VERSIONS.md
NEXT_TASK.md

and previous experiment reports where relevant.

Do NOT create an unnecessary second memory system.

The agent must persist:

- experiment ID
- hypothesis
- dataset
- selected period
- experiment configuration
- AI reasoning
- experiment results
- AI interpretation
- decision
- proposed strategy modification
- next research question
- errors
- validation results
- LLM provider
- LLM model
- LLM call count

============================================================
PHASE 7 — BOUNDED AUTONOMOUS LOOP
============================================================

Implement a bounded autonomous mode.

Example:

python -m app.research_agent --autonomous --max-experiments 1

Support sensible controls such as:

--max-experiments
--max-failures
--dry-run
--status

For THIS task:

MAX_EXPERIMENTS = 1

The agent must NEVER automatically continue into experiment #2.

The loop is:

OBSERVE
↓
HYPOTHESIZE
↓
PLAN
↓
RUN ONE EXPERIMENT
↓
ANALYZE
↓
DECIDE
↓
SAVE
↓
STOP

============================================================
PHASE 8 — REAL LLM CONNECTION TEST
============================================================

Before running the research experiment, make exactly ONE small REAL Groq call to verify connectivity.

The call must actually reach Groq.

Do not use a mock.

Do not use a fake response.

Do not hard-code the response.

The test prompt can be something simple such as:

"You are a research assistant. Reply with the word CONNECTED and identify the
model you are running."

Verify that a real response is received.

Print only:

LLM_PROVIDER=groq
LLM_MODEL=<actual model>
LLM_CONNECTION=SUCCESS

Never print the API key.

If the connection fails:

STOP.

Show the actual error.

Do NOT continue with a fake AI response.

============================================================
PHASE 9 — CURRENT DATA
============================================================

Use the already available current-week dataset if appropriate.

Inspect:

data/raw/live-2026-09-21_2026-09-23

Do NOT unnecessarily download another large dataset.

Determine whether the data represents:

- a complete trading week
- a partial trading week
- the latest completed trading period

Do not assume 2026-09-21 to 2026-09-23 is a complete week.

If a more recent COMPLETED trading week with sufficient data already exists in
the repository, use that instead.

The AI agent may select the period, but the selection must be based on actual
available data.

Record:

SELECTED_PERIOD
START_DATE
END_DATE
DATASET
REASON_FOR_SELECTION

Do not invent missing candles.

Do not fabricate option prices.

============================================================
PHASE 10 — DATA QUALITY VALIDATION
============================================================

Before the experiment validate:

- underlying candle count
- option candle count
- timestamp validity
- Asia/Kolkata timezone
- duplicate candles
- missing intervals
- invalid OHLC
- underlying/option alignment
- option contract eligibility
- missing option observations
- stale data
- lookahead safety

If data is insufficient:

mark the experiment:

INSUFFICIENT_DATA

Do NOT invent or interpolate market data just to complete the experiment.

============================================================
PHASE 11 — CANONICAL STRATEGIES
============================================================

Do not change the canonical strategy definitions.

LEVEL_TO_LEVEL:

- NIFTY only
- 5-minute candles
- opening first 5-minute high/low
- premium below opening low
- red candle trades/breaks below Opening Low
- FIRST subsequent green 5-minute candle = entry
- entry at close of completed green candle
- no extra confirmation
- no extra indicators
- SL = opening low - configurable points
- default SL offset = 4 points
- target = opening high
- entry window follows the existing canonical project definition

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
- swing detection must be causal

IMPORTANT:

Do NOT invent an Ekalayava SL rule if the project does not already define one.

If Ekalayava SL is undefined, report it as undefined.

============================================================
PHASE 12 — BASELINE PROTECTION
============================================================

baseline-v1 is the canonical baseline.

Do NOT modify baseline-v1 during this experiment.

The AI is allowed to propose experimental changes.

If it proposes a modification, create an experimental version such as:

experimental-v2

or

experimental-v3

but do NOT promote it to baseline.

The report must clearly distinguish:

BASELINE
EXPERIMENTAL PROPOSAL
VALIDATED STRATEGY

Do not call a proposal validated unless it has actually passed proper validation.

============================================================
PHASE 13 — NO LOOKAHEAD BIAS
============================================================

This is mandatory.

Verify:

- setup detection only uses information available at that timestamp
- entries only use completed candles where required
- no future candle influences entry
- swing highs are causal
- future candles are used ONLY to determine post-entry outcome
- no future information leaks into features
- no future information is used to choose contracts retrospectively

If lookahead is detected:

MARK EXPERIMENT INVALID

Do not use the result for strategy learning.

============================================================
PHASE 14 — AI HYPOTHESIS GENERATION
============================================================

The AI must inspect:

- current project state
- previous experiment reports
- strategy definitions
- current dataset
- known data limitations

Then ask Groq to generate ONE falsifiable research hypothesis.

The hypothesis must NOT be hard-coded.

For example, the AI may investigate:

- CE vs PE
- ITM rank 2 vs rank 3
- entry time
- strategy-specific behaviour
- setup quality
- holding time
- MFE/MAE relationships

But the actual hypothesis must be generated by the LLM.

The agent must record the exact AI-generated hypothesis.

============================================================
PHASE 15 — AI EXPERIMENT SELECTION
============================================================

Ask Groq to select ONE experiment that can test the hypothesis using the
available data.

The LLM must consider:

- sample size
- data quality
- missing option observations
- potential selection bias
- lookahead risk
- whether the experiment is actually answerable

The AI must output a structured experiment plan.

The deterministic Python engine must then execute that experiment.

The LLM must NOT directly manipulate raw market data.

============================================================
PHASE 16 — DETERMINISTIC EXPERIMENT
============================================================

Run the selected experiment using the existing deterministic research engine.

Collect, where available:

- setup count
- valid setups
- skipped setups
- ambiguous setups
- target hits
- SL hits
- average points
- median points
- expectancy
- MFE
- MAE
- holding time
- maximum drawdown
- winning streak
- losing streak
- CE results
- PE results
- ITM rank 2
- ITM rank 3
- entry time
- strategy distribution

Do not invent metrics that the engine cannot calculate.

For unavailable metrics write:

NOT_AVAILABLE

============================================================
PHASE 17 — SEND REAL RESULTS BACK TO GROQ
============================================================

After the deterministic experiment finishes:

take the ACTUAL calculated results

and send them to Groq.

Do not summarize them manually in a hard-coded string that hides important
information.

Give the LLM enough structured information to analyze the experiment.

Ask Groq to determine:

1. Is the hypothesis supported?
2. What evidence supports it?
3. What evidence contradicts it?
4. Is the sample size adequate?
5. Could the observed difference be noise?
6. Are there data-quality concerns?
7. Is further validation needed?
8. Should any strategy rule be investigated?

The AI must be allowed to conclude:

ACCEPT
REJECT
NEED_MORE_DATA
INVESTIGATE

Do not force a positive conclusion.

Do not optimize solely for target-hit rate.

============================================================
PHASE 18 — AI DECISION
============================================================

The final decision must come from the real LLM response.

Persist:

AI_DECISION

AI_REASONING

EVIDENCE_FOR

EVIDENCE_AGAINST

LIMITATIONS

CONFIDENCE_OR_UNCERTAINTY

Do not turn an LLM opinion into a validated trading rule.

============================================================
PHASE 19 — NEXT RESEARCH QUESTION
============================================================

After analyzing the results, ask the LLM:

"Based on this experiment and the existing research state, what should the
research agent investigate next?"

Persist the answer.

DO NOT execute the next experiment.

This first autonomous run ends after generating the next research question.

============================================================
PHASE 20 — STRATEGY EVOLUTION
============================================================

If the AI proposes a strategy modification, record:

- experimental version
- exact rule change
- reason
- supporting evidence
- contradicting evidence
- expected impact
- validation required
- why baseline-v1 remains unchanged

Do NOT automatically implement a new trading rule just because the LLM
suggested it.

============================================================
PHASE 21 — IN-SAMPLE / OUT-OF-SAMPLE
============================================================

If the selected dataset is large enough:

split chronologically into:

DEVELOPMENT / DISCOVERY

and

VALIDATION / OUT-OF-SAMPLE

Never randomly shuffle time-series data.

If there is insufficient data for meaningful validation:

write exactly:

INSUFFICIENT OUT-OF-SAMPLE DATA

Do not pretend a tiny validation sample proves anything.

If the dataset is too small for an honest split, the agent should say so.

============================================================
PHASE 22 — ERROR HANDLING
============================================================

If an error occurs:

1. Capture it.
2. Classify it:
   - code
   - data
   - configuration
   - LLM/API
   - insufficient data
   - experiment
   - validation
3. Attempt a bounded code repair if appropriate.
4. Re-run the relevant test.
5. Never retry indefinitely.
6. Record the issue in ERROR_LOG.md.

Do NOT change strategy rules just to make an experiment pass.

============================================================
PHASE 23 — TESTS
============================================================

Add or update tests for:

- Groq provider
- missing API key
- LLM configuration
- LLM response parsing
- hypothesis generation
- experiment selection
- result interpretation
- next-question generation
- persistent memory
- autonomous loop
- max-experiments limit
- max-failures limit
- error handling
- baseline protection
- strategy versioning
- safety flags
- lookahead validation

All automated tests must use a MOCK/FAKE LLM.

Tests must NOT consume real Groq API calls.

Run the full test suite.

Fix failures before the real demo.

============================================================
PHASE 24 — REPORT STORAGE
============================================================

The real AI-agent experiment report MUST be permanently saved in:

data/runs/<actual_selected_period>/reports/

Create BOTH:

ai_agent_demo_report.json

ai_agent_demo_report.md

Example only:

data/runs/2026-09-21_2026-09-23/reports/ai_agent_demo_report.json

data/runs/2026-09-21_2026-09-23/reports/ai_agent_demo_report.md

Use the ACTUAL selected period.

The JSON must contain structured machine-readable information.

The Markdown must be human-readable.

The report MUST include:

------------------------------------------------------------
AI AGENT DEMO REPORT
------------------------------------------------------------

Experiment ID

Selected period

Dataset

Data quality

Underlying candle count

Option coverage

Missing intervals

Duplicate count

Invalid OHLC count

Timezone

Lookahead validation

------------------------------------------------------------
AI REASONING
------------------------------------------------------------

LLM provider

LLM model

LLM call count

AI-generated hypothesis

AI-selected experiment

------------------------------------------------------------
EXPERIMENT RESULTS
------------------------------------------------------------

Setup count

Valid setups

Skipped setups

Ambiguous setups

Target hits

SL hits

Average points

Median points

Expectancy if available

MFE

MAE

Holding time

Drawdown

Streaks

CE results

PE results

ITM 2 results

ITM 3 results

Entry-time results

------------------------------------------------------------
AI INTERPRETATION
------------------------------------------------------------

Evidence for

Evidence against

Limitations

AI decision

------------------------------------------------------------
STRATEGY EVOLUTION
------------------------------------------------------------

Any proposed strategy modification

Why it was proposed

Validation required

Baseline-v1 status

------------------------------------------------------------
NEXT RESEARCH
------------------------------------------------------------

Next research question

------------------------------------------------------------
SAFETY
------------------------------------------------------------

EXECUTION_ALLOWED=false

PAPER_ONLY=true

Groww read-only

No order execution

------------------------------------------------------------

NEVER put:

- API keys
- secrets
- access tokens
- authorization headers
- passwords

inside the reports.

============================================================
PHASE 25 — UPDATE PERSISTENT RESEARCH FILES
============================================================

After the experiment update:

PROJECT_STATE.md
EXPERIMENT_LOG.md
ERROR_LOG.md
STRATEGY_VERSIONS.md
NEXT_TASK.md

Do not destroy previous research history.

Append/update carefully.

Record:

- what happened
- experiment ID
- selected dataset
- hypothesis
- results
- AI interpretation
- decision
- limitations
- next research question

============================================================
PHASE 26 — LLM USAGE TRACKING
============================================================

Track:

LLM provider

LLM model

LLM call count

prompt tokens if available

completion tokens if available

total tokens if available

agent step count

experiment count

errors/retries

Print at the end:

LLM_PROVIDER=groq
LLM_MODEL=<model>
LLM_CALL_COUNT=<number>
EXPERIMENT_COUNT=1
AGENT_STEP_COUNT=<number>

Do not claim a particular number of Groq credits unless the API actually
returns such information.

============================================================
PHASE 27 — CLI
============================================================

Ensure this works:

python -m app.research_agent --status

and:

python -m app.research_agent --autonomous --max-experiments 1

The autonomous command must:

- load state
- inspect data
- call the real LLM
- generate hypothesis
- select experiment
- execute exactly one experiment
- analyze results
- call the real LLM with results
- produce AI interpretation
- produce next research question
- save report
- update persistent state
- stop

============================================================
PHASE 28 — FINAL SECURITY AUDIT
============================================================

Before declaring success verify:

[ ] EXECUTION_ALLOWED=false
[ ] PAPER_ONLY=true
[ ] Groww remains read-only
[ ] no order placement
[ ] no order modification
[ ] no order cancellation
[ ] no API key in Git
[ ] no API key in reports
[ ] no API key in logs
[ ] baseline-v1 unchanged
[ ] no lookahead
[ ] data validated
[ ] real Groq call completed
[ ] AI-generated hypothesis was actually used
[ ] deterministic experiment actually ran
[ ] actual results were sent back to Groq
[ ] Groq generated the interpretation
[ ] next research question was generated
[ ] persistent memory updated
[ ] report saved
[ ] exactly ONE experiment executed
[ ] tests pass

============================================================
PHASE 29 — IMPORTANT: DO NOT FAKE SUCCESS
============================================================

If any of the following happens:

- Groq API unavailable
- API key missing
- provider misconfigured
- LLM call fails
- data insufficient
- experiment fails
- lookahead detected
- report cannot be written

DO NOT pretend the AI agent worked.

Clearly report:

WHAT WORKED
WHAT FAILED
WHY IT FAILED
WHAT NEEDS TO BE FIXED

Do not fabricate LLM output.

============================================================
PHASE 30 — FINAL OUTPUT
============================================================

After everything is complete, give me a concise final summary containing:

1. Whether a REAL AI agent was successfully created.
2. Whether a REAL Groq LLM call succeeded.
3. LLM provider/model.
4. Number of LLM calls.
5. Number of experiments executed.
6. Selected data period.
7. AI-generated hypothesis.
8. Experiment result summary.
9. AI interpretation.
10. AI decision.
11. Next research question.
12. Whether baseline-v1 was changed.
13. Number of tests passed.
14. Exact report paths.
15. Exact files changed.
16. Any remaining limitations.

MOST IMPORTANT:

Do not merely tell me that an AI agent exists.

PROVE it through the execution trace:

REAL LLM CALL
→ AI HYPOTHESIS
→ AI EXPERIMENT PLAN
→ REAL PYTHON EXPERIMENT
→ REAL RESULTS
→ RESULTS SENT TO LLM
→ AI INTERPRETATION
→ AI DECISION
→ NEXT RESEARCH QUESTION
→ PERSISTED REPORT

Only after this complete chain succeeds should you report:

AI_AGENT_DEMO=SUCCESS

If any part of that chain did not actually happen, report:

AI_AGENT_DEMO=FAILED

with the exact reason.

START NOW.