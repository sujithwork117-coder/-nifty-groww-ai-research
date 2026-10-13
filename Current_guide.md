NEXT TASK — VERIFY RESEARCH AND PREPARE SAFE PAPER-ONLY VALIDATION

Work in my existing nifty-groww-ai-research repository.

Do not rerun the full historical optimisation, chase unavailable 2025 data, or expand parameter grids.

1. Audit the research outputs

* Verify that reported metrics reconcile with the actual trade-level CSVs.
* Check L2L and Ekalavaya entry signals against their canonical definitions.
* Audit target fills, stop fills, same-candle ambiguity, gaps and end-of-session exits.
* Investigate the Ekalavaya trailing-stop rule and verify that its price-action logic is causal.
* Check that no future candles are used to determine entries, swing points or stops.
* Run relevant tests and report exactly which passed and failed.
* Fix confirmed defects and rerun only affected calculations.

2. Preserve canonical strategy rules

* L2L remains at its canonical entry, Opening Low −4 stop and Opening High target.
* Do not promote any experimental target or stop-loss.
* Ekalavaya’s experimental exit policies remain separate from its canonical definition.
* Do not change production behaviour without a separately documented and approved specification.

3. Verify paper-only observer readiness

Inspect the existing observer and its tests. Verify:

* Exact daily option contract selection for CE/PE ITM2/ITM3.
* Completed 5-minute candle processing.
* Correct market-hours and timezone handling.
* No duplicate signals or entries after reconnection/restart.
* Safe recovery from missing data and API disconnections.
* Persistent signal and paper-trade journaling.
* Clear separation between observed signals and simulated exits.

Do not place live orders or enable execution. Keep EXECUTION_ALLOWED=false and PAPER_ONLY=true.

If the observer is not ready, fix the specific defects where feasible. Do not claim readiness based on tests that were not run.

4. Deliver

Produce a concise audit report containing:

* Confirmed defects and fixes.
* Research metrics verified or corrected.
* Test commands and actual results.
* Observer readiness and remaining blockers.
* Exact files changed.
* The safest next step.

Do not perform unrelated refactoring, repeat the full optimisation or download unavailable data. Start with the audit.
