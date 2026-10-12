# Ekalayava Final Research — Jan–Sep 2026

**Requested period:** 2026-01-01 through 2026-09-30. Source data ends Sep 29. This research uses the existing corrected baseline and exact selected option CSVs. No market data was downloaded and the entry strategy definition was not changed.

## 1. Canonical rule and implementation boundary

The canonical entry remains the existing completed 5-minute sequence: opening candle defines the range; option premium breaks below Opening Low; a causal recovery/swing structure develops; a later candle breaks and closes above the causal swing high while remaining below Opening High; entry is at that completed breakout candle close. The current implementation uses a causal left=2/right=0 swing-high convention. Opening High is the target/reference.

The canonical strategy document still does **not** define an executable structural stop, numeric buffer, opposite-signal exit, expiry convention, or forced end-of-day close. The empirical low and lifecycle model below are a research proposal, not a silent change to the canonical strategy. There is no official Ekalayava win rate or P&L until the owner versions/adopts a complete lifecycle.

## 2. Observed entries and target behavior

| Observation | Result |
|---|---:|
| Entries in corrected baseline | 253 |
| Opening High target touches | 109 (43.1%) |
| No target touch in same-day observed path | 144 (56.9%) |
| Canonical lifecycle-resolved outcomes | 0; all 253 remain unresolved |
| Mean / median target distance from entry | 61.10 / 54.80 points |
| Mean / median MFE, all entries | +57.35 / +31.05 points |
| Mean / median MAE, all entries | −53.27 / −45.60 points |
| Mean / median time to MFE | 113.99 / 85 min |
| Mean / median time to MAE | 179.05 / 195 min |
| Mean / median time to target touch, among 109 touches | 93.72 / 65 min |

“Target touch” is a high reaching Opening High in a later candle. It is not an exit, win, realized point result, or full-strategy P&L. The same-day target-touch sample has a long tail: **44/109** touches first appear after 90 minutes. OHLC gives the first touched candle window, not the exact intrabar instant.

| First target-touch window after entry | Touches |
|---|---:|
| 0–5 min | 13 |
| 5–10 min | 6 |
| 10–15 min | 2 |
| 15–30 min | 16 |
| 30–60 min | 17 |
| 60–90 min | 11 |
| >90 min | 44 |

These intervals are computed from the entry bar/touch bar timestamps; actual touch is bounded by the five-minute candle. The 60–65 minute median interval and 88.7–93.7 minute mean interval do not imply a 90-minute holding rule.

### Observational breakdowns

| Group | Entries | Target touches | Touch fraction | Mean MFE | Mean MAE |
|---|---:|---:|---:|---:|---:|
| CE | 126 | 55 | 43.7% | +52.63 | −52.88 |
| PE | 127 | 54 | 42.5% | +62.02 | −53.66 |
| ITM2 | 128 | 53 | 41.4% | +54.82 | −48.91 |
| ITM3 | 125 | 56 | 44.8% | +59.93 | −57.75 |
| Entry 09:15–09:59 | 62 | 38 | 61.3% | +45.78 | −75.17 |
| Entry 10:00–10:59 | 114 | 42 | 36.8% | +48.52 | −58.50 |
| Entry 11:00+ | 77 | 29 | 37.7% | +79.72 | −27.91 |

Rates are conditional on observed exact contracts; they are not win rates. The early bucket has smaller average target distance (24.17 points) alongside larger adverse excursion; later entries had wider target distances and lower mean MAE in this sample. These are descriptive associations only.

Monthly entries/touches: Jan 35/20, Feb 38/14, Mar 21/8, Apr 27/5, May 34/19, Jun 36/17, Jul 21/11, Aug 26/11, Sep 15/4. The first six months had 83/191 touches; Jul–Sep had 26/62, but September is incomplete (through Sep 29). The observed monthly touch fractions vary; no month-level pattern establishes a stable exit expectation.

## 3. Causal structural-anchor study

Candidate levels use only candles available at or before the completed entry. The primary proposed anchor is the minimum option premium low from the first Opening-Low-break candle through the completed candle immediately **before** the breakout entry candle. It is causal, exists below entry in all 253 rows, and has entry-to-anchor mean/median distance **28.23/22.95** points (interquartile range 14.75–34.95). Price later revisited that level in **187/253 (73.9%)** observed paths.

