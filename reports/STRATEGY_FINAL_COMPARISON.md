# Strategy Final Comparison — Jan–Sep 2026

**Source:** corrected Jan–Sep baseline plus existing candle-level artifacts. This is a descriptive comparison, not a strategy ranking or profitability claim. No market data was downloaded. L2L includes one narrowly scoped correction for entry already at/above target; Ekalayava official lifecycle results remain undefined by its canonical specification.

## Overall counts

| Measure | L2L (corrected canonical) | Ekalayava (canonical observation) | Ekalayava structural-trough candidate, buffer 0* |
|---|---:|---:|---:|
| Setups / entries | 361 | 253 | 253 |
| Target touches/outcomes | 57 | 109 observed touches | 87 hypothetical target exits |
| SL | 145 | Undefined | 151 hypothetical SL exits |
| Resolved target/SL | 202 | 0 lifecycle-resolved | 238 |
| Skipped / unresolved | 158 skipped; 1 ambiguous | 253 unresolved lifecycle (144 had no target touch) | 15 unresolved; 0 ambiguous |
| Target fraction among target/SL resolved | 28.2% | Not a canonical win rate | 36.6% |
| Gross / resolved-only mean points | +237.45 gross; +1.18 mean | Not defined | +2.63 mean among resolved only |
| Average winner / loser | +29.25 / −9.86 | Not defined | +48.26 / −23.65 |
| Median holding interval | 10 min by stored bar timestamps | Not defined | 32.5–37.5 min (OHLC interval) |
| Max drawdown | 250.05 equal-unit resolved sequence | Not defined | 449.20 equal-unit resolved sequence |

*The hypothetical Ekalayava model is research-only and not the canonical strategy. It uses a causal pre-entry reversal-sequence trough, no buffer, later 5-minute candle stop/target touches, and same-candle ambiguity. Unresolved cases are excluded from its resolved-only mean. None of these figures establish profitability.

## Timing, excursions, and observed subgroup context

| Behavior | L2L | Ekalayava |
|---|---|---|
| Target timing | 57 valid target events; median interval 10–15 min; 56/57 within 90 min, one at 110–115 min | 109 target touches; median 60–65 min; 44/109 after 90 min |
| Fast target events | 13/57 in first 0–5 min; 24/57 within 10 min | 13/109 in 0–5 min, 21/109 within 15 min |
| Mean MFE / MAE | +18.22 / −12.82 among target/SL-resolved events | +57.35 / −53.27 over all observed entry paths; still observational |
| CE / PE target behavior | CE 26/104 resolved (25.0%); PE 31/98 (31.6%) | CE 55/126 touches (43.7%); PE 54/127 (42.5%) |
| ITM2 / ITM3 target behavior | ITM2 26/101 resolved (25.7%); ITM3 31/101 (30.7%) | ITM2 53/128 touches (41.4%); ITM3 56/125 (44.8%) |

L2L target outcomes appear sooner in the observed sample, but neither target-touch rates nor conditional resolved point totals should be compared as equivalent measures: Ekalayava has no canonical stop or resolved lifecycle. CE/PE, ITM2/ITM3, and entry-time differences are descriptive and subject to missing contracts.

## Monthly distributions

| Month | L2L target / SL; gross points | Ekalayava entries / target touches | Ekalayava hypothetical b0 target / SL / unresolved |
|---|---:|---:|---:|
| Jan | 10 / 21; +49.95 | 35 / 20 | 17 / 18 / 0 |
| Feb | 6 / 9; +41.60 | 38 / 14 | 13 / 24 / 1 |
| Mar | 2 / 14; −92.35 | 21 / 8 | 8 / 11 / 2 |
| Apr | 4 / 15; −65.65 | 27 / 5 | 3 / 20 / 4 |
| May | 14 / 14; +298.00 | 34 / 19 | 12 / 19 / 3 |
| Jun | 5 / 33; −96.70 | 36 / 17 | 14 / 22 / 0 |
| Jul | 3 / 22; −64.70 | 21 / 11 | 9 / 10 / 2 |
| Aug | 9 / 7; +146.10 | 26 / 11 | 9 / 14 / 3 |
| Sep* | 4 / 10; +21.20 | 15 / 4 | 2 / 13 / 0 |

*September data ends Sep 29. L2L’s combined points are concentrated: May alone contributes +298.00, while other months net to −60.55. The Ekalayava touch counts and hypothetical outcomes vary across months; neither series establishes a stable regime-independent outcome.

## Structural-stop comparison for Ekalayava

The primary research candidate is the lowest premium low from the first Opening-Low-break candle through the completed candle before entry. It is available below entry in all 253 rows; median entry distance is 22.95 points and it was revisited in 187/253 observed paths. A 0/2/4-point buffer sensitivity changed hypothetical counts from 87/151/15 to 89/146/18 to 91/142/20 (target/SL/unresolved). The target fraction rises conditionally while losses widen and unresolved counts increase. No precise buffer is justified; the setting is unset in code by default.

The canonical Ekalayava entry and Opening High target remain unchanged. The engine can run this stop/target convention only when an operator explicitly sets `EKALAYAVA_SL_BUFFER_POINTS`; its default continues to record observation-only signals. Until the candidate is approved/versioned, Ekalayava has no valid P&L comparison with L2L.

## Data quality and interpretation limits

There were 185 expected sessions; 184 have underlying data (13,783/13,875 bars). Option data covers 42,149/55,500 expected 5-minute bars (75.9%) across 740 contract-days: 561 complete, 1 partial, and 178 missing/unselectable. There are 112 fully usable, 55 partially usable, and 18 unusable days. Missing exact contracts can suppress signals and bias all subgroup and monthly frequencies. Each of the 253 exact Ekalayava event contract-days has a complete 75-bar session, but the missing option universe can still hide other entries.

L2L gross points exclude position sizing, fees, spread, slippage, and capital. Ekalayava candidate simulation uses hypothetical OHLC fills, no intrabar ordering, and excludes unresolved paths from the resolved-only mean. Neither is rupee/account P&L. Do not infer a 90-minute holding rule from either target-time distribution.

## Readiness

- **L2L: NOT READY for live paper observation.** The stateful engine is present, but the full Groww observer coordinator, exchange holiday/special-session calendar, stream orchestration, and real reconnect integration remain incomplete.
- **Ekalayava: READY FOR OBSERVATION ONLY.** Canonical default has no approved executable stop buffer; structural stop results remain hypotheses.
- Both remain paper-only: `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`; no live order path was activated.

Evidence: [`l2l_final_validation.md`](l2l_final_validation.md), [`EKALAYAVA_FINAL_RESEARCH.md`](EKALAYAVA_FINAL_RESEARCH.md), and [`paper_trading_readiness.md`](paper_trading_readiness.md).
