# Ekalayava Final Stop-Loss and Target Decision

## Decision

**No experimental stop-loss/target policy is approved.** Keep the canonical
Ekalayava entry rules unchanged and leave its canonical exit lifecycle
unresolved. Do not wire any candidate into the paper engine or use this
research as trading authorization.

The validation screen provisionally selected `C_B2_2R_V1`, but its chronological
record is unstable: training was negative, validation and the 2025 test were
positive, and the recovered Jan–September 2026 ledger was negative. All 253
saved 2026 exact-contract paths are now available, but fees, spread, slippage
and executable fills remain unknown, and the comparisons are retrospective.

## Candidate outcomes that determine the decision

All results below are gross option-premium points per equal-unit event, before
fees, spread, slippage, taxes, sizing, or capital constraints.

| Candidate | Train: Jul–Aug 2025 | Validation: Sep–Oct 2025 | Test: Nov–Dec 2025 | 2026 Jan–Sep (target / stop / EOD; gross) |
|---|---:|---:|---:|---:|
| `A_B4_TP25_V1` | +50.90; PF 1.072 | −321.85; PF 0.669 | +148.20; PF 1.211 (34 target / 35 stop) | 107 / 136 / 10; −1353.30 |
| `A_B4_OPENING_HIGH_V1` | −120.90; PF 0.857 | −141.60; PF 0.851 | +167.25; PF 1.251 (30 / 35; 4 EOD) | 91 / 141 / 21; +780.80 |
| `B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1` | +217.65; PF 1.528 | −19.85; PF 0.960 | +1.25; PF 1.003 (22 / 47) | 57 / 193 / 3; +79.05 |
| `C_B2_1R_V1` | −303.65; PF 0.670 | −276.25; PF 0.693 | +76.95; PF 1.113 (34 / 31; 4 EOD) | 107 / 139 / 7; −1237.90 |
| `C_B2_1_5R_V1` | −274.30; PF 0.732 | −9.05; PF 0.990 | +118.22; PF 1.154 (26 / 37; 6 EOD) | 85 / 155 / 13; −1124.77 |
| `C_B2_2R_V1` | −258.20; PF 0.764 | +75.85; PF 1.079 | +172.70; PF 1.207 (21 / 40; 8 EOD) | 68 / 164 / 21; −1141.85 |
| `A_STRUCTURAL_TROUGH_B4_TP25` (archived fraction) | +26.09; PF 1.063 | −185.96; PF 0.698 | −7.36; PF 0.980 (45 / 24) | 157 / 93 / 3; −272.90 |

The 2025 test period for the validation-selected 2R candidate had 69 eligible and
resolved simulated entries: 21 targets, 40 stops, and 8 experimental
end-of-session exits; maximum drawdown was 221.25 points and the longest
losing streak was 10. Positive 2025 test gross points do not establish stable
or net profitability: training was negative, validation drawdown was 306.70
points, and all 253 recovered 2026 paths lost 1141.85 points for this 2R
candidate. Guide 8 subsequently replayed the other fixed candidates once on
the same test period for count completeness; those comparisons are
retrospective and were not used to tune a replacement.

The combined 2025 H2 plus saved 2026 entry ledger contains 447 observations
per candidate. All 447 entries now have a replay classification; 2025 still
has 192 complete and 2 partial entry paths, while the 2026 ledger has 253/253
complete paths and no missing exact paths. The 2R candidate produced 127
target exits, 282 stop exits and 38 experimental end-of-session exits, for
−1151.50 gross points. Candidate-by-candidate outcome counts,
touch-versus-exit reconciliation, and period results are in
[EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md](./EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md).

`A_B4_OPENING_HIGH_V1` is now the descriptive combined-gross leader at
+685.55 points (PF 1.105; maximum drawdown 602.05), driven by +780.80 in
recovered 2026 data despite negative training and validation. It is not
stable across periods or approved. B2, audited because it was the former
leader, returned +278.10 gross points across the full 447 entries (PF 1.067;
maximum drawdown 660.90), with +217.65 training, −19.85 validation, +1.25
test and +79.05 in 2026. Its 2026 monthly/segment profile was +143.55
Jan–June, +19.40 July–August, and −83.90 in September. Neither candidate
demonstrates a repeatable, cost-adjusted edge.

