# Research Plan

## Baseline

Preserve the canonical rules in `NIFTY_Strategy_Definitions_Level_to_Level_Ekalavya.md`. Do not modify baseline strategy code while collecting evidence.

## Agent Loop

1. Inspect source, data quality, prior reports, and the latest checkpoint.
2. Write a falsifiable hypothesis and identify the dataset.
3. Run one bounded experiment through `ResearchAgent`.
4. Validate candles, timestamps, alignment, contract eligibility, and lookahead constraints.
5. Save raw and processed results without overwriting prior reports.
6. Compare setup count, outcomes, points, MFE, MAE, holding time, drawdown, streaks, CE/PE, ITM rank, and time of day.
7. Separate in-sample discovery from out-of-sample validation.
8. Record the decision and define the next experiment.

## Guardrails

- A poor result is a research finding, not a reason to rewrite the strategy.
- Missing or incomplete data is reported as insufficient data.
- Experimental rules require a new version identifier and baseline comparison.
- No experiment may call an order placement, modification, or cancellation API.