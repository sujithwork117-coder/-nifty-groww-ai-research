# Target-Hit Analysis — L2L and Ekalayava

**As of:** 2026-10-13
**Scope:** Reconcile existing saved ledgers only. No optimization grid was rerun. No policy was adopted as canonical.

## Executive conclusions

| Strategy / reference | Target touches | Simulated target exits | Exit rate and denominator | Gross points | Interpretation |
|---|---:|---:|---|---:|---|
| L2L canonical Opening High / Opening Low −4 | 58 | 57 | 57/203 = 28.08% | +237.45 | 1 ambiguous touch; 158 of 361 setup records were skipped, not entries. |
| L2L most target exits: `SL_6_TP_25` | 132 | **116** | 116/236 = 49.15% | +218.69 | +59 exits and +21.07 percentage points versus baseline, but gross fell by 18.76 points. Sixteen touches were ambiguous rather than confirmed exits. |
| L2L highest exit rate: `SL_4_TP_25` | 118 | 105 | 105/203 = 51.72% | +205.67 | +23.64 percentage points versus baseline; 13 touches were ambiguous. This is not the most-exit-count policy. |
| Ekalayava canonical Opening High observation | **109** | **NOT AVAILABLE** | 109/253 = 43.08% touch rate only | NOT AVAILABLE | All 253 canonical entries have no approved exit lifecycle; touches are not wins or P&L. |
| Ekalayava most target exits / highest exit rate: `A_STRUCTURAL_TROUGH_B4_TP25` | 189 | **157** | 157/253 = 62.06% | −272.90 | Experimental only. 32 observed touches did not become that policy’s target exit. The canonical baseline has no comparable exit count or P&L. |

No target-count increase establishes profitability, fill quality, or robustness. The L2L high-count candidate’s full-period gross was lower than the canonical baseline. The Ekalayava high-count candidate lost gross points, and no canonical Ekalayava exit comparison exists.

## Source files and policy definitions

The calculations use the corrected baseline and saved policy trade ledgers:

- [`multi_year_baseline_metrics.csv`](./multi_year_baseline_metrics.csv)
- [`multi_year_l2l_target_policy_trades.csv`](./multi_year_l2l_target_policy_trades.csv)
- [`multi_year_l2l_stop_policy_trades.csv`](./multi_year_l2l_stop_policy_trades.csv)
- [`multi_year_l2l_combined_sl_tp_trades.csv`](./multi_year_l2l_combined_sl_tp_trades.csv)
- [`multi_year_ekalayava_observations.csv`](./multi_year_ekalayava_observations.csv)
- [`ekalayava_exit_policy_trades.csv`](./ekalayava_exit_policy_trades.csv)
- [`ekalayava_exit_policy_summary.csv`](./ekalayava_exit_policy_summary.csv)

The combined L2L file contains 12 distinct stop/target combinations, each with 361 setup rows. It was used as the one-row-per-policy/setup source; the target-only and stop-only ledgers were not added again. The Ekalayava exit file contains 37 distinct policies: 36 anchor/buffer/target combinations and one separate trailing candidate.

Code confirms the L2L candidate target is `entry + fraction * (Opening High - entry)` and the candidate stop is `Opening Low - configured buffer` (`app/research_target_policies.py`, `target_for_fraction` and `simulate_exit_policy`). The canonical baseline is Opening High with the 4-point Opening-Low buffer. Ekalayava candidates use the policy’s fixed, entry-known target fraction and one of:

- **A:** saved causal structural trough minus buffer.
- **B:** completed breakout-candle low minus buffer.
- **C:** recovery-base invalidation aliases A in the saved implementation; it was not simulated as an additional policy.
- **D:** option Opening Low minus buffer.
- **Trailing:** a separate A-minus-2 initial stop, tightened only after a completed lower low against the preceding two completed bars; the new stop applies to the next candle.

The Ekalayava simulator fills a stop gap at the candle open, records targets at their target price, labels unresolved same-bar stop/target order as ambiguous unless the open establishes precedence, and fails closed on missing intervals. Its 15:25 close is an experimental end-of-session exit, not a canonical Ekalayava rule.

## Metric definitions and denominators

The three machine-readable outputs are:

- [`target_hit_policy_period_summary.csv`](./target_hit_policy_period_summary.csv)
- [`target_hit_baseline_comparison.csv`](./target_hit_baseline_comparison.csv)
- [`target_hit_data_quality_summary.csv`](./target_hit_data_quality_summary.csv)

The summary includes every saved policy, the overall period, training, validation, incomplete September, and CE/PE, ITM-rank, entry-time, and month segments where labels exist.

Definitions used in those files:

1. **Eligible setups** are rows in the saved signal/event ledger. This is not the full market opportunity universe; missing contracts may hide signals.
2. **Eligible entries** are policy-eligible entry records. For L2L this excludes its pre-entry skip outcomes. For Ekalayava this is the 253 canonical entry observations, including cases later excluded by a candidate stop geometry.
3. **Valid entries** exclude candidate-policy `EXCLUDED_*` and other pre-entry skip rows. Both valid and eligible denominators are supplied because they differ for some Ekalayava policies.
4. **Complete paths** are paths available for the metric being measured. L2L counts valid paths through a terminal outcome; Ekalayava target touches use the saved canonical MFE path, through an Opening-High touch or session end. For both strategies, the saved policy ledgers report 75 source bars per entry; the L2L policy CSVs do not retain per-candle timestamps for a separate cadence replay.
5. **L2L target touches** count one touch per `TARGET` or `AMBIGUOUS` policy outcome through that policy’s terminal candle. An ambiguous touch is not a confirmed target exit; later price movement after the position’s simulated terminal exit is not counted.
6. **Ekalayava target touches** are independently counted from canonical saved MFE: `MFE >= candidate target - entry`. This measures the target on the full saved observation horizon, even if an experimental stop would have exited earlier. For TP100, the reconstructed 109 touches exactly match the saved `target_touched` flag.
7. **Target exits** include only unambiguous `TARGET` outcomes. Ekalayava terminal end-of-session exits are reported separately.
8. **Target-hit rate** is simulated target exits divided by eligible entries. `target_exit_rate_valid` separately divides by policy-valid entries; `target_exit_rate_of_resolved` divides by resolved outcomes. Touch rates use complete paths. Every CSV row includes its numerator and denominator.
9. **Gross points** sum resolved simulated exit points only. Average points per policy-valid entry, eligible entry, and resolved trade are separate. No fees, spread, slippage, size, capital, or real-world fills are modeled.
10. **Drawdown** and **losing streak** are computed chronologically over resolved equal-unit gross points. Ambiguous, unresolved, and skipped records are not assigned synthetic P&L. Unavailable metrics remain blank, not zero.

## L2L results

The corrected canonical baseline is **361 setups: 203 policy-eligible entries, 57 target exits, 145 stop exits, 1 ambiguous touch, 0 unresolved, and 158 skips** (157 stop-already-breached and 1 target-already-reached). Gross was **+237.45 premium points**.

| Finding | Policy | Target exits / denominator | Rate | Touches | Stop / ambiguous / unresolved | Gross points | Max drawdown | Longest losing streak |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Canonical baseline | `SL_4_TP_100` | 57/203 | 28.08% | 58 | 145 / 1 / 0 | +237.45 | 250.05 | 23 |
| Most target exits | `SL_6_TP_25` | 116/236 | 49.15% | 132 | 104 / 16 / 0 | +218.69 | 161.13 | 8 |
| Highest target-exit rate | `SL_4_TP_25` | 105/203 | 51.72% | 118 | 85 / 13 / 0 | +205.67 | 132.93 | 7 |
| Best all-period gross among candidates | `SL_4_TP_50` | 79/203 | 38.92% | 81 | 122 / 2 / 0 | +254.65 | 250.43 | 17 |
| Best validation-period gross | `SL_6_TP_75` | 18/50 | 36.00% | 18 | 32 / 0 / 0 | +173.56 | 55.35 | 6 |

For the **most-exit-count** candidate, target exits increased by **59**, and its target-exit rate rose **21.07 percentage points** (116/236 versus 57/203). Gross deteriorated by **18.76 points**; drawdown decreased by 88.93 points and the longest losing streak shortened by 15. This candidate had 16 ambiguous same-candle touches; none were counted as confirmed exits.

For the **highest-rate** candidate, target exits increased by 48 and the rate rose **23.64 percentage points** (105/203 versus 57/203). Gross deteriorated by 31.78 points. Its 13 ambiguous touches are separated from the 105 confirmed exits.

The best validation gross policy, `SL_6_TP_75`, made **+173.56** in Jul–Aug versus the baseline’s **+81.40**, but its Jan–Jun training gross was **−169.14** and its all-period gross was **−25.55**. The largest target-exit-count candidate `SL_6_TP_25` did show more Jul–Aug exits (25/50, 50.00%) than baseline (12/41, 29.27%), a **+20.73 percentage-point** rate difference; its validation gross was lower (+26.61 versus +81.40). The highest-rate candidate `SL_4_TP_25` had 22/41 exits in validation (53.66%, +24.39 percentage points) but validation gross was only +34.85.

Thus the target-hit count/rate improvements appeared in the existing validation period, but did not consistently improve gross points. The policies were tested against the same finite saved period; this is not a fresh independent holdout. September is incomplete and not an untouched holdout.

## Ekalayava results