| Candidate anchor | Eligible below-entry paths | Median entry distance | Later revisit | Buffer-0 target / SL / unresolved* | Target share of resolved |
|---|---:|---:|---:|---:|---:|
| Reversal-sequence trough (primary candidate) | 253 | 22.95 | 187/253 (73.9%) | 87 / 151 / 15 | 36.6% |
| Last causal swing-low candidate | 223 | 20.75 | 168/223 (75.3%) | 75 / 137 / 11 | 35.4% |
| First breakdown candle low | 124 | 20.28 | 118/124 (95.2%) | 43 / 81 / 0 | 34.7% |
| Breakout candle low | 253 | 10.70 | 223/253 (88.1%) | 58 / 189 / 6 | 23.5% |

*Anchor candidates have different eligible populations. Same-bar stop/target collisions are reported ambiguous in the machine-readable results; no collisions occurred in these displayed buffer-0 aggregates. “Later revisit” means the level was touched after entry during the observed same-day path. Breakdown low is not below entry for 129/253 entries, so it is not a universal protective anchor. The breakout low is close to entry and was revisited frequently; its hypothetical results are included as a comparison, not as an endorsed structural definition.

## 4. Bounded hypothetical lifecycle: reversal trough with controlled buffer

The following is a counterfactual OHLC replay, **not a canonical backtest**. It starts after the completed entry candle. Target triggers when a later candle high is at/above Opening High. Stop triggers when a later candle low is at/below `pre-breakout reversal trough − buffer`. If target and stop are both touched in one bar the result is `AMBIGUOUS`; no intrabar ordering is invented. No forced session-end exit is applied; remaining paths are unresolved. The 5-minute exit bar’s full high/low contributes to MFE/MAE, so those excursions include within-bar movement after a hypothetical exit.

| Buffer | Entries | Target | SL | Ambiguous | Unresolved | Target / resolved | Avg / median target points | Avg / median SL points | Resolved-only mean | Max drawdown* | Longest SL streak |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 253 | 87 | 151 | 0 | 15 | 36.6% | +48.26 / +39.20 | −23.65 / −20.45 | +2.63 | 449.20 | 21 |
| 2 | 253 | 89 | 146 | 0 | 18 | 37.9% | +47.82 / +38.25 | −25.71 / −22.50 | +2.13 | 522.30 | 20 |
| 4 | 253 | 91 | 142 | 0 | 20 | 39.1% | +47.41 / +38.25 | −27.79 / −24.50 | +1.58 | 537.45 | 19 |

*Equal-unit cumulative premium points across resolved events, ordered by exit time then symbol. This is not account drawdown. “Resolved-only mean” omits unresolved cases and costs; it is not full-strategy expectancy or a profitability claim. No position sizing, transaction costs, spreads, slippage, or capital is modeled. 22, 20, and 18 stops respectively were followed later that day by an Opening-High touch; those later moves do not undo the earlier hypothetical stop.

Across the three buffers, increasing the buffer changes trade classification, widens average losses, increases unresolved cases, and shifts drawdown. The chronological target fractions also vary by block:

| Block | Buffer 0 (T/SL/open; target/resolved) | Buffer 2 | Buffer 4 |
|---|---:|---:|---:|
| Jan–Mar (94 entries) | 38/53/3; 41.8% | 39/51/4; 43.3% | 40/50/4; 44.4% |
| Apr–Jun (97 entries) | 29/61/7; 32.2% | 29/60/8; 32.6% | 30/58/9; 34.1% |
| Jul–Sep (62 entries) | 20/37/5; 35.1% | 21/35/6; 37.5% | 21/34/7; 38.2% |

The higher conditional target fraction at wider buffers does not justify a buffer: unresolved counts and average losses also rise, while monthly/chronological behavior remains mixed. The 0/2/4-point set is a bounded sensitivity check, not an optimization search. **The data does not establish an evidence-backed numeric buffer.**

### Buffer-0 subgroup counts

These are the hypothetical primary-anchor outcomes, not canonical wins/losses.

