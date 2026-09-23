You are working on my existing NIFTY Groww AI research repository.

The GitHub repository is the SOURCE OF TRUTH.

Do NOT rebuild the project from scratch. First inspect and understand the complete existing repository, including:
- strategy definitions
- Python code
- tests
- data pipeline
- latest research reports
- configuration
- README/documentation
- current project state

==================================================
1. BUILD AN AUTONOMOUS AI RESEARCH AGENT
==================================================

I want this repository to contain the infrastructure required for an AI research/coding agent to continuously work on the project.

The agent's job is NOT simply to answer questions.

It should be able to operate as an autonomous research engineer:

    INSPECT
       ↓
    PLAN
       ↓
    RUN
       ↓
    OBSERVE
       ↓
    DIAGNOSE
       ↓
    MODIFY CODE IF REQUIRED
       ↓
    TEST
       ↓
    RERUN
       ↓
    ANALYZE RESULTS
       ↓
    FORM HYPOTHESIS
       ↓
    DESIGN NEXT EXPERIMENT
       ↓
    VALIDATE
       ↓
    SAVE RESULTS
       ↓
    UPDATE PROJECT STATE
       ↓
    CONTINUE

The agent must be able to recover from normal implementation errors without requiring me to manually intervene every time.

For example:

Python execution fails
        ↓
Agent reads traceback
        ↓
Agent identifies root cause
        ↓
Agent inspects relevant files
        ↓
Agent modifies the implementation
        ↓
Agent adds/fixes regression test
        ↓
Agent runs tests
        ↓
Agent reruns the failed research
        ↓
Agent verifies the result
        ↓
Agent continues

Do NOT simply catch exceptions and hide them.

==================================================
2. AGENT MEMORY / PERSISTENT PROJECT STATE
==================================================

Create a persistent research state system so that a new AI agent can open the repository and understand what has already happened.

Create or improve files such as:

PROJECT_STATE.md
RESEARCH_PLAN.md
EXPERIMENT_LOG.md
ERROR_LOG.md
STRATEGY_VERSIONS.md
NEXT_TASK.md

Use the existing repository structure if equivalent files already exist rather than creating unnecessary duplicates.

PROJECT_STATE should contain:
- current project status
- current strategy version
- latest completed experiment
- latest research period
- latest research report
- known data limitations
- known implementation issues
- tests currently passing/failing
- current research objectives
- next recommended action

EXPERIMENT_LOG should contain every experiment and its results.

ERROR_LOG should contain important implementation/data errors and their fixes.

NEXT_TASK should clearly state what the next AI agent should work on.

The state must be updated after meaningful research milestones.

==================================================
3. AGENT MUST BE ABLE TO WORK ITERATIVELY
==================================================

The agent should NOT stop after one successful Python execution.

After completing an experiment, it should inspect the results and determine whether another research experiment is justified.

The agent should be able to:

- identify interesting patterns
- identify weak areas
- identify unexpected behavior
- formulate hypotheses
- design follow-up experiments
- run those experiments
- compare results
- document conclusions

However, the agent must avoid endless meaningless experiments.

Every new experiment must have a documented reason/hypothesis.

==================================================
4. AGENT MUST DISTINGUISH CODE ERRORS FROM RESEARCH FINDINGS
==================================================

If something fails because of a programming/data-pipeline error:

FIX THE CODE.

If something performs poorly because the strategy genuinely performs poorly:

DO NOT "fix" the result.

Instead:
- record the result
- investigate why
- formulate a research hypothesis
- test a potential strategy modification

Never manipulate code simply to make a result look better.

==================================================
5. STRATEGY LEARNING / EVOLUTION
==================================================

The agent IS allowed to evolve the strategies based on historical evidence.

The existing Level-to-Level and Ekalayava strategies are the BASELINE.

They are not permanently frozen.

The agent may propose changes to:
- entry conditions
- timing conditions
- candle conditions
- breakout/reversal logic
- ITM selection
- filters
- exits
- stop-loss logic
- target logic
- other strategy parameters

