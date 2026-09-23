# Canonical Two-Month Groww AI Research Report

- Experiment ID: EXP-8ee0e64d66
- Generated: 2026-09-23T15:23:31.516520+00:00
- Provider/model: groq / openai/gpt-oss-20b
- Dataset: data/runs/canonical_two_months_20260923_151545/nifty_5m.csv
- Selected period: {'start': '2026-09-07', 'end': '2026-09-11', 'trading_dates': ['2026-09-07', '2026-09-08', '2026-09-09', '2026-09-10', '2026-09-11']}
- Contracts: NIFTY ITM 2/3 CE/PE
- Missing option candles: unavailable; no interpolation or fabrication

## Hypothesis
LEVEL_TO_LEVEL and EKALAYAVA strategies will achieve higher average daily points compared to the baseline over the two-month period ending 2026-09-23.

## Experiment Specification
```json
{
  "comparison_dimension": "strategy",
  "dataset_period": "2026-07-23 to 2026-09-23",
  "hypothesis": "LEVEL_TO_LEVEL and EKALAYAVA strategies will achieve higher average daily points compared to the baseline over the two-month period ending 2026-09-23.",
  "minimum_data_requirements": [
    "completed 5-minute candles",
    "ITM 2 and 3 CE/PE"
  ],
  "reason": "To validate the effectiveness of canonical strategies over the baseline, ensuring data completeness and contract eligibility for the specified period.",
  "required_groupings": [
    "strategy"
  ],
  "required_metrics": [
    "strategy_breakdown",
    "average_daily_points_by_strategy"
  ],
  "statistical_test": null,
  "strategy_scope": [
    "LEVEL_TO_LEVEL",
    "EKALAYAVA"
  ]
}
```

## Deterministic Results
- Setup count: 31
- Valid setups: 25
- Targets: 16
- SL: 9
- Open: 6
- Average points: 7.040000000000003
- Median points: 4.699999999999999
- MFE: 55.77096774193549
- MAE: -76.19032258064514
- Strategy breakdown: {"EKALAYAVA": {"average_daily_points": 17.39999999999999, "average_points_per_setup": 6.959999999999996, "days": 5, "open_outcomes": 6, "points": 69.59999999999997, "setups": 16, "sl_hits": 0, "target_hits": 10, "valid_setups": 10}, "LEVEL_TO_LEVEL": {"average_daily_points": 21.28000000000002, "average_points_per_setup": 7.093333333333339, "days": 5, "open_outcomes": 0, "points": 106.40000000000009, "setups": 15, "sl_hits": 9, "target_hits": 6, "valid_setups": 15}}
- CE/PE breakdown: {"CE": 20, "PE": 11}
- ITM breakdown: {"2": 15, "3": 16}
- Entry-time breakdown: {"10": 6, "11": 1, "12": 1, "9": 23}
- Result completeness: PASS
- Lookahead: PASS: deterministic engine uses completed candles and future candles only after entry

## Groq Interpretation
- Decision: NEED_MORE_DATA
- Supported evidence: LEVEL_TO_LEVEL and EKALAYAVA strategies achieved average daily points of 21.28 and 17.40 respectively over the 5 trading days in the dataset, which are higher than the overall average points of 7.04 reported for all setups. However, the baseline average daily points for comparison are not provided in the result, so the hypothesis that these strategies outperform the baseline cannot be confirmed.
- Contradictory evidence: METRIC NOT AVAILABLE
- Limitations: 1. Baseline average daily points metric is missing, preventing direct comparison. 2. Only 5 trading days (one week) of data are available, limiting statistical power. 3. Several option contracts have missing intervals (e.g., 125 missing for 24250-PE, 34 missing for 24400-PE), indicating incomplete candle data. 4. Contract coverage shows zero contract_count entries, suggesting potential data extraction issues. 5. The experiment notes insufficient out-of-sample data and reserves one week for validation, further limiting evidence.
- Next question: What are the baseline average daily points for the baseline-v1 strategy over the same two‑month period, and can the missing option candle data be filled or excluded to provide a complete dataset?
