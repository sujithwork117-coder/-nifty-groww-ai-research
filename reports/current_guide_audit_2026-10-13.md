# Current Guide Audit — 2026-10-13

## Summary

The saved Jan–Sep 2026 trade ledgers reconcile with the corrected research
summary. One observer health-reporting defect was fixed: an internal option
candle gap now marks the observer degraded while the affected contract remains
fail-closed. Strategy rules and execution settings were not changed.

No full historical optimization was rerun and no market data was downloaded.
The requested window ends Sep 30, but source data ends Sep 29.

## Research verification

The canonical entries were checked against
[`strategies.py`](../app/strategies.py) and the stateful engine in
[`paper_engine.py`](../app/paper_engine.py):

- L2L uses the first completed candle for opening levels, a subsequent red
  candle breaking Opening Low, then the first later completed green candle
  within 09:15–11:00 IST. Entry is at its close; stop remains Opening Low −4
  points and target remains Opening High.
- Ekalayava uses a completed Opening Low break, a causal left=2/right=0 swing
  high, and a later completed breakout below Opening High. No future candle
  defines the entry or structural-low candidate. Its canonical stop and full
  exit lifecycle remain undefined; target touches are observations, not wins
  or realized P&L.

Trade-level reconciliation:

| Strategy | CSV ledger | Reconciled result |
|---|---|---|
| L2L | [`multi_year_l2l_entry_quality.csv`](multi_year_l2l_entry_quality.csv) | 361 setups: 57 targets, 145 SL, 1 ambiguous, 157 stop-breached skips, 1 target-already-reached skip; 202 resolved trades sum to **+237.45 points**. Mean/median resolved MFE, MAE and holding time also match `L2L_FINAL_VALIDATION.json`. |
| Ekalayava | [`multi_year_ekalayava_observations.csv`](multi_year_ekalayava_observations.csv) | 253 entries: 109 target touches, 144 no-touch paths; all 253 lifecycle outcomes unresolved and none has realized P&L. Mean/median MFE is +57.345/+31.05; MAE is −53.275/−45.60. |

The source L2L ledger labels 58 events `TARGET`; the corrected ledger
reclassifies the Jan 1 PE ITM2 entry (129.10, already above the 126.50 target)
as `SKIPPED_TARGET_ALREADY_REACHED`. Excluding its invalid −2.60 recorded
points gives the corrected 57 targets and +237.45-point total. This matches
the corrected JSON and summary CSV; it is not a new calculation.

L2L same-candle stop/target collisions are marked ambiguous; no forced
end-of-session close is applied. A remaining fill-model limitation is that
canonical L2L code checks OHLC barrier touches but does not use the bar open to
model a gap through a stop or to disambiguate a gap through a target. The
committed trade ledger does not include exit-bar OHLC, so affected trade count
and corrected points cannot be established from it. No fill behavior was
changed without an approved specification. The separate experimental
Ekalayava exit simulator handles stop gaps at the bar open and activates a
causal trailing update only after the completed bar; its tests pass. Those
experimental policies remain separate from canonical Ekalayava.

## Paper observer

**Status: component checks pass; operational readiness is not certified.**

- Exact daily CE/PE ITM2/ITM3 selection, expiry roll, missing-rank handling,
  and no-substitution behavior are covered by tests.
- Only completed five-minute candles are processed; IST conversion and session
  boundaries are enforced. The exchange calendar currently supports 2026 only.
- Persisted engine state and stable journal IDs suppress duplicate events after
  sequential restart/replay. Mocked provider tests cover reconnect/re-auth and
  failed, stale, and malformed streams.
- Gaps disable entries for the affected contract. The fix now also marks the
  observer `DEGRADED_OPTION_DATA`, ensuring the supervisor sees the problem and
  can reconnect.
- Signals and simulated outcomes are separately journaled. Canonical
  Ekalayava remains unresolved by default; no order API exists in the app.

No live Groww read-only connectivity/reconnect session was run, so provider
behavior and deployment readiness remain unverified. Runtime safety flags
were checked: `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`.

## Fix and validation

Confirmed fix: option streams with an internal candle gap now appear in the
observer's skipped/degraded status, in addition to journaling the gap and
disabling entries for that contract.

Command run:

```text
/home/codespace/.python/current/bin/python -m pytest -q tests/test_paper_observer.py tests/test_live_listener.py tests/test_journal.py tests/test_paper_engine.py tests/test_ekalayava_backtest.py tests/test_research_ekalayava_exits.py tests/test_research_target_policies.py tests/test_contract_selection.py tests/test_nse_calendar.py tests/test_read_only_verification.py tests/test_safety.py tests/test_safety_audit.py
```

Result: **53 passed, 0 failed**.

## Files changed

- [`app/paper_observer.py`](../app/paper_observer.py)
- [`tests/test_paper_observer.py`](../tests/test_paper_observer.py)
- [`reports/current_guide_audit_2026-10-13.md`](current_guide_audit_2026-10-13.md)

## Safest next step

Keep execution disabled. Before relying on paper P&L, approve and document
gap-through fill semantics, then validate them against exit-bar OHLC. Before
operational observation, perform a supervised read-only Groww integration
check and maintain the calendar for any dates beyond 2026.