BUT every change must be treated as a research hypothesis.

The required process is:

BASELINE
    ↓
OBSERVE HISTORICAL PATTERN
    ↓
FORM HYPOTHESIS
    ↓
CREATE EXPERIMENTAL STRATEGY VERSION
    ↓
BACKTEST
    ↓
COMPARE WITH BASELINE
    ↓
OUT-OF-SAMPLE TEST
    ↓
ROBUSTNESS TEST
    ↓
ACCEPT / REJECT / NEED MORE DATA

Never silently modify the baseline.

==================================================
6. STRATEGY VERSIONING
==================================================

Maintain:

BASELINE STRATEGY
EXPERIMENTAL STRATEGY
CURRENT VALIDATED STRATEGY

Every strategy modification must receive a version identifier.

For every modification record:

- strategy name
- previous version
- new version
- exact rule changed
- reason for change
- historical evidence
- hypothesis
- datasets used
- in-sample results
- out-of-sample results
- comparison with baseline
- decision
- date
- experiment IDs

Never overwrite historical strategy versions.

==================================================
7. DO NOT OPTIMIZE FOR ACCURACY ALONE
==================================================

The agent must NOT optimize only for target-hit accuracy.

Evaluate:

- setup count
- valid setups
- skipped setups
- target hits
- SL hits
- target-hit rate
- SL-hit rate
- average points
- median points
- expectancy where valid
- MFE
- MAE
- maximum drawdown
- holding time
- winning/losing streaks
- setup frequency
- CE vs PE
- ITM 2 vs ITM 3
- entry time
- market regime/period where available

A higher accuracy is NOT automatically better.

A strategy modification should only be considered successful if the evidence shows meaningful improvement in the relevant overall trading characteristics and the improvement survives validation.

==================================================
8. OUT-OF-SAMPLE VALIDATION
==================================================

The agent must understand the difference between:

IN-SAMPLE DATA
and
OUT-OF-SAMPLE DATA.

Do not use the same historical observations both to discover a rule and to claim that the rule has been independently validated.

When enough data exists, maintain separate research/development and validation periods.

If insufficient historical data exists:

REPORT:

INSUFFICIENT OUT-OF-SAMPLE DATA

Do not pretend validation exists.

==================================================
9. RESEARCH INTEGRITY
==================================================

Never:

- use future candles to determine an entry
- use future information to modify a past decision
- invent candles
- invent option prices
- fabricate missing data
- silently discard losing setups
- selectively remove bad trades
- change historical data
- manipulate timestamps
- use future contract information
- introduce lookahead bias
- hide data-quality problems

If required data is unavailable:

MARK THE SETUP/EXPERIMENT AS INVALID OR INSUFFICIENT DATA

according to the existing project conventions.

==================================================
10. DATA QUALITY CHECKS
==================================================

Before trusting a research result, check:

- missing intervals
- duplicate candles
- invalid OHLC
- timezone
- underlying/option alignment
- option data coverage
- stale data
- incomplete contracts
- cross-day contamination
- future timestamps
- contract selection
- missing required candles

If data quality could materially affect the result, explicitly flag it.

==================================================
11. EXISTING STRATEGY SAFETY
==================================================

Preserve the current strategy definitions as the initial baseline.

Maintain:

- NIFTY only
- CE/PE
- ITM rank 2 and 3
- 5-minute candles
- Asia/Kolkata timezone
- opening 5-minute high/low
- causal calculations
- no lookahead
- completed-candle logic where required
- no cross-day contamination

Do NOT introduce actual trading.

These settings must remain enforced:

EXECUTION_ALLOWED=false
PAPER_ONLY=true

There must be NO order placement, modification or cancellation functionality.

==================================================
12. AGENT SHOULD USE PYTHON FOR HEAVY COMPUTATION
==================================================

Do not waste AI reasoning credits processing every candle manually.

The agent should write efficient Python code that performs:

