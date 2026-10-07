# Fresh Market Analysis — 2026-09-28 to 2026-10-01

**Scope:** only the four requested NIFTY sessions, 5-minute candles, Asia/Kolkata. Existing canonical Level-to-Level (L2L) and Ekalayava implementations were used without changing rules. No historical experiments were rerun, no missing candles were filled, and no orders were placed. Groww read-only authentication succeeded. Safety settings remained `EXECUTION_ALLOWED=false` and `PAPER_ONLY=true`.

## Data retrieval and quality

The 2026 NSE F&O holiday circular lists 2 October as a holiday and does not list 30 September or 1 October; those two dates are weekdays and were treated as expected sessions. [NSE 2026 F&O holiday circular](https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf). Groww was queried separately by date for the underlying and again for the selected 28–29 September option contracts. The 28 September retry added no candles. Direct Groww requests for 30 September and 1 October returned no underlying candles.

The existing contract selector needs the unique 09:15 underlying open to choose the nearest expiry's CE/PE ITM2/ITM3 strikes. Since 30 September and 1 October have no 09:15 underlying candle, those eight option slots could not be identified canonically; no substitute price or prior-day strike was used. The nearest expiry for both selected dates 28 and 29 September was 29 September.

| Date | Underlying | Selected option coverage | Assessment |
|---|---:|---|---|
| 2026-09-28 | 75/75; complete | 0 complete, 4 partial; 228/300 option bars | Partial observations only |
| 2026-09-29 | 58/75; 17 missing | 0 complete, 4 partial; 194/300 option bars | Partial observations only |
| 2026-09-30 | 0/75; no bars | 4 contracts not selectable without 09:15 underlying | Unusable |
| 2026-10-01 | 0/75; no bars | 4 contracts not selectable without 09:15 underlying | Unusable |

Across the four dates, 1 of 4 underlying sessions is complete, 1 is partial, and 2 are missing. Of the 16 required CE/PE ITM2/ITM3 instrument slots, 8 could be selected and queried; all 8 were partial and none complete. The remaining 8 are unselected/unavailable because their daily ITM ranks cannot be determined without that date's underlying opening price. No day has complete underlying plus all four complete option contracts: 0 fully usable, 2 partially usable, and 2 unusable. Accordingly, this is not a complete four-session strategy sample.

### Exact missing intervals

Each option contract-day below had 75 expected regular-session bars, 09:15–15:25 inclusive. All listed files passed OHLC validation; duplicates were not used.

| Date | Contract | Bars | Missing 5-minute intervals |
|---|---|---:|---|
| Sep 28 | CE ITM2 `NSE-NIFTY-29Sep26-22350-CE` | 61/75 | 09:15, 09:20, 09:25, 09:30, 09:35, 09:50, 09:55, 10:00, 10:30, 10:50, 11:35, 12:15, 13:50, 13:55 |
| Sep 28 | PE ITM2 `NSE-NIFTY-29Sep26-23950-PE` | 52/75 | 09:15, 10:05, 10:50, 11:00, 11:40, 11:45, 12:05, 12:10, 12:15, 12:20, 12:30, 12:45, 12:55, 13:40, 13:50, 13:55, 14:05, 14:10, 14:15, 14:20, 14:25, 14:30, 14:35 |
| Sep 28 | CE ITM3 `NSE-NIFTY-29Sep26-22300-CE` | 72/75 | 09:15, 09:55, 12:35 |
| Sep 28 | PE ITM3 `NSE-NIFTY-29Sep26-24050-PE` | 43/75 | 09:55, 10:00, 10:05, 10:45, 10:50, 11:00, 11:10, 11:35, 11:40, 11:45, 11:55, 12:05, 12:20, 12:25, 12:40, 12:50, 12:55, 13:05, 13:10, 13:15, 13:30, 13:35, 13:40, 14:00, 14:05, 14:10, 14:15, 14:30, 14:40, 14:55, 15:00, 15:05 |
| Sep 29 | CE ITM2 `NSE-NIFTY-29Sep26-22350-CE` | 57/75 | 14:00–15:25, every 5 minutes (18 intervals) |
| Sep 29 | PE ITM2 `NSE-NIFTY-29Sep26-23850-PE` | 38/75 | 09:15, 10:25, 10:35, 10:50, 11:00, 11:05, 11:40, 11:45, 12:00, 12:10, 12:15, 12:20, 12:40, 12:55, 13:00, 13:20, 13:30, 13:35, 13:55, 14:00, 14:05, 14:10, 14:15, 14:20, 14:25, 14:30, 14:35, 14:40, 14:45, 14:50, 14:55, 15:00, 15:05, 15:10, 15:15, 15:20, 15:25 |
| Sep 29 | CE ITM3 `NSE-NIFTY-29Sep26-22300-CE` | 57/75 | 14:00–15:25, every 5 minutes (18 intervals) |
| Sep 29 | PE ITM3 `NSE-NIFTY-29Sep26-23950-PE` | 42/75 | 09:55, 10:35, 10:50, 11:15, 11:30, 11:35, 11:55, 12:10, 12:20, 12:25, 12:50, 13:00, 13:10, 13:25, 13:50, 14:00, 14:05, 14:10, 14:15, 14:20, 14:25, 14:30, 14:35, 14:40, 14:45, 14:50, 14:55, 15:00, 15:05, 15:10, 15:15, 15:20, 15:25 |

