# NIFTY Groww Pure Learning Engine v001

## Purpose
Research, analysis and paper simulation only. No order placement, modification or cancellation code exists.

## Strategy 1 — Level-to-Level
NIFTY only; CE/PE; 5-minute execution; opening 5-minute high/low; premium below opening low; wait for the first completed green 5-minute candle; paper entry at its close; SL = opening low minus configured 3/4 points; target = opening high; primary observation window 09:15–11:00. A signal closing at/below its configured stop is recorded as skipped because the stop is already breached.

## Strategy 2 — Ekalayava
NIFTY only; CE/PE; 5-minute execution; opening high/low from the 09:15 candle; premium first trades below opening low; a causal swing high is a completed candle high above the prior two highs; a later completed candle must have both high and close above that swing reference while its high remains below the opening high; entry is the breakout candle close; target = opening high. The existing stop-loss remains undefined. No mandatory textbook candle.

## Learning
The engine records setup frequency, timing, candle structure, premium movement, swing timing, MFE, MAE, outcomes, CE/PE, ITM rank and expiry context when those fields are available. It uses chronological train/validation rather than random shuffling. The optional classifier is research-only and cannot place orders.

## ITM / expiry
ITM ranks are explicitly 2 and 3 by default. OTM and deeper ITM are excluded. Expiry is not silently invented; research should enumerate Groww's available NIFTY expiries and label results. Set an explicit expiry later if the final strategy needs one.

## Groww authentication
Create `.env` from `.env.example`, then set `GROWW_API_KEY` and exactly one of
`GROWW_API_SECRET` or `GROWW_TOTP`, according to the credential type configured
for your Groww API key. Never commit `.env` or print access tokens.

## Install
Windows:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Local test
pytest -q
python -m app.main --auth
python -m app.main --smoke
python -m app.main --csv data/raw/sample.csv
python -m app.main --history data/raw/nifty_5m.csv

## Requested-period baseline

Run the deterministic paper-only baseline over explicitly selected underlying and option data sources:

```powershell
python -m app.period_research `
  --start 2026-04-25 --end 2026-09-25 `
  --underlying data/runs/2026-07-20_2026-08-18/nifty_5m.csv `
  --underlying data/runs/canonical_two_months_20260923_151545/nifty_5m.csv `
  --underlying data/raw/nifty_5m.csv `
  --underlying data/raw/live_2026-09-21_2026-09-23/nifty_5m.csv `
  --underlying data/raw/live_2026-09-23_nifty_5m.csv `
  --option-dir data/runs/2026-07-20_2026-08-18/options `
  --option-dir data/runs/canonical_two_months_20260923_151545/options `
  --option-dir data/runs/canonical_groww_20260923_145708/options `
  --option-dir data/raw/options `
  --option-dir data/raw/live_2026-09-21_2026-09-23 `
  --option-dir data/raw/live_2026-09-23_options
```

Repeat `--underlying` and `--option-dir` for each source. Later-listed sources take precedence only when timestamps conflict; the source manifest records duplicate and conflicting rows. The runner validates OHLC, combines exact timestamps, and never fills missing intervals. It writes the merged source snapshot under `data/derived/` and a JSON baseline report under `data/reports/`.

The report lists only trading dates present in the source files. It does not treat weekdays without data as confirmed market sessions, and it will not label incomplete data as a complete five-month result. Historical downloads require Groww credentials in environment variables or `.env`; missing dates and contracts remain unavailable until downloaded through the read-only API.

## Bounded AI research agent
The autonomous loop uses a real, configurable LLM and never substitutes a
hard-coded response. Configure `RESEARCH_LLM_PROVIDER` (`openai`,
`openai-compatible`, or `anthropic`), `RESEARCH_LLM_API_KEY`, and optionally
`RESEARCH_LLM_MODEL`, `RESEARCH_LLM_BASE_URL`, `RESEARCH_LLM_TEMPERATURE`, and
`RESEARCH_LLM_MAX_TOKENS`. Keep these values in the environment; never commit
them. Run one bounded experiment with:

python -m app.research_agent --autonomous --max-experiments 1

Without provider configuration the command stops before research and reports
the missing variables. Use `--status` to inspect the latest checkpoint.

## Groww Cloud
Upload the project or copy the relevant script into the Groww Strategy environment. Use only secure credential fields if Groww provides them. Do not hardcode secrets. Use paper/observation settings only.

Suggested fields:
- Strategy name: NIFTY Learning - Paper Only
- Runtime: Python, if offered
- Code: app/groww_strategy_script.py
- Execution/order permission: OFF
- Credentials: Groww secure credential mechanism, if offered
- Trigger: 5-minute candle/event trigger, if offered
- Quantity/capital: none; this build does not place orders

If the UI contains an unfamiliar field, do not guess; verify its current meaning first.

## Hard lock
EXECUTION_ALLOWED=false and PAPER_ONLY=true are mandatory. The learning build intentionally contains no place_order/modify_order/cancel_order call.

## Security
Rotate any credential that was exposed. Do not store real API secrets in source code.