The canonical strategy has **253 observed entries, 109 Opening-High touches, 144 non-touches, and 253 unresolved canonical exit lifecycles**. The touch rate is 109/253 = **43.08%**. There is no canonical simulated target-exit count, stop count, gross P&L, drawdown, or losing streak; those are intentionally blank in the observation reference row.

| Finding | Policy | Touches / complete paths | Target exits / eligible entries | Stop / EOD / ambiguous / unresolved | Gross points | Max drawdown | Longest losing streak |
|---|---|---:|---:|---:|---:|---:|---:|
| Canonical Opening-High observation | `EKALAYAVA_CANONICAL_OPENING_HIGH_OBSERVATION_ONLY` | 109/253 | **Unavailable** | No canonical exit lifecycle | **Unavailable** | **Unavailable** | **Unavailable** |
| Highest touch count (tie: all nine TP25 anchor/buffer combinations) | e.g. `A_STRUCTURAL_TROUGH_B0_TP25` | 189/253 | 152/253 | 100 / 1 / 0 / 0 | −87.51 | 533.91 | 9 |
| Most target exits and highest exit rate | `A_STRUCTURAL_TROUGH_B4_TP25` | 189/253 | **157/253 = 62.06%** | 93 / 3 / 0 / 0 | **−272.90** | **732.09** | 9 |
| Highest all-period gross among experimental policies | `B_BREAKOUT_CANDLE_B2_TP100_OPENING_HIGH` | 109/253 | 65/253 | 182 / 6 / 0 / 0 | +1,145.70 | 306.30 | 25 |
| Best validation-period gross among experimental policies | `A_STRUCTURAL_TROUGH_B2_TP100_OPENING_HIGH` | 22/47 | 19/47 | 22 / 6 / 0 / 0 | +216.30 | 228.90 | 8 |

For the highest-exit candidate, **32/189 observed target touches did not qualify as that policy’s target exit**. Touches can occur after the experimental stop would have terminated the position; they are observations, not wins. Relative to the same A/B4 experimental stop with TP100, TP25 had 66 more target exits (157 vs 91) and 80 more touches (189 vs 109), but gross deteriorated by **1,053.70 points** (+780.80 to −272.90) and drawdown worsened by **130.94 points** (601.15 to 732.09). This comparison is experimental-to-experimental, not a canonical baseline comparison.

In validation, A/B4/TP25 recorded 29 target exits and 32 touches from 47 entries, but gross was **−72.25** and drawdown 249.84. A/B4/TP100 recorded 19 target exits, 22 touches, and +192.15 gross over those 47 entries. The increase in target exits did not preserve gross performance. The best validation gross policy, A/B2/TP100, recorded 19 exits, 22 touches, and +216.30; it is still an experimental, same-validation-set result.

No Ekalayava candidate can be said to improve target exits, gross points, or hit rate **versus a canonical exit baseline**, because none exists. The +80 touch comparison between a TP25 policy (189) and the canonical Opening-High reference (109) uses different target levels and is descriptive only.

## Data quality and period limits

The reports verify 4,332 L2L rows (12 policies × 361 setups) and 9,361 Ekalayava rows (37 policies × 253 entries), with no duplicate policy/setup identities. The 253 Ekalayava observations joined one-to-one to exit rows using date, timestamp, and exact option symbol. Each saved policy record reports 75 source bars. Outcomes are counted once per signal/policy; ambiguous and unresolved statuses remain distinct; the C/A alias is not double-counted.

The authoritative 2026-01-01 through 2026-09-30 inventory has 740 expected option contract-days: **561 complete, 1 partial, and 178 missing or unselectable**; 42,149/55,500 expected option bars (75.94%). Underlying data covers 13,783/13,875 bars through Sep 29; Sep 30 is absent and Sep 29 is missing 17 late bars. There is no local 2022–2025 five-minute dataset. These missing contracts can hide setups and unseen outcomes; the CSV counts describe saved event ledgers, not the full market opportunity set.

The segment summaries expose CE/PE, ITM2/ITM3, entry-time bucket, month, and the training/validation/incomplete-September periods. Small or missing segment samples are descriptive only; no significance test was performed.

## Decision

- Do **not** change canonical L2L rules or adopt an experimental TP from these counts.
- Do **not** give Ekalayava an exit/P&L rule from this grid. Keep all exits experimental.
- L2L TP25 deserves cautious additional **paper-only** evaluation because its exit-rate increase persisted in Jul–Aug; its gross results do not support adoption, and the max-exit candidate’s full-period gross fell.
- Ekalayava results do not justify a canonical exit. Any future exit test must remain explicitly experimental and be evaluated on new, untouched observations.
- The safest next step is a supervised, read-only observer validation in a market session after the execution lock and observer health are rechecked—not an order-enabled run.