On 29 September the underlying itself is missing every 5-minute interval from 14:05 through 15:25. Each of the two CE options stops at 13:55, and the PE options also have substantial gaps. Post-13:55/end-of-day outcomes therefore cannot be determined.

## Day-by-day results

| Date | Data quality | L2L setups observed | L2L targets | L2L SL | L2L points | Ekalayava entries | Ekalayava target touches |
|---|---|---:|---:|---:|---:|---:|---:|
| 28 Sep | Underlying complete; all 4 options partial | 0 on 1 eligible contract; 3 contracts lacked 09:15 | 0 observed | 0 observed | 0 resolved; no resolved trade | 0 on 1 eligible contract | 0 |
| 29 Sep | Underlying 58/75; all 4 options partial | 3 candidates; 3 skipped | 0 | 0 | 0 resolved; no resolved trade | 3 | 2 observed |
| 30 Sep | Underlying absent; option ranks unavailable | N/A | N/A | N/A | N/A | N/A | N/A |
| 01 Oct | Underlying absent; option ranks unavailable | N/A | N/A | N/A | N/A | N/A | N/A |
| **Combined** | **No fully usable day** | **3 observed candidates; 3 skipped** | **0** | **0** | **0 resolved points** | **3 observed entries** | **2 observed touches** |

### Level-to-Level

The current implementation was run on option files with a valid 09:15 opening candle. On 28 September, only PE ITM3 qualified and it produced no observed setup. On 29 September, three candidate setups were found: CE ITM2 and CE ITM3 at 09:40 IST, and PE ITM3 at 10:45 IST. All three were labeled `SKIPPED_SL_ALREADY_BREACHED`: their entry closes (281.25, 329.20, 1349.35) were at or below their canonical stops (344.95, 393.00, 1424.80). There were no executable entries, target exits, stop-loss exits, or resolved point results. The PE ITM3 setup occurred after earlier missing candles, so its detection is especially data-sensitive. MFE/MAE and holding duration are not meaningful for these skipped trades.

No claim that L2L was consistently profitable or that a single day drove profits is supported: there were no resolved trades or realized points, and two of four days had no underlying data. The three observed skips describe only available bars, not the complete four-session strategy record.

### Ekalayava post-entry journal

Ekalayava has no canonical SL or end-of-day exit. The following is descriptive only. MFE/MAE below use all available post-entry bars through the last observed bar, not a realized P&L measure. Gaps may hide earlier target touches or more extreme movement.