The separate B2 exact-path audit rerun matched all 447 ledger rows against the
existing simulator. Its mean/median maximum favorable excursion were
+20.35/+12.05 points and adverse excursion
−14.77/−11.50; 78 of 331 stopped trades later touched Opening High, but those
are not wins. The top five winners contributed 15.5% of positive points.
Uniform round-trip cost of 0.622 premium points per trade erases its combined
gross result; hypothetical 0.50-point costs leave only +54.60 points and
1.00-point costs produce −168.90. These are sensitivity cases, not measured
fees or rupee returns. Details are in
[EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md](./EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md).

## Rule formulas tested (research-only)

Let `E` be the actual entry close, `L` the causal recovery-structure trough
observed by entry, `H` the first completed five-minute candle's opening-range
high, and `b` the buffer:

* `A_B4_TP25_V1`: initial stop `L - 4`; fixed target `E + 25` premium points.
  This is **not** the archived policy called `TP25`.
* `A_B4_OPENING_HIGH_V1`: initial stop `L - 4`; target `H`.
* `B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1`: initial stop `L - 2`; target `H`;
  experimental trailing proxy lowers the stop to the lower of the prior two
  completed candle lows minus 2 points, effective from the next candle. This
  is not a strict, right-side-confirmed pivot trail.
* `C_B2_1R_V1`, `C_B2_1_5R_V1`, `C_B2_2R_V1`: initial stop `L - 2`; initial
  risk `R = E - (L - 2)`; target respectively `E + R`, `E + 1.5R`, or `E + 2R`.

The archived policy `A_STRUCTURAL_TROUGH_B4_TP25` instead uses target
`E + 0.25 * (H - E)`. It was replayed separately from the new fixed `+25`
candidate. All tested policies are research candidates only; none has been
approved as the final rule.

## Assumptions and limitations

* Entry logic is unchanged and uses completed five-minute candles and only
  causal information. Exact formulas and simulator sequencing are documented
  in [EKALAYAVA_FINAL_RULE_SPEC.md](./EKALAYAVA_FINAL_RULE_SPEC.md).
* Exit monitoring starts after the entry candle. Stop gaps fill at the bar
  open, target gaps at the target; same-bar stop/target collisions are
  ambiguous; missing intervals remain unresolved. End-of-session close is an
  experimental simulator convention, not a canonical strategy rule. No
  partial exits are modeled.
* The 2025 candidate comparison uses the same 194 detected entries. There are
  192 complete and 2 partial entry paths; the 2026 saved ledger now has 253
  exact complete paths out of 253 observations after bounded recovery.
* A target touch is not a realized win. In the exact 2026 archived replay, 5
  later opening-high touches occurred after a simulated exit.
* Fees, taxes, spreads, slippage, executable fill quality, sizing and rupee
  P&L were not available. The 2025 holdout's gross 2R result averages 2.50
  points per trade; an all-in cost above that per event would erase its gross
  mean. This break-even arithmetic is not a cost estimate or net result.
* The validation screen was a limited predeclared filter (at least 25 complete
  paths, positive gross points, and profit factor above 1). Passing it was
  provisional, not a robustness or deployment criterion. No candidate is
  recommended despite the 2R test-period gross result.
* The Nov–Dec period was originally evaluated only for the frozen validation
  choice. Guide 8 later accounted each pre-existing candidate on that period
  once to satisfy the all-candidate count requirement. This is retrospective
  descriptive analysis, not an untouched comparison for future selection.

## Approval status

**Research decision: no policy approved.** No production/paper-engine exit
implementation was added. Any future candidate requires more exact-contract
historical coverage, realistic cost inputs, a frozen evaluation protocol, and
supervised paper observation. Live trading remains disabled.
