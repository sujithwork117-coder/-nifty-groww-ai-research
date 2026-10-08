# L2L Target-Hit Timing Research — Jan–Sep 2026

**Scope:** Existing corrected Jan–Sep baseline only (`final_baseline.json`) and its already-downloaded exact-contract 5-minute option candles. No full research run, new download, or strategy change was performed. The canonical entry remains red breakdown below Opening Low, then the first later completed green candle, entered at that candle’s close.

## Summary

- **361 setups:** 203 resolved (**58 target, 145 stop-loss**), 157 skipped because the entry close was already at/below the stop, and 1 ambiguous. Target hits were **58/203 = 28.6%** of resolved trades.
- The earliest observed target hits occurred in the **first 5-minute candle after entry**: 14/58 (24.1%). **25/58 (43.1%)** were first seen within the first two post-entry bars (nominally within 10 minutes); **34/58 (58.6%)** within three bars (15 minutes); **39/58 (67.2%)** within six bars (30 minutes); **49/58 (84.5%)** within twelve bars (60 minutes); **57/58 (98.3%)** within eighteen bars (90 minutes); one first appeared in the bar window beginning 110 minutes after entry.
- Since source bars are OHLC only, the exact intrabar touch instant is unavailable. Across the 58 target paths, the **median actual elapsed-time interval is 10–15 minutes**, and the **mean is bounded by 23.6–28.6 minutes**. The reported median/mean intervals come from first target-touch candle windows, not guessed touch instants.
- The fastest observed hit is in the first candle after the entry candle closes: **0–5 minutes after entry**. No post-entry same-entry-candle target hit is causally measurable.

## Definitions and time resolution

Baseline event `timestamp` is the entry candle’s 5-minute bucket start. Under the canonical rule the entry is at that candle’s completed close, so `entry close time = timestamp + 5 minutes`. Baseline `exit_time` identifies the first later 5-minute candle whose OHLC resolved the trade; it is that candle’s start, not an intrabar target-touch timestamp. For a target bar, the possible elapsed time from entry-close to touch is reported as the interval `[target-bar start − entry close, target-bar end − entry close]`, clipped at zero. For example, the first subsequent candle means **0–5 minutes** after entry.

The “number of candles” below is the ordinal of the first subsequent candle whose high met the target (1 = the first candle after the entry candle). The number of fully completed bars at the actual touch can range from ordinal−1 to ordinal. Exact touch time and within-bar event order cannot be recovered from 5-minute OHLC. Entry time in this report is the actual completed-candle close, not the timestamp printed on the entry candle.

## Target timing distribution

| First target-touch candle window after entry | Target hits | Share of target hits |
|---|---:|---:|
| 0–5 min | 14 | 24.1% |
| 5–10 min | 11 | 19.0% |
| 10–15 min | 9 | 15.5% |
| 15–20 min | 2 | 3.4% |
| 20–25 min | 3 | 5.2% |
| 30–35 min | 3 | 5.2% |
| 40–45 min | 2 | 3.4% |
| 45–50 min | 3 | 5.2% |
| 55–60 min | 2 | 3.4% |
| 60–65 min | 1 | 1.7% |
| 65–70 min | 1 | 1.7% |
| 70–75 min | 1 | 1.7% |
| 75–80 min | 1 | 1.7% |
| 85–90 min | 4 | 6.9% |
| >90 min | 1 | 1.7% |
| **Total** | **58** | **100%** |

Cumulative target-hit counts by elapsed-time limit (based on the first target-touch candle window):

| Limit | Hits whose full observed candle window ends by this limit | Share of 58 |
|---|---:|---:|
| 5 minutes | 14 | 24.1% |
| 10 minutes | 25 | 43.1% |
| 15 minutes | 34 | 58.6% |
| 30 minutes | 39 | 67.2% |
| 60 minutes | 49 | 84.5% |
| 90 minutes | 57 | 98.3% |

At bar-window boundaries the exact touch may occur at the boundary or anywhere within the five-minute candle. These are candle-window counts, not claims of exact elapsed-minute precision.

| Timing measure | Result |
|---|---:|
| Targets among resolved trades | 58/203 (28.6%) |
| Median time-to-target, OHLC-supported interval | 10–15 min |
| Mean time-to-target, OHLC-supported bounds | 23.6–28.6 min |
| Fastest possible / observed candle window | First post-entry candle, 0–5 min |
| Latest observed target-touch window | 110–115 min after entry |
| Target first seen in same entry candle after entry | 0 causally measurable; entry candle ends at entry |

### Target touches by side and rank

| Group | Resolved | Targets | SL | Target / resolved | Median elapsed interval | Mean elapsed bounds |
|---|---:|---:|---:|---:|---:|---:|
| CE | 104 | 26 | 78 | 25.0% | 10–15 min | 19.4–24.4 min |
| PE | 99 | 32 | 67 | 32.3% | 12.5–17.5 min | 27.0–32.0 min |
| ITM2 | 102 | 27 | 75 | 26.5% | 10–15 min | 23.0–28.0 min |
| ITM3 | 101 | 31 | 70 | 30.7% | 10–15 min | 24.2–29.2 min |

Target-hit counts by timing window are 26 CE / 32 PE and 27 ITM2 / 31 ITM3. Elapsed intervals are conditional on each group’s target-hit cases and use the same 5-minute OHLC bounds; the PE mean includes the 110–115 minute case. These are descriptive counts from the observed baseline sample.

## Monthly distribution