| Group | Entries | Target | SL | Unresolved | Target / resolved |
|---|---:|---:|---:|---:|---:|
| CE | 126 | 43 | 75 | 8 | 36.4% |
| PE | 127 | 44 | 76 | 7 | 36.7% |
| ITM2 | 128 | 43 | 76 | 9 | 36.1% |
| ITM3 | 125 | 44 | 75 | 6 | 37.0% |
| 09:15–09:59 | 62 | 26 | 36 | 0 | 41.9% |
| 10:00–10:59 | 114 | 37 | 73 | 4 | 33.6% |
| 11:00+ | 77 | 24 | 42 | 11 | 36.4% |

Monthly buffer-0 simulation counts (entries: target/SL/unresolved): Jan 35: 17/18/0; Feb 38: 13/24/1; Mar 21: 8/11/2; Apr 27: 3/20/4; May 34: 12/19/3; Jun 36: 14/22/0; Jul 21: 9/10/2; Aug 26: 9/14/3; Sep 15: 2/13/0. These conditional rates and point outcomes remain subject to the incomplete option universe and should not be used to select a subgroup.

## 5. Structural-stop proposal and exact paper-engine behavior

**Research candidate:**

```text
anchor = minimum option premium low from the first completed Opening-Low-break candle
         through the completed candle immediately before the breakout entry candle
paper stop = anchor - EKALAYAVA_SL_BUFFER_POINTS
stop touch = a later completed 5-minute candle low <= paper stop
target = Opening High; target touch = a later completed 5-minute candle high >= target
same bar touches both = AMBIGUOUS; no intrabar order is assumed
session/data end before either = unresolved; no forced close is invented
```

The primary anchor is selected as the clearest causal definition for **further controlled validation**, not as a proven optimal or canonical stop. The empirical comparisons do not justify a specific buffer. `EKALAYAVA_SL_BUFFER_POINTS` is therefore a controlled optional parameter and is **unset by default**. With it unset, the paper engine records structural low and target observations but leaves status unresolved and realizes no points. If explicitly set, the paper engine tracks the candidate stop and target and journals paper-only target, stop, ambiguous, or session-end unresolved states. This opt-in engine capability does not itself amend the canonical strategy document; a rule owner must approve/version the actual strategy rule before any Ekalayava P&L comparison or live paper lifecycle is considered valid.

## 6. Missing-data impact and readiness

The 185-session window has 184 underlying dates, 13,783/13,875 underlying bars (99.3%), and 42,149/55,500 option bars (75.9%) across 740 expected option contract-days. There are 561 complete, 1 partial, and 178 missing/unselectable contract-days; 112 days are fully usable, 55 partial, and 18 unusable. The 253 observed entries occurred on 202 fully usable and 51 partially usable days; each exact event contract-day itself has 75/75 session bars. Missing contracts can suppress entries and bias observed touch and hypothetical lifecycle rates. September ends Sep 29.

**Readiness: Ekalayava is READY FOR OBSERVATION ONLY.** The default remains structural observation without a selected stop buffer, and the proposed anchor/buffer is not yet canonical. End-to-end Groww observer orchestration, session calendar, and reconnect integration remain incomplete. L2L remains **NOT READY** for controlled live paper observation for those integration reasons. `EXECUTION_ALLOWED=false`, `PAPER_ONLY=true`; no live orders or market observer were started.

## 7. Next research decision

Approve or reject the versioned pre-breakout reversal-trough anchor as a candidate rule; specify a numeric buffer (or an explicit no-buffer rule) and its live touch convention; then settle opposite-signal, session-end, expiry, and end-of-data treatment. If no buffer is accepted, keep Ekalayava observation-only and do not claim a full P&L comparison. The next data task is separate: recover exact unavailable historical contract-days only if authoritative records become available; do not substitute contracts.

Machine-readable structural, buffer, subgroup, monthly, and chronological calculations: [`EKALAYAVA_FINAL_RESEARCH.json`](EKALAYAVA_FINAL_RESEARCH.json). Canonical audit: [`ekalayava_spec_implementation_audit.md`](ekalayava_spec_implementation_audit.md).
