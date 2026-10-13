# Ekalayava Multi-Period Exit Validation

## Protocol

The canonical entry analyzer was held fixed. Six exit candidates were
evaluated over 2025 H2 using chronological periods defined before the final
replay: training July–August, validation September–October, and one untouched
November–December test. The validation screen required at least 25 complete
paths, positive gross points and profit factor above 1; it selected
`C_B2_2R_V1`. That candidate was then evaluated once on the untouched 2025
test. No test result was used to retune it.

The additional 2026 comparison uses only seven entries with complete exact
contract paths. These are a sparse later-date diagnostic, not a sufficiently
powered holdout. The 246 entries without paths are excluded from outcome
metrics and remain visible in coverage reports.

There is no canonical Ekalayava exit baseline to compare against: the
canonical lifecycle is unresolved. Thus the 2025 table compares fixed
experimental candidates under identical 2025 entry/path eligibility; it does
not claim improvement over a validated incumbent.

## 2025 training and validation results

All candidates have the same 61 training and 64 validation entries; among
validation entries, 62 paths are complete and 2 partial. Values are gross
premium points before all trading costs.

| Candidate | Stop / target family | Train gross | Train PF | Train max DD | Validation gross | Validation PF | Validation max DD |
|---|---|---:|---:|---:|---:|---:|---:|
| `A_B4_TP25_V1` | Trough −4 / fixed +25 points | +50.90 | 1.072 | 203.85 | −321.85 | 0.669 | 406.00 |
| `A_B4_OPENING_HIGH_V1` | Trough −4 / Opening High | −120.90 | 0.857 | 306.85 | −141.60 | 0.851 | 249.55 |
| `B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1` | Trough −2 / lower-low trailing proxy / Opening High | +217.65 | 1.528 | 150.00 | −19.85 | 0.960 | 190.70 |
| `C_B2_1R_V1` | Trough −2 / 1R | −303.65 | 0.670 | 374.10 | −276.25 | 0.693 | 412.90 |
| `C_B2_1_5R_V1` | Trough −2 / 1.5R | −274.30 | 0.732 | 361.17 | −9.05 | 0.990 | 333.42 |
| `C_B2_2R_V1` | Trough −2 / 2R | −258.20 | 0.764 | 325.90 | +75.85 | 1.079 | 306.70 |

Despite meeting the narrow validation screen, `C_B2_2R_V1` had a strong
train/validation sign reversal. The other candidates also show unstable
period-to-period outcomes; no robust 2025 winner was established.

## Frozen candidate's untouched 2025 test

| Eligible / complete paths | Target | Stop | End-of-session | Ambiguous | Unresolved | Gross points | Mean / median | Win rate | PF | Max DD | Longest losing streak |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 69 / 69 | 21 | 40 | 8 | 0 | 0 | +172.70 | +2.50 / −9.40 | 37.7% | 1.207 | 221.25 | 10 |

Mean initial risk was 23.05 points; mean realized reward/risk was 0.067; mean
MFE / MAE were +27.05 / −17.42 points; average holding time was 97.32
minutes. Eight end-of-session exits use the experimental last-candle-close
convention. A positive aggregate with a negative median, low win rate,
10-trade losing streak and adverse training result is not enough to approve
the policy.

## Later 2026 exact-path subset

For the validation-selected 2R candidate, the six complete Jul–Aug 2026
entries produced −49.40 gross points (2 targets, 4 stops; PF 0.654). The one
complete exact entry path from the wider incomplete September period lost
21.90 points at its stop. Combined over the seven exact paths: **−71.30 gross
points**. This small sample is descriptive, not statistically conclusive, but
it contradicts treating the 2025 holdout result as robust.

The full six-candidate 2026 exact-subset metric rows are in
`reports/ekalayava_guide7_research_summary.json`; entry-level results are in
`reports/ekalayava_guide7_2026_candidate_traces.csv`. Exact-path counts and
missing paths are in
`reports/ekalayava_guide7_2026_entry_path_coverage.csv`.

## Reproduction of archived policy outcomes and target touches

The archived 2026 ledger was independently replayed against exact candle
paths, matching **outcome, realized points, and exit timestamp** for each of
the seven eligible events under each policy:

| Archived policy | Exact paths | Exact reproductions |
|---|---:|---:|
| `A_STRUCTURAL_TROUGH_B4_TP25` (25% fraction of distance to Opening High) | 7 | 7 |
| `A_STRUCTURAL_TROUGH_B4_TP100_OPENING_HIGH` | 7 | 7 |
| `TRAIL_CAUSAL_LOWER_LOW_B2_TP100` | 7 | 7 |

This is only 21 successful event-policy replays, not verification of all 253
saved entries or archived aggregate statistics. The archived `TP25` fractional
target is explicitly different from candidate `A_B4_TP25_V1`'s fixed
25-premium-point target. The archived fractional policy's saved stop and
target were used to test replay sequencing; the replay does not independently
validate how the archived target was originally derived. Five later
Opening-High touches occurred after an already-simulated exit, demonstrating
why target-touch counts are not trade wins.

## Costs, sensitivity, and limits

No reliable historical brokerage, tax, spread or slippage inputs were
available, so net performance and a realistic cost/slippage sensitivity
cannot be calculated. The 2025 test gross mean for the frozen candidate was
2.50 points per event; this is merely its arithmetic break-even all-in cost
per event before gross points reach zero, not a measured cost or claimed net
return. No rupee or account-level return is reported.

Path lengths are evaluated with the existing fail-closed simulator. It begins
after the entry close, fills a stop gap at the candle open and a target gap at
the target, marks same-candle stop/target collisions ambiguous, and leaves
missing intervals unresolved. The end-of-session close is an experimental
convention. No partial profits are modeled. Candidate trail B is a lower-low
proxy, not a fully confirmed swing-pivot trailing policy.

## Conclusion

**No stop-loss/target policy is approved.** Preserve the canonical entry and
do not promote an experimental exit to the paper engine. Collect further
exact-contract paths under the existing supervised, paper-only safeguards;
pre-register any future evaluation and include measured transaction costs.