| Month | Setups | Resolved | Targets | SL | Skipped |
|---|---:|---:|---:|---:|---:|
| 2026-01 | 55 | 32 | 11 | 21 | 22 |
| 2026-02 | 49 | 15 | 6 | 9 | 34 |
| 2026-03 | 26 | 16 | 2 | 14 | 10 |
| 2026-04 | 36 | 19 | 4 | 15 | 17 |
| 2026-05 | 52 | 28 | 14 | 14 | 24 |
| 2026-06 | 51 | 38 | 5 | 33 | 13 |
| 2026-07 | 34 | 25 | 3 | 22 | 9 |
| 2026-08 | 38 | 16 | 9 | 7 | 22 |
| 2026-09 | 20 | 14 | 4 | 10 | 6 |

Target counts by month were Jan 11, Feb 6, Mar 2, Apr 4, May 14, Jun 5, Jul 3, Aug 9, Sep 4. September data ends Sep 29; contract-day coverage is incomplete as recorded in the baseline.

## Entry-time distribution

| Entry time (IST; completed close) | Setups | Resolved | Targets | SL | Skipped |
|---|---:|---:|---:|---:|---:|
| 09:15–09:59 | 285 | 154 | 40 | 114 | 131 |
| 10:00–10:59 | 74 | 48 | 18 | 30 | 25 |
| 11:00 | 2 | 1 | 0 | 1 | 1 |

Among target hits, 40 entries were in the 09:xx hour and 18 in the 10:xx hour; no target outcome came from an 11:00 entry. For target hits entered in the 09:xx hour, median elapsed interval was 5–10 minutes and mean was 14.6–19.6 minutes; for 10:xx entries, median was 37.5–42.5 minutes and mean was 43.6–48.6 minutes. The canonical window and baseline event-time grouping are unchanged.

## OHLC and baseline interpretation limitations

- **No exact intrabar target timestamp:** a 5-minute `high >= Opening High` establishes only that the target level occurred somewhere in that candle (subject to data accuracy). It cannot identify the second, ordering against the candle low, or whether an open gapped across the level. The table therefore provides the target-touch candle interval; `exit_time` should not be read as an exact touch instant.
- **Entry candle:** 2 of the 58 target-outcome entry candles had `high >= target`. Because entry occurs at that completed candle’s close, such an entry-candle touch cannot be counted as occurring after entry; its order relative to the eventual close is unknowable. The baseline simulator correctly starts target/SL resolution only on subsequent candles for this chronology.
- **Target at/below entry:** 1 of 58 target outcomes had entry price 129.10 versus target 126.50. The stored simulator labels the next future bar TARGET under its `high >= target` test even though price was already above the target level at entry. This is a target-level/long-side interpretation artifact, not evidence of a positive upward move to target. One of the 58 first target bars also opened at or above the target, consistent with an immediate/gap-through observation. Excluding the entry-at/above-target case descriptively leaves 57 target outcomes; their median actual elapsed-time interval remains 10–15 minutes and mean is bounded by 24.0–29.0 minutes. No rule or result was altered.
- **Missing data:** the corrected Jan–Sep dataset has 75.9% of expected option candles and 178 missing/unselectable contract-day slots; the sample includes events from both fully and partially usable days. For these 58 target outcomes, the first later OHLC target bar matched the stored baseline `exit_time`, and there were no missing expected 5-minute intervals between entry and that observed bar. Missing contracts can still omit entire setups; results describe observed events, not a complete market census.
- One additional resolved-sample setup is `AMBIGUOUS` (both SL and target touched in one 5-minute candle) and is not counted among 58 TARGET/145 SL outcomes. OHLC cannot determine which level was hit first in that bar.

## Every resolved setup

The table contains all 203 resolved TARGET/SL setups. The baseline entry timestamp is converted to the completed-candle close. For TARGET, “first target bar” gives the earliest later OHLC candle whose high reached the Opening High; the time interval is the possible elapsed time after entry. For SL, no target was reached before the stop resolved the setup, so target timing is not applicable. “Bars completed at touch” is an OHLC-supported range.

