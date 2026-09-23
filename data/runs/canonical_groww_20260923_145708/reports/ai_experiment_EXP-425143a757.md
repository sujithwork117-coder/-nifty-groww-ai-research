# Canonical Groww AI Research Report

- Experiment ID: EXP-425143a757
- Provider/model: groq / openai/gpt-oss-20b
- Strategy: canonical NIFTY Level-to-Level + Ekalayava
- Contracts: ITM 2 and ITM 3 CE/PE only
- Missing option candles: unavailable; no interpolation or fabrication
- Previous SMA experiment: discarded as invalid/inconclusive

## Hypothesis
The LEVEL_TO_LEVEL strategy produces a statistically higher average daily profit than the EKALAYAVA strategy when applied to NIFTY ITM rank 2 and 3 CE/PE contracts using completed 5‑minute candles for the week of 2026‑09‑07 to 2026‑09‑11.

## Experiment
1. Retrieve all completed 5‑minute candles for eligible contracts (ITM rank 2 and 3 CE/PE) for each trading day in the week 2026‑09‑07 to 2026‑09‑11. 2. Apply the LEVEL_TO_LEVEL strategy to each day's candles and record the daily profit or loss. 3. Apply the EKALAYAVA strategy to the same day's candles and record the daily profit or loss. 4. Compute the average daily profit for each strategy over the five trading days. 5. Perform a paired t‑test (or non‑parametric equivalent if assumptions fail) to determine if the mean difference in daily profits is statistically significant at the 5% level.

## Result
- Valid setups: 25
- Target hits: 16
- Stop-loss hits: 9
- Average points: 7.040000000000003
- Strategies: {'EKALAYAVA': 16, 'LEVEL_TO_LEVEL': 15}
- Option types: {'CE': 20, 'PE': 11}
- ITM ranks: {'2': 15, '3': 16}

## Groq Interpretation
- Decision: NEED_MORE_DATA
- Supported evidence: []
- Contradictory evidence: []
- Limitations: ['No per‑strategy profit or average daily profit figures are provided; only aggregate metrics are available.', 'Missing 5‑minute candles for several option contracts (e.g., 24250‑PE missing 125 intervals, 24400‑PE missing 34 intervals) limit the completeness of the dataset.', 'Only a single week of data (2026‑09‑07 to 2026‑09‑11) is available, which is insufficient for a statistically robust comparison.', 'The "by_strategy" field lists the number of setups per strategy but does not provide corresponding profit or loss statistics.']
- Next question: Could you provide the average daily profit (or total points) separately for the LEVEL_TO_LEVEL and EKALAYAVA strategies, and confirm whether the missing option candles can be interpolated or if additional complete weeks of data are available?
