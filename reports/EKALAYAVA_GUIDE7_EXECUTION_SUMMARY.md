# Guide 7 Execution Summary

## Result

Guide 7's bounded Groww retrieval and offline replay completed. Decision:
**no stop-loss/target policy approved**. `C_B2_2R_V1` passed the limited
validation screen and was evaluated once on the untouched Nov–Dec 2025 test;
its training result and seven exact 2026 paths contradict a stable winner.
No experimental policy was wired into the paper engine.

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
* Automated focused coverage: `tests/test_ekalayava_guide7_research.py`.

## Validation

Reproduce the offline reports after the ignored retrieval manifest and candles
are present:

```sh
.venv/bin/python -m tools.run_ekalayava_guide7_research
```

Tests run:

```sh
.venv/bin/python -m pytest -q \
  tests/test_ekalayava_guide7_research.py \
  tests/test_research_ekalayava_exits.py \
  tests/test_contract_selection.py \
  tests/test_groww_data.py \
  tests/test_safety.py
```

Focused result: **23 passed**. Full repository result: **119 passed**.
Python syntax compilation passed for the retriever, runner, and new tests.
Two ordinary report-run issues (monthly timestamp ordering and missing
test-entry timestamps) were fixed and the final replay completed. Pylance did
not recognize the new untracked runner as a workspace user file, so no
Pylance file diagnostic was available.

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
