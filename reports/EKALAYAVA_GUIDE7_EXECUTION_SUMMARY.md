# Guide 7 Execution Summary

> **Historical snapshot:** This report predates Guide 9's bounded 2026
> exact-path recovery. Its 7/253 coverage and resulting candidate conclusions
> are superseded by
> [EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md](./EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md),
> [EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md](./EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md),
> and [EKALAYAVA_FINAL_SL_TARGET_DECISION.md](./EKALAYAVA_FINAL_SL_TARGET_DECISION.md).
> The Guide 7 execution and test record below remains historical.

## Result

Guide 7's bounded Groww retrieval and offline replay completed; Guide 8 added
the per-policy target/stop and touch reconciliation. Decision:
**no stop-loss/target policy approved**. `C_B2_2R_V1` passed the limited
validation screen. It was evaluated first on the Nov–Dec 2025 test; Guide 8
later made a one-pass descriptive accounting replay for all fixed candidates
there, without changing the validation selection. Its training result and
seven exact 2026 paths contradict a stable winner. No experimental policy was
wired into the paper engine.

## Files and outputs

* Retrieval tool: `tools/fetch_ekalayava_2025_h2.py`; the bounded H2 2025
  download completed and remains in ignored `data/derived/ekalayava_2025_h2_groww/`.
* Replay and reports: `tools/run_ekalayava_guide7_research.py`,
  `reports/ekalayava_guide7_*.csv`, and
  `reports/ekalayava_guide7_research_summary.json`.
* Decision documents:
  `reports/EKALAYAVA_FINAL_SL_TARGET_DECISION.md`,
  `reports/EKALAYAVA_HISTORICAL_DATA_COVERAGE_JUL_DEC_2025.md`,
  `reports/EKALAYAVA_MULTI_PERIOD_EXIT_VALIDATION.md`, and
  `reports/EKALAYAVA_FINAL_RULE_SPEC.md`.
* Automated focused coverage:
  `tests/test_ekalayava_guide7_research.py` and
  `tests/test_ekalayava_guide8_reconciliation.py`.
* Guide 8 outcome accounting:
  `tools/run_ekalayava_guide8_reconciliation.py`,
  `reports/EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md`, and
  `reports/ekalayava_guide8_*.csv`.

## Validation

Reproduce the offline reports after the ignored retrieval manifest and candles
are present:

```sh
.venv/bin/python -m tools.run_ekalayava_guide7_research
```

Guide 7 tests run:

```sh
.venv/bin/python -m pytest -q \
  tests/test_ekalayava_guide7_research.py \
  tests/test_research_ekalayava_exits.py \
  tests/test_contract_selection.py \
  tests/test_groww_data.py \
  tests/test_safety.py
```

Guide 7 focused result: **23 passed**; full repository result at that stage:
**119 passed**. Guide 8 adds a focused count/touch suite; see
`reports/EKALAYAVA_GUIDE8_EXECUTION_SUMMARY.md` for final combined test results.
Python syntax compilation passed for both research runners and their tests.

## Remaining limitations and safety

* 2025 entry paths: 192 complete, 2 partial out of 194 detected; selected
  contract-session paths: 488 complete, 4 partial out of 492.
* 2026 exact paths: 7 complete out of 253 saved entries; 246 have no usable
  exact path. Archived replay produced 21/21 exact outcome/points/exit-time
  matches across three policies, but only on those seven paths.
* Fees, taxes, spread, slippage, and rupee sizing are unavailable; all
  results are gross premium points.
* Live execution is disabled (`EXECUTION_ALLOWED=False`), paper-only mode is
  true, and no broker orders were submitted. No production lifecycle was
  enabled.