| Date / side / rank | Entry IST / price | Entry structure | Opening-high target | Observed post-entry behavior | Last observed / status |
|---|---|---|---:|---|---|
| Sep 29 CE ITM2 | 10:40 / 276.70 | Prior breakdown; causal swing reference 273.00 | 403.55 | Target touched at 12:00. Observed-through-tape MFE +140.50 at 12:00; MAE -21.20 at 11:05. | 13:55; after that 18 intervals through close are missing. Target touch observed; EOD path incomplete. |
| Sep 29 CE ITM3 | 10:40 / 324.10 | Prior breakdown; causal swing reference 320.50 | 436.15 | Target touched at 11:30. Observed-through-tape MFE +140.20 at 12:00; MAE -19.95 at 11:05. | 13:55; after that 18 intervals through close are missing. Target touch observed; EOD path incomplete. |
| Sep 29 PE ITM3 | 09:35 / 1353.70 | Prior breakdown; causal swing reference 1314.75 | 1428.80 | No target touch in available bars. MFE +13.55 at 10:20; MAE -169.20 at 12:05. | 13:55; 33 session intervals are missing in this contract-day. No target observed; unresolved and EOD unknown. |

There were no Ekalayava entries on the one eligible 28 September contract (PE ITM3). The other three 28 September option contracts lacked their opening candle and could not be run without fabricating the opening range. Thus, among three observed 29 September entries, 2/3 (66.7%) touched the opening-high target in observed candles. This small, incomplete sample is not an estimate for four sessions. The two observed target touches were both CE (one ITM2, one ITM3); the single PE ITM3 entry did not touch target in its available tape. All three option tapes end with missing afternoon intervals, so daily-close status is unknown. Ekalayava outcomes remain target touches/open observations, not complete P&L.

## Combined interpretation and historical context

- **L2L:** three setup candidates were observed, all skipped by the existing already-breached-stop rule. No valid entry or resolved point result was recorded. The available evidence cannot answer whether four-day L2L behavior was consistently profitable or driven by one day.
- **Ekalayava:** three entries were observed on 29 September; two CE entries touched opening high and one PE entry remained below target in available data. The PE path reached a larger observed adverse excursion than either CE path, but the contract tapes are incomplete and the sample is three entries.
- **MFE/MAE:** observed Ekalayava excursions were +140.50/-21.20 (CE ITM2), +140.20/-19.95 (CE ITM3), and +13.55/-169.20 (PE ITM3) premium points. These are extrema in available bars only; missing intervals can change them.
- **Prior research context only:** prior independent-period Ekalayava target-touch fractions were 82/170 (48.2%) in Period A and 58/132 (43.9%) in Period B. The current 2/3 observed target touches cannot be compared as a reliable rate because only one day generated entries and all option tapes were partial. Prior L2L resolved gross points were +502.40 in Period A and -333.70 in Period B; this fresh sample has zero resolved L2L trades and cannot extend either result.
- **Recurring behavior to investigate:** both observed CE Ekalayava entries arose at 10:40 IST and reached opening high within 50–80 minutes; with only two CE entries and missing data after 13:55, this is a question for a complete sample, not an established pattern. The PE entry showed materially larger observed adverse movement before the available tape ended.

## Direct answers

1. **L2L over four days:** no resolved trades, zero targets, zero SL exits, three observed candidates skipped on 29 September, and zero resolved points. The other two sessions have no underlying data; 28 September has only one eligible option contract.
2. **Consistency / day concentration:** not assessable; there are no resolved point results, so no profitable day or concentration claim can be made.
3. **Ekalayava after entry:** two CE entries touched opening high; one PE entry had no observed touch and a -169.20 point observed MAE by its last available post-entry bar. All remained without a canonical complete lifecycle.
4. **Opening-high target frequency:** 2 of 3 observed entries (both on 29 September); not a valid four-session rate.
5. **MFE/MAE:** +140.50/-21.20, +140.20/-19.95, and +13.55/-169.20 points for the three entries, subject to missing-candle censoring.
6. **Repeated behavior:** two CE target touches after 50 and 80 minutes from the common 10:40 entry time; too few observations to establish recurrence.
7. **Invalid/incomplete dates:** 30 September and 1 October are unusable due to no underlying bars. 28 and 29 September are partial and cannot support complete-session conclusions. No date is fully usable across underlying and required options.

## Safety and verification

Groww was used read-only; no order endpoints were called. Credentials and tokens are excluded. `EXECUTION_ALLOWED=false`; `PAPER_ONLY=true`. Existing tests were run after this report was generated: **57 passed**.

