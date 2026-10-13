# Ekalayava Guide 9 — Final Research Execution Summary

## Decision

**No stop-loss/target policy is approved for the paper engine.** The canonical
entry remains unchanged and the canonical exit lifecycle remains unresolved.
All reported P&L is gross option-premium points, not net returns or rupee P&L.

The highest descriptive combined-gross candidate after data recovery is
`A_B4_OPENING_HIGH_V1` at +685.55 points (164 target exits, 243 stops, 40
experimental end-of-session exits; PF 1.105, maximum drawdown 602.05). Its
training and validation periods lost −120.90 and −141.60 points, respectively,
so the positive aggregate, driven by recovered 2026 paths, is not stable
evidence and does not justify selection.

Guide 9 audited B2 because it was the previous gross leader:
`B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1` produced 112 targets, 331 stops, 4
experimental end-of-session exits and +278.10 gross points over 447 rows.
Its split was +217.65 training, −19.85 validation, +1.25 2025 test and +79.05
in 2026. A separate exact-path audit rerun matched 447/447 ledger outcomes,
points and exit timestamps. The B2 audit, path diagnostics and hypothetical
cost sensitivity are in
[EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md](./EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md).

## Data and reproducibility

* A bounded, read-only recovery requested the 246 exact symbol/date sessions
  missing from the saved 2026 entry ledger. All 246 requests returned data;
  none was empty, retried or substituted. No order API was used.
* 2025 H2: 194 canonical entries, 192 complete and 2 partial exact paths.
* Saved 2026 ledger: 253/253 complete exact-contract paths after recovery;
  these candle recoveries do not independently revalidate each historical
  entry decision.
* Every fixed candidate was reconciled over the 447-entry ledger. All
  eligible-entry and simulated-outcome reconciliation deltas are zero.
  Later target touches after an exit remain diagnostic, never wins.
* See [EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md](./EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md)
  and [EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md](./EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md)
  for path classifications, candidate totals and period tables.

## Economics, validation and blockers

No reliable historical brokerage, tax, bid/ask spread, slippage, executable
fill or account-sizing inputs were available. For B2, a uniform hypothetical
round-trip cost of 0.622 premium points per resolved trade erases its combined
gross result; scenarios of 0.50 and 1.00 points leave +54.60 and −168.90
points. These are sensitivities, not estimates of actual costs. The 2025 test
and candidate comparisons have already been examined and are retrospective.
No new stop/target variant is justified by this evidence.

The concrete next evidence is a consecutive, predeclared supervised paper
observation of at least 100 qualifying signals over at least 60 trading
sessions, whichever takes longer, with exact contract identity, five-minute
paths, quote/fill evidence, explicit costs and all incomplete/ambiguous cases
retained. This observation does not activate a candidate exit. See
[EKALAYAVA_PAPER_TRADING_READINESS.md](./EKALAYAVA_PAPER_TRADING_READINESS.md).

## Safety and verification

`EXECUTION_ALLOWED=False`; `PAPER_ONLY=True`. No live, paper or broker orders
were submitted, modified or cancelled. No candidate was wired into the paper
engine.

Commands run:

```sh
.venv/bin/python -m tools.run_ekalayava_guide8_reconciliation
.venv/bin/python -m tools.run_ekalayava_guide9_audit
.venv/bin/python -m pytest -q \
  tests/test_ekalayava_guide9_audit.py \
  tests/test_ekalayava_guide9_recovery.py \
  tests/test_ekalayava_guide8_reconciliation.py \
  tests/test_research_ekalayava_exits.py
.venv/bin/python -m pytest -q
.venv/bin/python -m py_compile \
  tools/run_ekalayava_guide8_reconciliation.py \
  tools/run_ekalayava_guide9_audit.py \
  tools/recover_ekalayava_guide9_paths.py \
  tests/test_ekalayava_guide9_audit.py \
  tests/test_ekalayava_guide9_recovery.py
git diff --check
```

The focused regression selection passed **17 tests**; the full repository suite
passed **129 tests**. The exact replay generators reported 253/253 recovered
2026 paths, 447/447 B2 audit matches, and zero candidate reconciliation
deltas. Python compilation and `git diff --check` passed. No test failures
remain.