| Date | Contract | Entry close IST | Entry | Target (Opening High) | Outcome | First target bar IST | Elapsed interval | First future bar # | Completed bars at touch |
|---|---|---|---:|---:|---|---|---|---:|---|
| 2026-01-01 | CE ITM3 26050 | 2026-01-01 09:30 | 187.55 | 206.25 | SL | — | — | — | — |
| 2026-01-01 | CE ITM2 26100 | 2026-01-01 09:30 | 151.30 | 167.20 | SL | — | — | — | — |
| 2026-01-01 | PE ITM2 26250 | 2026-01-01 10:00 | 129.10 | 126.50 | TARGET | 2026-01-01 10:00–2026-01-01 10:05 | 0–5 min | 1 | 0–1 |
| 2026-01-05 | PE ITM2 26400 | 2026-01-05 10:30 | 78.45 | 109.55 | TARGET | 2026-01-05 11:25–2026-01-05 11:30 | 55–60 min | 12 | 11–12 |
| 2026-01-05 | PE ITM3 26450 | 2026-01-05 10:30 | 111.50 | 147.15 | TARGET | 2026-01-05 11:25–2026-01-05 11:30 | 55–60 min | 12 | 11–12 |
| 2026-01-06 | CE ITM3 26050 | 2026-01-06 09:35 | 170.60 | 221.00 | SL | — | — | — | — |
| 2026-01-06 | CE ITM2 26100 | 2026-01-06 09:35 | 125.45 | 173.85 | SL | — | — | — | — |
| 2026-01-06 | PE ITM2 26250 | 2026-01-06 10:10 | 36.15 | 74.45 | TARGET | 2026-01-06 11:15–2026-01-06 11:20 | 65–70 min | 14 | 13–14 |
| 2026-01-06 | PE ITM3 26300 | 2026-01-06 10:10 | 67.65 | 109.35 | TARGET | 2026-01-06 11:10–2026-01-06 11:15 | 60–65 min | 13 | 12–13 |
| 2026-01-07 | PE ITM2 26200 | 2026-01-07 09:30 | 132.70 | 145.60 | SL | — | — | — | — |
| 2026-01-07 | PE ITM3 26250 | 2026-01-07 09:30 | 162.95 | 177.55 | SL | — | — | — | — |
| 2026-01-08 | CE ITM3 26000 | 2026-01-08 09:40 | 154.00 | 179.65 | SL | — | — | — | — |
| 2026-01-08 | CE ITM2 26050 | 2026-01-08 09:40 | 121.30 | 145.00 | SL | — | — | — | — |
| 2026-01-09 | CE ITM3 25750 | 2026-01-09 09:45 | 209.90 | 237.60 | SL | — | — | — | — |
| 2026-01-09 | CE ITM2 25800 | 2026-01-09 09:45 | 172.40 | 197.00 | SL | — | — | — | — |
| 2026-01-16 | CE ITM3 25600 | 2026-01-16 09:45 | 207.85 | 226.45 | TARGET | 2026-01-16 09:55–2026-01-16 10:00 | 10–15 min | 3 | 2–3 |
| 2026-01-16 | CE ITM2 25650 | 2026-01-16 09:45 | 171.95 | 189.60 | TARGET | 2026-01-16 09:55–2026-01-16 10:00 | 10–15 min | 3 | 2–3 |
| 2026-01-21 | PE ITM2 25200 | 2026-01-21 09:40 | 126.55 | 148.70 | TARGET | 2026-01-21 09:55–2026-01-21 10:00 | 15–20 min | 4 | 3–4 |
| 2026-01-21 | PE ITM3 25250 | 2026-01-21 09:40 | 147.85 | 169.60 | TARGET | 2026-01-21 09:55–2026-01-21 10:00 | 15–20 min | 4 | 3–4 |
| 2026-01-21 | CE ITM2 25050 | 2026-01-21 10:05 | 247.10 | 347.90 | SL | — | — | — | — |
| 2026-01-22 | CE ITM2 25250 | 2026-01-22 10:35 | 185.10 | 200.00 | SL | — | — | — | — |
| 2026-01-23 | CE ITM3 25200 | 2026-01-23 10:00 | 189.50 | 216.65 | SL | — | — | — | — |
| 2026-01-23 | CE ITM2 25250 | 2026-01-23 10:00 | 156.15 | 182.05 | SL | — | — | — | — |
| 2026-01-27 | PE ITM2 25150 | 2026-01-27 09:55 | 76.85 | 175.10 | SL | — | — | — | — |
| 2026-01-27 | PE ITM3 25200 | 2026-01-27 09:55 | 102.45 | 209.05 | SL | — | — | — | — |
| 2026-01-28 | PE ITM2 25300 | 2026-01-28 09:35 | 215.00 | 237.90 | TARGET | 2026-01-28 10:05–2026-01-28 10:10 | 30–35 min | 7 | 6–7 |
| 2026-01-28 | PE ITM3 25350 | 2026-01-28 09:35 | 237.45 | 271.35 | TARGET | 2026-01-28 10:05–2026-01-28 10:10 | 30–35 min | 7 | 6–7 |
| 2026-01-28 | CE ITM3 25100 | 2026-01-28 09:50 | 379.00 | 420.60 | SL | — | — | — | — |
| 2026-01-29 | CE ITM3 25200 | 2026-01-29 09:35 | 255.85 | 299.00 | SL | — | — | — | — |
| 2026-01-29 | CE ITM2 25250 | 2026-01-29 09:35 | 227.00 | 266.10 | SL | — | — | — | — |
| 2026-01-30 | CE ITM3 25150 | 2026-01-30 09:30 | 258.00 | 333.95 | SL | — | — | — | — |
| 2026-01-30 | CE ITM2 25200 | 2026-01-30 09:30 | 229.65 | 263.80 | SL | — | — | — | — |
| 2026-02-01 | PE ITM3 25450 | 2026-02-01 10:45 | 244.00 | 297.75 | SL | — | — | — | — |
| 2026-02-06 | CE ITM3 25500 | 2026-02-06 09:50 | 162.20 | 207.65 | SL | — | — | — | — |
| 2026-02-09 | CE ITM2 25850 | 2026-02-09 09:30 | 78.00 | 100.25 | SL | — | — | — | — |
| 2026-02-09 | CE ITM3 25800 | 2026-02-09 09:45 | 89.90 | 123.20 | TARGET | 2026-02-09 10:55–2026-02-09 11:00 | 70–75 min | 15 | 14–15 |
| 2026-02-09 | PE ITM2 26000 | 2026-02-09 10:10 | 198.05 | 238.60 | SL | — | — | — | — |
| 2026-02-10 | CE ITM2 25850 | 2026-02-10 09:30 | 88.60 | 101.10 | TARGET | 2026-02-10 09:30–2026-02-10 09:35 | 0–5 min | 1 | 0–1 |
| 2026-02-12 | CE ITM2 25800 | 2026-02-12 09:40 | 159.65 | 192.85 | SL | — | — | — | — |
| 2026-02-18 | CE ITM3 25650 | 2026-02-18 09:30 | 187.60 | 216.00 | SL | — | — | — | — |
| 2026-02-18 | CE ITM2 25700 | 2026-02-18 09:30 | 157.10 | 184.00 | SL | — | — | — | — |
| 2026-02-18 | PE ITM2 25850 | 2026-02-18 09:50 | 196.35 | 211.20 | TARGET | 2026-02-18 09:50–2026-02-18 09:55 | 0–5 min | 1 | 0–1 |
| 2026-02-18 | PE ITM3 25900 | 2026-02-18 09:50 | 230.15 | 244.50 | TARGET | 2026-02-18 09:50–2026-02-18 09:55 | 0–5 min | 1 | 0–1 |
| 2026-02-20 | CE ITM3 25300 | 2026-02-20 09:35 | 247.45 | 254.60 | TARGET | 2026-02-20 09:40–2026-02-20 09:45 | 5–10 min | 2 | 1–2 |
| 2026-02-20 | CE ITM2 25350 | 2026-02-20 09:35 | 207.50 | 217.95 | TARGET | 2026-02-20 09:40–2026-02-20 09:45 | 5–10 min | 2 | 1–2 |
| 2026-02-27 | CE ITM3 25350 | 2026-02-27 09:40 | 131.05 | 182.60 | SL | — | — | — | — |
| 2026-02-27 | CE ITM2 25400 | 2026-02-27 09:40 | 103.50 | 140.20 | SL | — | — | — | — |
| 2026-03-02 | CE ITM2 24650 | 2026-03-02 09:35 | 346.55 | 392.90 | SL | — | — | — | — |
| 2026-03-02 | PE ITM2 24800 | 2026-03-02 09:40 | 47.20 | 100.00 | SL | — | — | — | — |
| 2026-03-02 | PE ITM3 24850 | 2026-03-02 09:40 | 60.00 | 127.70 | SL | — | — | — | — |
| 2026-03-10 | PE ITM2 24350 | 2026-03-10 10:25 | 194.00 | 227.00 | SL | — | — | — | — |
| 2026-03-10 | PE ITM3 24400 | 2026-03-10 10:25 | 237.00 | 268.55 | SL | — | — | — | — |
| 2026-03-12 | PE ITM2 23750 | 2026-03-12 10:05 | 303.65 | 379.85 | SL | — | — | — | — |
| 2026-03-12 | PE ITM3 23800 | 2026-03-12 10:05 | 328.10 | 408.10 | SL | — | — | — | — |
| 2026-03-13 | PE ITM2 23550 | 2026-03-13 09:35 | 268.00 | 311.85 | SL | — | — | — | — |
| 2026-03-16 | CE ITM3 23000 | 2026-03-16 09:30 | 283.95 | 368.50 | TARGET | 2026-03-16 09:40–2026-03-16 09:45 | 10–15 min | 3 | 2–3 |
| 2026-03-16 | CE ITM2 23050 | 2026-03-16 09:30 | 250.20 | 334.30 | TARGET | 2026-03-16 09:40–2026-03-16 09:45 | 10–15 min | 3 | 2–3 |
| 2026-03-18 | PE ITM2 23700 | 2026-03-18 09:55 | 211.85 | 270.05 | SL | — | — | — | — |
| 2026-03-19 | CE ITM3 23100 | 2026-03-19 09:45 | 330.35 | 413.35 | SL | — | — | — | — |
| 2026-03-20 | PE ITM2 23200 | 2026-03-20 09:40 | 209.00 | 266.20 | SL | — | — | — | — |
| 2026-03-20 | PE ITM3 23250 | 2026-03-20 09:40 | 230.25 | 300.00 | SL | — | — | — | — |
| 2026-03-27 | CE ITM3 23050 | 2026-03-27 09:45 | 255.05 | 312.80 | SL | — | — | — | — |
| 2026-03-30 | CE ITM2 22500 | 2026-03-30 10:40 | 113.25 | 207.25 | SL | — | — | — | — |
| 2026-04-06 | PE ITM3 22900 | 2026-04-06 09:45 | 376.50 | 395.25 | TARGET | 2026-04-06 09:45–2026-04-06 09:50 | 0–5 min | 1 | 0–1 |
| 2026-04-09 | CE ITM2 23850 | 2026-04-09 10:05 | 198.05 | 246.25 | SL | — | — | — | — |
| 2026-04-13 | PE ITM2 23700 | 2026-04-13 10:15 | 103.15 | 171.45 | SL | — | — | — | — |
| 2026-04-15 | CE ITM3 24050 | 2026-04-15 09:45 | 334.25 | 392.30 | SL | — | — | — | — |
| 2026-04-15 | CE ITM2 24100 | 2026-04-15 09:45 | 302.75 | 357.60 | SL | — | — | — | — |
| 2026-04-16 | PE ITM3 24500 | 2026-04-16 09:35 | 269.45 | 293.55 | TARGET | 2026-04-16 09:35–2026-04-16 09:40 | 0–5 min | 1 | 0–1 |
| 2026-04-16 | CE ITM3 24250 | 2026-04-16 09:50 | 229.70 | 262.35 | SL | — | — | — | — |
| 2026-04-16 | CE ITM2 24300 | 2026-04-16 09:50 | 201.20 | 231.95 | SL | — | — | — | — |
| 2026-04-17 | PE ITM2 24250 | 2026-04-17 09:35 | 211.80 | 270.05 | SL | — | — | — | — |
| 2026-04-17 | PE ITM3 24300 | 2026-04-17 09:35 | 238.65 | 302.40 | SL | — | — | — | — |
| 2026-04-22 | CE ITM3 24350 | 2026-04-22 09:35 | 276.10 | 318.80 | SL | — | — | — | — |
| 2026-04-22 | CE ITM2 24400 | 2026-04-22 09:35 | 249.00 | 287.80 | SL | — | — | — | — |
| 2026-04-23 | PE ITM3 24350 | 2026-04-23 09:35 | 298.20 | 347.95 | SL | — | — | — | — |
| 2026-04-27 | PE ITM2 24050 | 2026-04-27 09:35 | 129.40 | 150.30 | SL | — | — | — | — |
| 2026-04-27 | PE ITM3 24100 | 2026-04-27 09:35 | 157.15 | 171.60 | SL | — | — | — | — |
| 2026-04-27 | CE ITM3 23850 | 2026-04-27 09:45 | 258.50 | 279.35 | TARGET | 2026-04-27 09:45–2026-04-27 09:50 | 0–5 min | 1 | 0–1 |
| 2026-04-27 | CE ITM2 23900 | 2026-04-27 09:45 | 218.90 | 247.70 | TARGET | 2026-04-27 09:45–2026-04-27 09:50 | 0–5 min | 1 | 0–1 |
| 2026-04-29 | PE ITM2 24200 | 2026-04-29 09:35 | 233.10 | 283.05 | SL | — | — | — | — |
| 2026-04-29 | PE ITM3 24250 | 2026-04-29 09:35 | 262.00 | 309.05 | SL | — | — | — | — |
| 2026-05-04 | CE ITM3 23950 | 2026-05-04 10:30 | 314.90 | 380.10 | SL | — | — | — | — |
| 2026-05-04 | CE ITM2 24000 | 2026-05-04 10:30 | 274.45 | 336.35 | SL | — | — | — | — |
| 2026-05-05 | PE ITM2 24100 | 2026-05-05 10:00 | 88.20 | 171.15 | SL | — | — | — | — |
| 2026-05-05 | PE ITM3 24150 | 2026-05-05 10:00 | 124.05 | 218.15 | TARGET | 2026-05-05 10:30–2026-05-05 10:35 | 30–35 min | 7 | 6–7 |
| 2026-05-07 | CE ITM3 24250 | 2026-05-07 10:15 | 231.35 | 295.90 | SL | — | — | — | — |
| 2026-05-07 | CE ITM2 24300 | 2026-05-07 10:15 | 202.90 | 275.05 | SL | — | — | — | — |
| 2026-05-08 | PE ITM2 24300 | 2026-05-08 09:35 | 207.40 | 234.75 | TARGET | 2026-05-08 09:45–2026-05-08 09:50 | 10–15 min | 3 | 2–3 |
| 2026-05-08 | PE ITM3 24350 | 2026-05-08 10:50 | 219.30 | 269.25 | SL | — | — | — | — |
| 2026-05-14 | PE ITM2 23600 | 2026-05-14 09:35 | 206.00 | 241.40 | TARGET | 2026-05-14 09:40–2026-05-14 09:45 | 5–10 min | 2 | 1–2 |
| 2026-05-14 | PE ITM3 23650 | 2026-05-14 09:35 | 231.60 | 271.85 | TARGET | 2026-05-14 09:40–2026-05-14 09:45 | 5–10 min | 2 | 1–2 |
| 2026-05-15 | PE ITM2 23800 | 2026-05-15 09:50 | 172.95 | 238.55 | SL | — | — | — | — |
| 2026-05-15 | PE ITM3 23850 | 2026-05-15 09:50 | 197.55 | 267.90 | SL | — | — | — | — |
| 2026-05-19 | PE ITM2 23750 | 2026-05-19 09:35 | 114.35 | 134.05 | TARGET | 2026-05-19 09:35–2026-05-19 09:40 | 0–5 min | 1 | 0–1 |
| 2026-05-19 | PE ITM3 23800 | 2026-05-19 09:35 | 149.60 | 167.20 | TARGET | 2026-05-19 09:35–2026-05-19 09:40 | 0–5 min | 1 | 0–1 |
| 2026-05-19 | CE ITM3 23550 | 2026-05-19 10:05 | 165.05 | 208.40 | TARGET | 2026-05-19 10:10–2026-05-19 10:15 | 5–10 min | 2 | 1–2 |
| 2026-05-19 | CE ITM2 23600 | 2026-05-19 10:05 | 126.20 | 166.00 | TARGET | 2026-05-19 10:10–2026-05-19 10:15 | 5–10 min | 2 | 1–2 |
| 2026-05-25 | PE ITM2 24000 | 2026-05-25 09:35 | 121.75 | 145.00 | SL | — | — | — | — |
| 2026-05-25 | PE ITM3 24050 | 2026-05-25 09:35 | 149.85 | 181.85 | SL | — | — | — | — |
| 2026-05-25 | CE ITM3 23800 | 2026-05-25 09:55 | 204.80 | 234.00 | TARGET | 2026-05-25 10:35–2026-05-25 10:40 | 40–45 min | 9 | 8–9 |
| 2026-05-25 | CE ITM2 23850 | 2026-05-25 09:55 | 170.45 | 196.65 | TARGET | 2026-05-25 10:40–2026-05-25 10:45 | 45–50 min | 10 | 9–10 |
| 2026-05-27 | PE ITM2 23950 | 2026-05-27 09:30 | 180.30 | 218.90 | SL | — | — | — | — |
| 2026-05-27 | PE ITM3 24000 | 2026-05-27 09:30 | 207.75 | 247.30 | SL | — | — | — | — |
| 2026-05-27 | CE ITM3 23750 | 2026-05-27 10:05 | 271.80 | 299.15 | TARGET | 2026-05-27 10:15–2026-05-27 10:20 | 10–15 min | 3 | 2–3 |
| 2026-05-27 | CE ITM2 23800 | 2026-05-27 10:05 | 238.60 | 266.70 | TARGET | 2026-05-27 10:15–2026-05-27 10:20 | 10–15 min | 3 | 2–3 |
| 2026-05-29 | CE ITM3 23800 | 2026-05-29 09:35 | 227.20 | 274.30 | SL | — | — | — | — |
| 2026-05-29 | CE ITM2 23850 | 2026-05-29 09:35 | 194.95 | 238.65 | SL | — | — | — | — |
| 2026-05-29 | PE ITM2 24000 | 2026-05-29 10:20 | 140.00 | 179.30 | TARGET | 2026-05-29 12:10–2026-05-29 12:15 | 110–115 min | 23 | 22–23 |
| 2026-05-29 | PE ITM3 24050 | 2026-05-29 10:30 | 177.40 | 198.30 | TARGET | 2026-05-29 10:50–2026-05-29 10:55 | 20–25 min | 5 | 4–5 |
| 2026-06-02 | PE ITM3 23400 | 2026-06-02 09:50 | 128.30 | 171.60 | SL | — | — | — | — |
| 2026-06-03 | CE ITM2 23350 | 2026-06-03 09:40 | 181.80 | 253.05 | SL | — | — | — | — |
| 2026-06-04 | PE ITM2 23350 | 2026-06-04 09:35 | 166.70 | 210.30 | SL | — | — | — | — |
| 2026-06-04 | PE ITM3 23400 | 2026-06-04 09:35 | 191.20 | 239.55 | SL | — | — | — | — |
| 2026-06-05 | CE ITM3 23350 | 2026-06-05 09:30 | 244.95 | 268.45 | SL | — | — | — | — |
| 2026-06-05 | CE ITM2 23400 | 2026-06-05 09:30 | 213.30 | 234.40 | SL | — | — | — | — |
| 2026-06-08 | PE ITM2 23150 | 2026-06-08 09:40 | 108.85 | 151.30 | SL | — | — | — | — |
| 2026-06-08 | PE ITM3 23200 | 2026-06-08 09:40 | 133.05 | 181.30 | SL | — | — | — | — |
| 2026-06-09 | PE ITM2 23300 | 2026-06-09 09:30 | 100.35 | 140.15 | SL | — | — | — | — |
| 2026-06-09 | PE ITM3 23350 | 2026-06-09 09:30 | 138.75 | 180.55 | SL | — | — | — | — |
| 2026-06-09 | CE ITM3 23100 | 2026-06-09 09:55 | 134.25 | 155.15 | SL | — | — | — | — |
| 2026-06-09 | CE ITM2 23150 | 2026-06-09 09:55 | 94.75 | 114.35 | SL | — | — | — | — |
| 2026-06-10 | PE ITM2 23300 | 2026-06-10 09:40 | 162.20 | 221.80 | SL | — | — | — | — |
| 2026-06-10 | PE ITM3 23350 | 2026-06-10 09:40 | 184.45 | 250.45 | SL | — | — | — | — |
| 2026-06-11 | PE ITM2 23200 | 2026-06-11 09:35 | 209.75 | 235.40 | SL | — | — | — | — |
| 2026-06-11 | PE ITM3 23250 | 2026-06-11 09:35 | 239.65 | 267.35 | SL | — | — | — | — |
| 2026-06-12 | CE ITM3 23300 | 2026-06-12 09:50 | 190.30 | 231.00 | SL | — | — | — | — |
| 2026-06-12 | CE ITM2 23350 | 2026-06-12 09:50 | 160.80 | 197.35 | SL | — | — | — | — |
| 2026-06-15 | CE ITM3 23850 | 2026-06-15 09:35 | 146.20 | 185.60 | SL | — | — | — | — |
| 2026-06-15 | CE ITM2 23900 | 2026-06-15 09:45 | 130.00 | 150.00 | SL | — | — | — | — |
| 2026-06-15 | PE ITM3 24100 | 2026-06-15 11:05 | 177.00 | 216.00 | SL | — | — | — | — |
| 2026-06-16 | PE ITM2 24000 | 2026-06-16 09:40 | 94.50 | 138.95 | SL | — | — | — | — |
| 2026-06-16 | PE ITM3 24050 | 2026-06-16 09:40 | 133.15 | 180.30 | SL | — | — | — | — |
| 2026-06-16 | CE ITM2 23850 | 2026-06-16 10:15 | 78.05 | 111.00 | TARGET | 2026-06-16 10:20–2026-06-16 10:25 | 5–10 min | 2 | 1–2 |
| 2026-06-17 | CE ITM3 23900 | 2026-06-17 09:30 | 222.10 | 232.20 | TARGET | 2026-06-17 09:30–2026-06-17 09:35 | 0–5 min | 1 | 0–1 |
| 2026-06-17 | CE ITM2 23950 | 2026-06-17 09:30 | 192.40 | 202.00 | TARGET | 2026-06-17 09:30–2026-06-17 09:35 | 0–5 min | 1 | 0–1 |
| 2026-06-18 | PE ITM2 24150 | 2026-06-18 10:00 | 147.40 | 192.45 | SL | — | — | — | — |
| 2026-06-18 | PE ITM3 24200 | 2026-06-18 10:00 | 175.70 | 224.00 | TARGET | 2026-06-18 11:15–2026-06-18 11:20 | 75–80 min | 16 | 15–16 |
| 2026-06-18 | CE ITM3 23950 | 2026-06-18 10:45 | 190.55 | 240.25 | SL | — | — | — | — |
| 2026-06-19 | CE ITM3 23850 | 2026-06-19 09:40 | 201.95 | 226.70 | SL | — | — | — | — |
| 2026-06-22 | PE ITM2 24200 | 2026-06-22 09:30 | 124.70 | 159.70 | SL | — | — | — | — |
| 2026-06-22 | PE ITM3 24250 | 2026-06-22 09:40 | 158.20 | 198.50 | SL | — | — | — | — |
| 2026-06-24 | PE ITM2 23850 | 2026-06-24 09:35 | 138.15 | 188.00 | SL | — | — | — | — |
| 2026-06-24 | PE ITM3 23900 | 2026-06-24 09:35 | 162.15 | 216.05 | SL | — | — | — | — |
| 2026-06-25 | PE ITM2 24200 | 2026-06-25 09:30 | 142.35 | 166.15 | SL | — | — | — | — |
| 2026-06-25 | PE ITM3 24250 | 2026-06-25 09:30 | 172.40 | 199.10 | SL | — | — | — | — |
| 2026-06-29 | CE ITM3 23950 | 2026-06-29 09:40 | 163.60 | 195.35 | TARGET | 2026-06-29 10:25–2026-06-29 10:30 | 45–50 min | 10 | 9–10 |
| 2026-06-29 | PE ITM3 24200 | 2026-06-29 10:35 | 132.00 | 188.30 | SL | — | — | — | — |
| 2026-07-08 | CE ITM3 24100 | 2026-07-08 09:45 | 210.15 | 251.85 | SL | — | — | — | — |
| 2026-07-08 | CE ITM2 24150 | 2026-07-08 09:45 | 180.90 | 219.60 | SL | — | — | — | — |
| 2026-07-08 | PE ITM2 24300 | 2026-07-08 10:50 | 164.30 | 179.10 | SL | — | — | — | — |
| 2026-07-08 | PE ITM3 24350 | 2026-07-08 10:50 | 192.30 | 208.70 | SL | — | — | — | — |
| 2026-07-10 | PE ITM2 24200 | 2026-07-10 09:40 | 121.80 | 172.50 | SL | — | — | — | — |
| 2026-07-10 | PE ITM3 24250 | 2026-07-10 09:40 | 146.90 | 200.00 | SL | — | — | — | — |
| 2026-07-13 | CE ITM3 23900 | 2026-07-13 09:30 | 150.70 | 183.75 | SL | — | — | — | — |
| 2026-07-13 | CE ITM2 23950 | 2026-07-13 09:30 | 117.45 | 148.25 | SL | — | — | — | — |
| 2026-07-14 | CE ITM2 24000 | 2026-07-14 10:00 | 94.35 | 133.75 | SL | — | — | — | — |
| 2026-07-14 | CE ITM3 23950 | 2026-07-14 10:25 | 119.30 | 173.15 | TARGET | 2026-07-14 10:45–2026-07-14 10:50 | 20–25 min | 5 | 4–5 |
| 2026-07-23 | PE ITM2 24000 | 2026-07-23 09:30 | 179.00 | 216.95 | SL | — | — | — | — |
| 2026-07-23 | PE ITM3 24050 | 2026-07-23 09:30 | 210.25 | 249.55 | SL | — | — | — | — |
| 2026-07-24 | CE ITM3 23550 | 2026-07-24 09:55 | 208.00 | 262.60 | SL | — | — | — | — |
| 2026-07-24 | CE ITM2 23600 | 2026-07-24 09:55 | 175.85 | 225.90 | SL | — | — | — | — |
| 2026-07-27 | PE ITM2 24000 | 2026-07-27 09:50 | 92.70 | 127.00 | TARGET | 2026-07-27 10:35–2026-07-27 10:40 | 45–50 min | 10 | 9–10 |
| 2026-07-27 | PE ITM3 24050 | 2026-07-27 09:55 | 137.85 | 161.00 | TARGET | 2026-07-27 10:35–2026-07-27 10:40 | 40–45 min | 9 | 8–9 |
| 2026-07-27 | CE ITM3 23800 | 2026-07-27 10:15 | 178.75 | 206.25 | SL | — | — | — | — |
| 2026-07-27 | CE ITM2 23850 | 2026-07-27 10:15 | 139.30 | 167.20 | SL | — | — | — | — |
| 2026-07-28 | CE ITM3 23850 | 2026-07-28 10:15 | 138.40 | 192.95 | SL | — | — | — | — |
| 2026-07-28 | CE ITM2 23900 | 2026-07-28 10:15 | 93.65 | 146.80 | SL | — | — | — | — |
| 2026-07-28 | PE ITM3 24100 | 2026-07-28 11:00 | 83.10 | 141.35 | SL | — | — | — | — |
| 2026-07-29 | PE ITM3 24300 | 2026-07-29 09:55 | 184.60 | 220.55 | SL | — | — | — | — |
| 2026-07-30 | PE ITM3 24400 | 2026-07-30 09:40 | 213.00 | 259.00 | SL | — | — | — | — |
| 2026-07-31 | CE ITM3 24250 | 2026-07-31 09:45 | 160.00 | 178.75 | SL | — | — | — | — |
| 2026-07-31 | CE ITM2 24300 | 2026-07-31 09:45 | 126.90 | 143.95 | SL | — | — | — | — |
| 2026-08-03 | PE ITM2 24650 | 2026-08-03 09:50 | 119.70 | 154.55 | SL | — | — | — | — |
| 2026-08-04 | PE ITM2 24750 | 2026-08-04 09:30 | 162.55 | 168.30 | TARGET | 2026-08-04 09:30–2026-08-04 09:35 | 0–5 min | 1 | 0–1 |
| 2026-08-04 | CE ITM3 24550 | 2026-08-04 09:40 | 75.90 | 93.70 | TARGET | 2026-08-04 09:45–2026-08-04 09:50 | 5–10 min | 2 | 1–2 |
| 2026-08-05 | CE ITM3 24500 | 2026-08-05 10:35 | 212.45 | 249.00 | TARGET | 2026-08-05 10:55–2026-08-05 11:00 | 20–25 min | 5 | 4–5 |
| 2026-08-06 | PE ITM3 24750 | 2026-08-06 10:00 | 177.05 | 199.95 | SL | — | — | — | — |
| 2026-08-14 | CE ITM2 24300 | 2026-08-14 09:35 | 132.15 | 155.00 | SL | — | — | — | — |
| 2026-08-17 | CE ITM2 24300 | 2026-08-17 09:40 | 69.20 | 115.00 | SL | — | — | — | — |
| 2026-08-18 | PE ITM2 24300 | 2026-08-18 09:35 | 80.95 | 87.80 | TARGET | 2026-08-18 09:45–2026-08-18 09:50 | 10–15 min | 3 | 2–3 |
| 2026-08-18 | PE ITM3 24350 | 2026-08-18 09:35 | 123.25 | 128.60 | TARGET | 2026-08-18 09:40–2026-08-18 09:45 | 5–10 min | 2 | 1–2 |
| 2026-08-21 | CE ITM2 24200 | 2026-08-21 09:30 | 134.70 | 166.95 | SL | — | — | — | — |
| 2026-08-24 | PE ITM2 24350 | 2026-08-24 09:30 | 68.90 | 79.80 | TARGET | 2026-08-24 09:40–2026-08-24 09:45 | 10–15 min | 3 | 2–3 |
| 2026-08-24 | PE ITM3 24400 | 2026-08-24 09:30 | 100.20 | 111.00 | TARGET | 2026-08-24 09:35–2026-08-24 09:40 | 5–10 min | 2 | 1–2 |
| 2026-08-25 | CE ITM3 24050 | 2026-08-25 10:30 | 101.90 | 152.00 | TARGET | 2026-08-25 11:55–2026-08-25 12:00 | 85–90 min | 18 | 17–18 |
| 2026-08-25 | CE ITM2 24100 | 2026-08-25 10:30 | 61.10 | 101.90 | TARGET | 2026-08-25 11:55–2026-08-25 12:00 | 85–90 min | 18 | 17–18 |
| 2026-08-26 | PE ITM2 24400 | 2026-08-26 09:55 | 82.80 | 107.55 | SL | — | — | — | — |
| 2026-08-31 | CE ITM2 24050 | 2026-08-31 09:35 | 80.90 | 160.10 | SL | — | — | — | — |
| 2026-09-01 | CE ITM3 23950 | 2026-09-01 09:30 | 129.70 | 162.40 | SL | — | — | — | — |
| 2026-09-01 | PE ITM3 24200 | 2026-09-01 09:40 | 159.00 | 169.85 | TARGET | 2026-09-01 09:40–2026-09-01 09:45 | 0–5 min | 1 | 0–1 |
| 2026-09-02 | PE ITM2 23950 | 2026-09-02 10:35 | 151.60 | 187.20 | TARGET | 2026-09-02 12:00–2026-09-02 12:05 | 85–90 min | 18 | 17–18 |
| 2026-09-02 | PE ITM3 24000 | 2026-09-02 10:35 | 179.30 | 218.45 | TARGET | 2026-09-02 12:00–2026-09-02 12:05 | 85–90 min | 18 | 17–18 |
| 2026-09-03 | CE ITM3 23900 | 2026-09-03 10:50 | 171.65 | 196.30 | SL | — | — | — | — |
| 2026-09-03 | CE ITM2 23950 | 2026-09-03 10:50 | 139.95 | 161.95 | SL | — | — | — | — |
| 2026-09-07 | CE ITM3 23750 | 2026-09-07 10:05 | 127.75 | 184.95 | SL | — | — | — | — |
| 2026-09-07 | CE ITM2 23800 | 2026-09-07 10:05 | 95.60 | 148.60 | SL | — | — | — | — |
| 2026-09-08 | CE ITM2 23650 | 2026-09-08 09:35 | 74.30 | 108.00 | SL | — | — | — | — |
| 2026-09-09 | CE ITM2 23450 | 2026-09-09 10:15 | 183.25 | 209.95 | TARGET | 2026-09-09 10:20–2026-09-09 10:25 | 5–10 min | 2 | 1–2 |
| 2026-09-10 | CE ITM2 23350 | 2026-09-10 10:20 | 191.40 | 226.45 | SL | — | — | — | — |
| 2026-09-18 | CE ITM2 23250 | 2026-09-18 09:40 | 153.55 | 176.45 | SL | — | — | — | — |
| 2026-09-21 | PE ITM3 23450 | 2026-09-21 09:35 | 104.85 | 141.20 | SL | — | — | — | — |
| 2026-09-22 | CE ITM3 23350 | 2026-09-22 09:40 | 115.10 | 145.50 | SL | — | — | — | — |

## Descriptive conclusion

Target outcomes were not uniformly slow: 14/58 (24.1%) first appeared in the first post-entry 5-minute candle and 25/58 (43.1%) within the first two bars. The median target-touch interval is 10–15 minutes. At the same time, target timing extends to 110–115 minutes and 24/58 targets (41.4%) first appear after 15 minutes. Thus short-duration target behavior is present and material in this observed sample, but it does not characterize every target hit. This is a descriptive timing study only; it does not select a new holding rule, optimize the strategy, or establish profitability.

No canonical strategy rule was modified. No market data was downloaded and no historical baseline was rerun.