- historical backtesting
- feature calculation
- setup detection
- outcome calculation
- statistical analysis
- experiment comparison
- report generation

The AI agent should handle:

- planning
- debugging
- interpretation
- hypothesis generation
- experiment design
- code changes
- validation
- research conclusions

Python should handle the repetitive computation.

==================================================
13. AUTOMATIC ERROR RECOVERY
==================================================

When a command fails:

1. Read the complete error.
2. Identify the root cause.
3. Inspect relevant code.
4. Fix the smallest appropriate part.
5. Add a regression test if appropriate.
6. Run tests.
7. Rerun the failed command.
8. Compare against the previous working state.
9. Record the error and fix.
10. Continue the research task.

Do not repeatedly make random changes.

If the same failure occurs repeatedly, stop modifying blindly and investigate the root cause systematically.

==================================================
14. AUTONOMOUS EXPERIMENT SELECTION
==================================================

After an experiment completes, analyze its results.

The agent may choose the next experiment based on:

- statistically interesting differences
- poor-performing segments
- strong recurring patterns
- CE/PE differences
- ITM2/ITM3 differences
- time-of-day differences
- strategy differences
- market-period differences
- MFE/MAE behavior
- target/SL behavior
- setup quality
- data quality

But every experiment must have a written hypothesis.

Example:

"PE setups appear to behave differently from CE setups. Test whether this difference remains across multiple historical periods before considering a strategy change."

NOT:

"PE performed better, so permanently change the strategy to PE."

==================================================
15. EXPERIMENT CHECKPOINTS
==================================================

After meaningful experiments:

- save the raw result
- save processed results
- generate a report
- update EXPERIMENT_LOG
- update PROJECT_STATE
- update NEXT_TASK
- preserve previous reports
- create a Git checkpoint/commit when appropriate

Another AI agent must be able to continue from the repository without requiring me to explain the project again.

==================================================
16. CURRENT TASK — BUILD THE AGENT INFRASTRUCTURE FIRST
==================================================

For THIS task:

DO NOT immediately launch a massive historical research run.

First inspect the repository thoroughly.

Then:

1. Identify the existing architecture.
2. Identify existing research/backtesting functionality.
3. Identify existing tests.
4. Identify existing strategy definitions.
5. Identify existing reports.
6. Identify existing state/logging functionality.
7. Build the autonomous research-agent infrastructure.
8. Add persistent project state.
9. Add experiment tracking.
10. Add strategy version tracking.
11. Add error tracking.
12. Add resumability/checkpointing.
13. Add automated validation where appropriate.
14. Add tests.
15. Run the tests.
16. Fix genuine errors.
17. Verify:

EXECUTION_ALLOWED=false
PAPER_ONLY=true

18. Do NOT start modifying strategy rules yet.

==================================================
17. AFTER INFRASTRUCTURE IS COMPLETE
==================================================

Once the infrastructure is working, prepare the repository so that the next task can be:

"Run the latest completed week's historical data, analyze the results, identify potential patterns, and propose the next research experiment."

Do not run that large experiment during this infrastructure task unless required to validate the infrastructure.

==================================================
18. FINAL REPORT
==================================================

At the end of this task, report:

- files inspected
- files created
- files modified
- existing components reused
- agent capabilities implemented
- autonomous loop implemented
- persistent state implemented
- experiment tracking implemented
- strategy versioning implemented
- error recovery implemented
- tests executed
- test results
- remaining issues
- exact next task for the research agent

IMPORTANT:

Do not ask me to explain the existing project if the repository contains the information.

Do not delete existing research.

Do not overwrite the latest research report.

Do not rebuild working components unnecessarily.

Do not change strategy rules during this infrastructure task.

The final goal is:

A persistent AI-assisted NIFTY historical research system where an AI coding/research agent can inspect the repository, run experiments, detect and fix genuine code errors, analyze historical results, formulate hypotheses, evolve strategy rules when evidence supports doing so, validate those changes on unseen data, document every change, and continue from the previous state without requiring manual re-explanation.