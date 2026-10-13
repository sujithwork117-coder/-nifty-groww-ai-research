# Ekalayava Historical Data Coverage — July–December 2025

## Scope and retrieval

One bounded, read-only Groww historical-data and contract-catalog retrieval was
completed for **2025-07-01 through 2025-12-31**, using five-minute candles.
The attempt used the project's documented Groww client, exact daily
catalog-first contract selection, paced requests, and no automatic retries.
No orders were submitted. No other provider, substitute strike/expiry, or
period outside the requested six months was used.

The retrieval manifest is
`data/derived/ekalayava_2025_h2_groww/manifest.json`; raw downloads remain
ignored by Git. It records 10,419 underlying candles across 124 sessions with
a 09:15 opening candle, 492 selected contract-session rows, and 348 unique
exact option contracts. All 348 option contract requests returned data; there
were zero empty or failed option requests. The exact daily selection ladder
and returned paths are recorded in
`reports/ekalayava_guide7_2025_contract_session_coverage.csv`.

## Option-path coverage

| Coverage unit | Complete | Partial | No usable / invalid | Total |
|---|---:|---:|---:|---:|
| Selected contract-session paths | 488 | 4 | 0 | 492 |
| Detected Ekalayava entry paths | 192 | 2 | 0 | 194 |

The entry-event counts by chronological period are:

| Period | Entries | Complete paths | Partial paths | No usable / invalid |
|---|---:|---:|---:|---:|
| Training: 2025-07-01–2025-08-31 | 61 | 61 | 0 | 0 |
| Validation: 2025-09-01–2025-10-31 | 64 | 62 | 2 | 0 |
| Untouched test: 2025-11-01–2025-12-31 | 69 | 69 | 0 | 0 |

The four partial selected contract-session paths and two partial entry paths
remain explicitly identified in the detailed CSVs; they were not relabeled as
complete. The retrieved datasets and manifests distinguish unavailable
historical inventory from an empty response for a requested contract.

## 2026 comparison coverage

The existing saved ledger contains 253 entries. Exact local post-entry
five-minute paths were found for **7** entries: 6 from the July–August
validation period and 1 from September's incomplete period. The other **246**
have no usable exact-contract path (191 Jan–Jun training, 41 Jul–Aug
validation, 14 September incomplete-period entries); no entries were filled
with another strike, expiry, or approximate price. There were no invalid or
mismatched paths among the seven accepted exact matches.

| Existing 2026 period | Complete paths | No usable path | Saved entries |
|---|---:|---:|---:|
| Jan–Jun training | 0 | 191 | 191 |
| Jul–Aug validation | 6 | 41 | 47 |
| Sep incomplete period | 1 | 14 | 15 |
| **Total** | **7** | **246** | **253** |

The single September entry path is complete for that entry, but does not make
the wider September dataset complete or an independent validation period.
Coverage details are in
`reports/ekalayava_guide7_2026_entry_path_coverage.csv`.

## Reproducibility and caveats

The 2025 underlying and options came from Groww's read-only historical
endpoints and catalog; request-level provenance and exact daily selections
are in the ignored manifest and
`reports/ekalayava_guide7_2025_contract_session_coverage.csv`. The 2025
entry ledger is regenerated from the unchanged canonical Ekalayava analyzer
and exact selected option paths, not from substitute contracts.

Historical candle data does not establish executable fills. Fees, taxes,
spreads, slippage and rupee sizing were unavailable. The 2025 results are
gross premium points only. Missing exact paths remain limitations and are
not treated as losses, wins, or no-signal days.

The complete replay command is:

```sh
.venv/bin/python -m tools.run_ekalayava_guide7_research
```

See [EKALAYAVA_MULTI_PERIOD_EXIT_VALIDATION.md](./EKALAYAVA_MULTI_PERIOD_EXIT_VALIDATION.md)
for policy outcomes and [EKALAYAVA_FINAL_SL_TARGET_DECISION.md](./EKALAYAVA_FINAL_SL_TARGET_DECISION.md)
for the decision.
