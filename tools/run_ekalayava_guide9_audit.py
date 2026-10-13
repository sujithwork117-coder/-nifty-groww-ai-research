"""Audit the fixed B2 trailing proxy on exact paths and cost sensitivities."""

from __future__ import annotations

import csv
from datetime import time
import json
import math
from pathlib import Path
import statistics

import pandas as pd

from app.groww_data import validate_candles
from app.research_ekalayava_exits import simulate_ekalayava_exit


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SOURCE_ROWS = REPORTS / "ekalayava_guide8_candidate_trade_outcomes.csv"
SUMMARY_INPUT = REPORTS / "ekalayava_guide8_reconciliation_summary.json"
AUDIT_CSV = REPORTS / "ekalayava_guide9_b2_trailing_proxy_trade_audit.csv"
COST_CSV = REPORTS / "ekalayava_guide9_cost_sensitivity.csv"
AUDIT_REPORT = REPORTS / "EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md"
DATA_COVERAGE_REPORT = REPORTS / "EKALAYAVA_FINAL_EVIDENCE_AND_DATA_COVERAGE.md"
READINESS_REPORT = REPORTS / "EKALAYAVA_PAPER_TRADING_READINESS.md"
SUMMARY_OUTPUT = REPORTS / "ekalayava_guide9_b2_trailing_proxy_summary.json"
POLICY_ID = "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1"
IST = "Asia/Kolkata"
SESSION_START = time(9, 15)
SESSION_END = time(15, 25)
COST_SCENARIOS = (0.0, 0.25, 0.5, 1.0, 2.0)

AUDIT_FIELDS = [
    "dataset", "period", "date", "setup_id", "symbol", "path_status",
    "option_type", "itm_rank", "simulation_attempted", "outcome", "reason",
    "entry_timestamp_utc",
    "entry", "initial_stop", "target", "exit_timestamp", "points",
    "holding_minutes", "mfe_points", "mae_points", "first_bar_low_below_entry",
    "stop_within_5_minutes", "stop_within_15_minutes",
    "stop_updates_json", "stop_never_widened", "last_update_active_from",
    "updates_before_exit", "active_stop_at_exit", "stop_exit_after_trail",
    "gap_stop",
    "target_touch_class", "target_touch_timestamp", "replay_matches",
    "source_path",
]


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _float_or_none(value: object) -> float | None:
    if value in ("", None):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _timestamp_equal(left: object, right: object) -> bool:
    if left in ("", None) or right in ("", None):
        return left in ("", None) and right in ("", None)
    return pd.Timestamp(left).tz_convert("UTC") == pd.Timestamp(right).tz_convert("UTC")


def _max_drawdown(values: list[float]) -> float:
    equity = peak = drawdown = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    return drawdown


def _longest_losing_streak(values: list[float]) -> int:
    current = longest = 0
    for value in values:
        current = current + 1 if value < 0 else 0
        longest = max(longest, current)
    return longest


def _net_metrics(rows: list[dict], cost_points: float) -> dict:
    points = [float(row["points"]) - cost_points for row in rows]
    wins = [value for value in points if value > 0]
    losses = [value for value in points if value < 0]
    negative_total = abs(sum(losses))
    return {
        "resolved_trades": len(points),
        "round_trip_cost_points": cost_points,
        "gross_points": sum(float(row["points"]) for row in rows),
        "net_points_scenario": sum(points),
        "net_expectancy_per_trade_scenario": (
            statistics.mean(points) if points else None
        ),
        "net_win_rate_scenario": len(wins) / len(points) if points else None,
        "net_profit_factor_scenario": (
            sum(wins) / negative_total if negative_total
            else (None if not wins else math.inf)
        ),
        "net_max_drawdown_scenario": _max_drawdown(points),
        "net_longest_losing_streak_scenario": _longest_losing_streak(points),
    }


def _bars_for(row: dict[str, str]) -> tuple[pd.DataFrame, list[dict]]:
    relative_path = row["source_path"]
    source = ROOT / relative_path
    if not source.is_file():
        raise FileNotFoundError(f"Exact source path is unavailable: {relative_path}")
    frame = validate_candles(pd.read_csv(source))
    if source.stem != row["symbol"]:
        raise ValueError(f"Source symbol does not match ledger symbol: {relative_path}")
    local = frame["timestamp"].dt.tz_convert(IST)
    same_session = frame.loc[
        (local.dt.strftime("%Y-%m-%d") == row["date"])
        & (local.dt.time >= SESSION_START)
        & (local.dt.time <= SESSION_END)
    ].sort_values("timestamp")
    bars = [
        {
            "timestamp": item.timestamp.to_pydatetime(),
            "open": float(item.open), "high": float(item.high),
            "low": float(item.low), "close": float(item.close),
        }
        for item in same_session.itertuples()
    ]
    return same_session, bars


def _audit_row(row: dict[str, str]) -> dict:
    base = {
        "dataset": row["dataset"],
        "period": row["period"],
        "date": row["date"],
        "setup_id": row["setup_id"],
        "symbol": row["symbol"],
        "path_status": row["path_status"],
        "option_type": row["option_type"],
        "itm_rank": row["itm_rank"],
        "simulation_attempted": row["simulation_attempted"],
        "outcome": row["outcome"],
        "reason": row["reason"],
        "entry_timestamp_utc": row["entry_timestamp_utc"],
        "initial_stop": row["initial_stop"],
        "target": row["target"],
        "target_touch_class": row["target_touch_class"],
        "target_touch_timestamp": row["target_touch_timestamp"],
        "source_path": row["source_path"],
        "replay_matches": "",
        "stop_never_widened": "",
        "updates_before_exit": "",
        "first_bar_low_below_entry": "",
        "stop_within_5_minutes": "",
        "stop_within_15_minutes": "",
        "stop_exit_after_trail": "",
        "gap_stop": "",
        "stop_updates_json": "",
        "last_update_active_from": "",
        "active_stop_at_exit": "",
        "entry": "",
        "exit_timestamp": row["exit_timestamp"],
        "points": row["points"],
        "holding_minutes": "",
        "mfe_points": "",
        "mae_points": "",
    }
    if row["simulation_attempted"].lower() != "true":
        return base

    session, bars = _bars_for(row)
    entry_stamp = pd.Timestamp(row["entry_timestamp_utc"]).tz_convert("UTC")
    entry_bars = session.loc[session["timestamp"].eq(entry_stamp)]
    if len(entry_bars) != 1:
        raise ValueError(
            f"Expected one exact entry candle for {row['setup_id']}; "
            f"found {len(entry_bars)}"
        )
    entry = float(entry_bars.iloc[0]["close"])
    expected_last = pd.Timestamp(
        f"{row['date']} 15:25", tz=IST,
    ).to_pydatetime()
    replay = simulate_ekalayava_exit(
        bars,
        entry_timestamp=entry_stamp.to_pydatetime(),
        entry=entry,
        initial_stop=float(row["initial_stop"]),
        target=float(row["target"]),
        expected_last_timestamp=expected_last,
        trailing=True,
        trail_buffer=2.0,
    )
    points_match = (
        replay.get("points") is None and row["points"] == ""
        or replay.get("points") is not None and row["points"] != ""
        and math.isclose(float(replay["points"]), float(row["points"]), abs_tol=1e-8)
    )
    matches = (
        replay["outcome"] == row["outcome"]
        and points_match
        and _timestamp_equal(replay.get("exit_timestamp"), row["exit_timestamp"])
    )
    if not matches:
        raise RuntimeError(f"Guide 9 independent replay mismatch: {row['setup_id']}")

    updates = replay.get("stop_updates", [])
    stop_values = [float(update["new_stop"]) for update in updates]
    never_widened = all(
        current >= previous
        for previous, current in zip(stop_values, stop_values[1:])
    ) and all(value >= float(row["initial_stop"]) for value in stop_values)
    updates_precede_exit = all(
        replay.get("exit_timestamp") is None
        or pd.Timestamp(update["timestamp"])
        < pd.Timestamp(replay["exit_timestamp"])
        for update in updates
    )
    if not never_widened:
        raise RuntimeError(f"Trailing stop widened for {row['setup_id']}")
    if not updates_precede_exit:
        raise RuntimeError(f"Trailing update occurred on/after exit: {row['setup_id']}")

    future = [
        bar for bar in bars
        if pd.Timestamp(bar["timestamp"]) > entry_stamp
    ]
    first_bar = future[0] if future else None
    exit_stamp = (
        pd.Timestamp(replay["exit_timestamp"])
        if replay.get("exit_timestamp") else None
    )
    holding = replay.get("holding_minutes")
    initial_stop = float(row["initial_stop"])
    active_stop = replay.get("active_stop_at_exit")
    base.update({
        "entry": entry,
        "exit_timestamp": replay.get("exit_timestamp") or "",
        "points": replay.get("points") if replay.get("points") is not None else "",
        "holding_minutes": holding if holding is not None else "",
        "mfe_points": replay.get("mfe_through_terminal_bar", ""),
        "mae_points": replay.get("mae_through_terminal_bar", ""),
        "first_bar_low_below_entry": (
            first_bar is not None and float(first_bar["low"]) < entry
        ),
        "stop_within_5_minutes": (
            replay["outcome"] == "STOP_LOSS" and holding is not None
            and holding <= 5
        ),
        "stop_within_15_minutes": (
            replay["outcome"] == "STOP_LOSS" and holding is not None
            and holding <= 15
        ),
        "stop_updates_json": json.dumps(updates, separators=(",", ":")),
        "stop_never_widened": never_widened,
        "last_update_active_from": (
            (
                pd.Timestamp(updates[-1]["timestamp"])
                + pd.Timedelta(5, unit="min")
            ).isoformat()
            if updates else ""
        ),
        "updates_before_exit": updates_precede_exit,
        "active_stop_at_exit": active_stop if active_stop is not None else "",
        "stop_exit_after_trail": (
            replay["outcome"] == "STOP_LOSS"
            and active_stop is not None and active_stop > initial_stop
        ),
        "gap_stop": replay.get("reason") == "gap_through_stop_filled_at_open",
        "replay_matches": True,
    })
    return base


def _ordered_resolved(rows: list[dict]) -> list[dict]:
    return sorted(
        (row for row in rows if row["points"] not in ("", None)),
        key=lambda row: (
            row["date"], row["exit_timestamp"],
            row["entry_timestamp_utc"], row["symbol"],
        ),
    )


def _cost_rows(rows: list[dict]) -> list[dict]:
    out = []
    all_resolved = _ordered_resolved(rows)
    groups = {"COMBINED_EXACT_PATHS": all_resolved}
    for period in sorted({row["period"] for row in all_resolved}):
        groups[period] = _ordered_resolved(
            [row for row in all_resolved if row["period"] == period]
        )
    for period, items in groups.items():
        for cost in COST_SCENARIOS:
            out.append({"period": period, **_net_metrics(items, cost)})
    return out


def _distribution(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "mean": None, "median": None, "p25": None, "p75": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "mean": statistics.mean(ordered),
        "median": statistics.median(ordered),
        "p25": float(pd.Series(ordered).quantile(0.25)),
        "p75": float(pd.Series(ordered).quantile(0.75)),
    }


def _summary(rows: list[dict], costs: list[dict], source_summary: dict) -> dict:
    resolved = _ordered_resolved(rows)
    points = [float(row["points"]) for row in resolved]
    positive = sum(value for value in points if value > 0)
    winners = sorted(
        (row for row in resolved if float(row["points"]) > 0),
        key=lambda row: float(row["points"]), reverse=True,
    )
    stop_rows = [row for row in rows if row["outcome"] == "STOP_LOSS"]
    after_target = [
        row for row in stop_rows
        if row["target_touch_class"] == "TOUCHED_AFTER_EXIT"
    ]
    updates = [row for row in rows if row["stop_updates_json"] not in ("", "[]")]
    entry_keys = [
        (row["date"], row["symbol"], row["entry_timestamp_utc"])
        for row in rows
    ]
    resolved_exit_keys = [
        (row["date"], row["symbol"], row["exit_timestamp"])
        for row in resolved
    ]
    overlapping_positions = 0
    grouped_positions: dict[tuple[str, str], list[dict]] = {}
    for row in resolved:
        grouped_positions.setdefault((row["date"], row["symbol"]), []).append(row)
    for group in grouped_positions.values():
        intervals = sorted(
            (
                pd.Timestamp(row["entry_timestamp_utc"]),
                pd.Timestamp(row["exit_timestamp"]),
            )
            for row in group
        )
        last_exit = None
        for entry_stamp, exit_stamp in intervals:
            if last_exit is not None and entry_stamp < last_exit:
                overlapping_positions += 1
            if last_exit is None or exit_stamp > last_exit:
                last_exit = exit_stamp
    results_by_period = {}
    for period in sorted({row["period"] for row in rows}):
        group = [row for row in rows if row["period"] == period]
        resolved_group = _ordered_resolved(group)
        gross = [float(row["points"]) for row in resolved_group]
        results_by_period[period] = {
            "entries": len(group),
            "resolved": len(resolved_group),
            "target_exits": sum(row["outcome"] == "TARGET" for row in group),
            "stop_exits": sum(row["outcome"] == "STOP_LOSS" for row in group),
            "end_of_session_exits": sum(
                row["outcome"] == "END_OF_SESSION" for row in group
            ),
            "unresolved": sum(row["outcome"].startswith("UNRESOLVED") for row in group),
            "gross_points": sum(gross),
            "mean_gross_points_per_resolved": statistics.mean(gross) if gross else None,
        }
    gross = sum(points)
    return {
        "policy_id": POLICY_ID,
        "rows_in_ledger": len(rows),
        "resolved_exact_path_trades": len(resolved),
        "replay_matches": sum(row["replay_matches"] is True for row in rows),
        "gross_points": gross,
        "mean_gross_points_per_resolved": statistics.mean(points) if points else None,
        "break_even_round_trip_cost_points": gross / len(resolved) if resolved else None,
        "mfe_points": _distribution([
            float(row["mfe_points"]) for row in resolved
            if row["mfe_points"] not in ("", None)
        ]),
        "mae_points": _distribution([
            float(row["mae_points"]) for row in resolved
            if row["mae_points"] not in ("", None)
        ]),
        "stopped_out": len(stop_rows),
        "duplicate_entry_observation_extras": (
            len(entry_keys) - len(set(entry_keys))
        ),
        "duplicate_exit_timestamp_extras": (
            len(resolved_exit_keys) - len(set(resolved_exit_keys))
        ),
        "overlapping_same_contract_positions": overlapping_positions,
        "stops_with_observed_opening_high_touch_after_exit": len(after_target),
        "stops_with_observed_opening_high_touch_after_exit_rate": (
            len(after_target) / len(stop_rows) if stop_rows else None
        ),
        "stops_within_5_minutes": sum(
            row["stop_within_5_minutes"] is True for row in rows
        ),
        "stops_within_15_minutes": sum(
            row["stop_within_15_minutes"] is True for row in rows
        ),
        "stops_after_trailing_update": sum(
            row["stop_exit_after_trail"] is True for row in rows
        ),
        "gap_stop_exits": sum(row["gap_stop"] is True for row in rows),
        "trades_with_trail_updates": len(updates),
        "all_stop_updates_monotonic": all(
            row["stop_never_widened"] is True for row in updates
        ),
        "top_winners": [
            {
                "date": row["date"], "period": row["period"],
                "symbol": row["symbol"], "points": float(row["points"]),
                "setup_id": row["setup_id"],
            }
            for row in winners[:10]
        ],
        "top_5_share_of_positive_points": (
            sum(float(row["points"]) for row in winners[:5]) / positive
            if positive else None
        ),
        "periods": results_by_period,
        "cost_scenarios": costs,
        "data_coverage": {
            key: source_summary[key] for key in (
                "entry_observations_2025", "entry_observations_2026",
                "exact_2025_complete_paths", "exact_2025_partial_paths",
                "exact_2026_paths", "2026_missing_exact_paths",
            )
        },
        "coverage_by_dataset_period_type_rank_status": _coverage_groups(rows),
        "execution_allowed": False,
        "paper_only": True,
        "orders_submitted": False,
    }


def _coverage_groups(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str, str, str], int] = {}
    for row in rows:
        key = (
            row["dataset"], row["period"], row.get("option_type", ""),
            row.get("itm_rank", ""), row["path_status"],
        )
        groups[key] = groups.get(key, 0) + 1
    return [
        {
            "dataset": key[0], "period": key[1], "option_type": key[2],
            "itm_rank": key[3], "path_status": key[4], "entries": count,
        }
        for key, count in sorted(groups.items())
    ]


def _write_report(summary: dict) -> None:
    periods = summary["periods"]
    cost_scenarios = [
        row for row in summary["cost_scenarios"]
        if row["period"] == "COMBINED_EXACT_PATHS"
    ]
    candidate_counts = _read_rows(
        REPORTS / "ekalayava_guide8_candidate_counts.csv",
    )
    overall_candidates = [
        row for row in candidate_counts
        if row["period"] == "COMBINED_2025_H2_2026_LEDGER"
    ]
    gross_leader = max(
        overall_candidates, key=lambda row: float(row["gross_points"]),
    )
    lines = [
        "# Guide 9 — B2 Trailing-Proxy Trade-Path Audit",
        "",
        "## Conclusion",
        "",
        "**No exit policy is approved.** The B2 lower-low trailing proxy is",
        "audited here because it was the previous gross leader. Following",
        "recovery of the missing 2026 paths, it is no longer the highest",
        f"combined-gross candidate: `{gross_leader['policy_id']}` at "
        f"{float(gross_leader['gross_points']):.2f} points. No candidate has",
        "demonstrated stable net expectancy. This audit reruns",
        "the fixed policy on its exact available paths and does not change its",
        "rules or select a new policy.",
        "",
        "## Candidate rule and scope",
        "",
        "Initial stop = causal structural trough − 2 premium points; target =",
        "Opening High; after a completed candle makes a lower low than the",
        "previous two completed lows, the proposed stop is that candle low − 2;",
        "the stop only tightens and is active on the next five-minute candle.",
        "It is a lower-low proxy, not a right-side-confirmed pivot rule.",
        "Candidate outcomes use completed OHLC bars, existing gap and",
        "same-bar-ambiguity conventions, and experimental session-end exits.",
        "",
        "## Available data and reproducibility",
        "",
        f"* 2025 H2 entries: {summary['data_coverage']['entry_observations_2025']};",
        f"  {summary['data_coverage']['exact_2025_complete_paths']} complete and",
        f"  {summary['data_coverage']['exact_2025_partial_paths']} partial exact paths.",
        f"* Saved 2026 entries: {summary['data_coverage']['entry_observations_2026']};",
        f"  {summary['data_coverage']['exact_2026_paths']} exact paths after the",
        f"  Guide 9 recovery attempt; {summary['data_coverage']['2026_missing_exact_paths']}",
        "  entries remain without exact paths.",
        f"* Exact-path trades matched in a separate audit replay: "
        f"{summary['replay_matches']}/",
        f"  {summary['resolved_exact_path_trades']}.",
        "",
        "Run `.venv/bin/python -m tools.run_ekalayava_guide8_reconciliation`",
        "followed by `.venv/bin/python -m tools.run_ekalayava_guide9_audit`.",
        "The detailed audit rows are in",
        "`ekalayava_guide9_b2_trailing_proxy_trade_audit.csv`.",
        "",
        "## Period outcomes on exact paths",
        "",
        "| Period | Entries | Resolved | Target | Stop | EOD | Unresolved | Gross points | Mean gross / resolved |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for period, item in periods.items():
        lines.append(
            f"| {period} | {item['entries']} | {item['resolved']} | "
            f"{item['target_exits']} | {item['stop_exits']} | "
            f"{item['end_of_session_exits']} | {item['unresolved']} | "
            f"{item['gross_points']:.2f} | "
            f"{item['mean_gross_points_per_resolved']:.3f} |"
        )
    lines.extend([
        "",
        "## Trade-path diagnostics",
        "",
        f"* MFE mean/median: {summary['mfe_points']['mean']:.2f} / "
        f"{summary['mfe_points']['median']:.2f} points; MAE mean/median: "
        f"{summary['mae_points']['mean']:.2f} / "
        f"{summary['mae_points']['median']:.2f} points, measured through each",
        "  simulated terminal bar. OHLC extremes within the terminal bar are",
        "  not ordered; these are excursions, not executable path sequencing.",
        f"* Stops within 5 minutes: {summary['stops_within_5_minutes']}; within",
        f"  15 minutes: {summary['stops_within_15_minutes']}; stops after a",
        f"  trailing update: {summary['stops_after_trailing_update']};",
        f"  gap-through-stop exits: {summary['gap_stop_exits']}.",
        f"* Trades with at least one trail update: {summary['trades_with_trail_updates']};",
        f"  every recorded update was monotonic: {summary['all_stop_updates_monotonic']}.",
        f"* Stop exits followed by an observed later Opening-High touch:",
        f"  {summary['stops_with_observed_opening_high_touch_after_exit']}/",
        f"  {summary['stopped_out']} stops. This is a counterfactual path",
        "  diagnostic, never counted as an actual target exit.",
        f"* The top five winners contributed",
        f"  {summary['top_5_share_of_positive_points']:.1%} of positive trade points.",
        f"* Duplicate entry observations: {summary['duplicate_entry_observation_extras']};",
        f"  duplicate exit timestamps: {summary['duplicate_exit_timestamp_extras']};",
        f"  overlapping same-contract positions: "
        f"{summary['overlapping_same_contract_positions']}.",
        "  See the audit CSV for every entry, path, excursion, stop update and",
        "  whether the independently repeated outcome matched.",
        "",
        "## Hypothetical transaction-cost sensitivity",
        "",
        "No actual fee, spread, slippage, tax, fill, contract multiplier or",
        "position-size input is configured. The following values are explicitly",
        "scenarios in premium points per completed round trip, not Groww fee",
        "estimates or rupee returns.",
        "",
        "| Scenario cost (points/trade) | Resolved trades | Gross points | Scenario net points | Scenario expectancy | PF | Max DD |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in cost_scenarios:
        pf = row["net_profit_factor_scenario"]
        pf_text = "n/a" if pf is None else "∞" if math.isinf(pf) else f"{pf:.3f}"
        lines.append(
            f"| {row['round_trip_cost_points']:.2f} | {row['resolved_trades']} | "
            f"{row['gross_points']:.2f} | {row['net_points_scenario']:.2f} | "
            f"{row['net_expectancy_per_trade_scenario']:.3f} | {pf_text} | "
            f"{row['net_max_drawdown_scenario']:.2f} |"
        )
    lines.extend([
        "",
        f"Uniform round-trip cost reaches gross break-even at approximately "
        f"{summary['break_even_round_trip_cost_points']:.3f} premium points per",
        "resolved trade. This threshold does not establish whether real costs",
        "are below it. The historical test segment is already retrospective;",
        "its gross contribution is too small to tolerate meaningful costs.",
        "",
        "## Interpretation and decision",
        "",
        "The exact-path results show both early adverse movement and frequent",
        "trailing exits; neither alone proves the entry or stop is defective.",
        "An observed later target touch after a stop cannot justify holding",
        "through the stop. The proxy was implemented consistently on this",
        "replay, but no new structural pivot variant is promoted: the sample",
        "does not support a fair selection, test results are retrospective, and",
        "net costs are unmeasured. Keep the canonical exit unresolved and",
        "do not connect this candidate to the paper engine.",
        "",
        "Execution safety: `EXECUTION_ALLOWED=False`, `PAPER_ONLY=True`; no",
        "orders were submitted.",
        "",
    ])
    AUDIT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    _write_coverage_report(summary)
    _write_readiness_report()


def _write_coverage_report(summary: dict) -> None:
    recovery_path = ROOT / "data/derived/ekalayava_guide9_2026_groww/manifest.json"
    recovery = (
        json.loads(recovery_path.read_text(encoding="utf-8"))
        if recovery_path.is_file() else {}
    )
    requests = recovery.get("requests", [])
    data_responses = sum(row.get("status") == "DATA" for row in requests)
    empty_responses = sum(row.get("status") == "EMPTY" for row in requests)
    stopped = recovery.get("stopped_after_error")
    lines = [
        "# Ekalayava Final Evidence and Data Coverage",
        "",
        "## Verified local inventory",
        "",
        "The 2025 H2 exact-option data came from the bounded Groww catalog-first",
        "retrieval recorded in `data/derived/ekalayava_2025_h2_groww/manifest.json`.",
        "Its 492 selected contract-session paths comprise 488 complete and 4",
        "partial sessions; the unchanged canonical detector produced 194",
        "qualifying Ekalayava entries with 192 complete and 2 partial exact paths.",
        "These include 61 training, 64 validation and 69 historical-test entries.",
        "",
        "The saved 2026 ledger has 253 entry observations across Jan–September",
        "2026. A one-time, read-only recovery attempt requested only the exact",
        "symbol/date sessions missing from that ledger, with no retries or",
        "substitutions.",
        "",
        f"* Planned recovery requests: {recovery.get('request_count_planned', 0)}.",
        f"* Completed requests: {len(requests)}; data responses: {data_responses};",
        f"  empty responses: {empty_responses}.",
        (
            f"* Recovery stopped after {stopped.get('requests_completed', 0)} "
            f"requests due to `{stopped.get('exception_type')}` for "
            f"{stopped.get('symbol')} on {stopped.get('date')}; it was not retried."
            if stopped else "* Recovery completed without an API exception."
        ),
        "",
        "## Entry-path status by period, contract type and ITM rank",
        "",
        "| Dataset | Period | Type | ITM rank | Path status | Entries |",
        "|---|---|---|---:|---|---:|",
    ]
    for row in summary["coverage_by_dataset_period_type_rank_status"]:
        lines.append(
            f"| {row['dataset']} | {row['period']} | {row['option_type'] or 'n/a'} | "
            f"{row['itm_rank'] or 'n/a'} | {row['path_status']} | {row['entries']} |"
        )
    lines.extend([
        "",
        "Path status uses exact contract symbol, saved entry timestamp, and",
        "five-minute continuity through the simulator's terminal point. A",
        "complete path has the session candles needed for a same-day replay;",
        "partial paths are not extended or interpolated. Any no-path or",
        "invalid/mismatched entries remain unresolved or excluded and are not",
        "counted as wins or losses.",
        "",
        "## Integrity and limitations",
        "",
        f"* Duplicate saved entry observations beyond exact date/symbol/time keys:",
        f"  {summary['duplicate_entry_observation_extras']}.",
        f"* Duplicate resolved exit timestamps for the same date and contract:",
        f"  {summary['duplicate_exit_timestamp_extras']}.",
        f"* Overlapping resolved positions in the same contract/date:",
        f"  {summary['overlapping_same_contract_positions']}. The equal-event",
        "  sequence is not a capital-weighted portfolio simulation.",
        "* The saved historical entry ledger contains qualifying entries, not",
        "  every rejected pre-entry setup; skipped-setup counts cannot be inferred.",
        "* A recovered 2026 candle path validates a price path for the saved",
        "  contract and timestamp; it does not independently re-run and verify",
        "  every historical entry decision.",
        "* All option data are OHLC bars. OHLC cannot establish intrabar order",
        "  or executable limit fills, and partial data can conceal excursions.",
        "* Fees, taxes, spread, slippage, lot multipliers and account sizing are",
        "  not configured as reliable historical inputs. Gross premium points",
        "  are not rupee returns.",
        "* Previously inspected 2025 test outcomes and archived 2026 policy",
        "  summaries make these candidate comparisons retrospective, not a",
        "  genuinely untouched out-of-sample selection.",
        "",
        "The complete B2 row-level replay and cost sensitivity are in",
        "`EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md` and",
        "`ekalayava_guide9_b2_trailing_proxy_trade_audit.csv`.",
        "",
    ])
    DATA_COVERAGE_REPORT.write_text("\n".join(lines), encoding="utf-8")


def _write_readiness_report() -> None:
    READINESS_REPORT.write_text(
        """# Ekalayava Paper-Trading Readiness

## Status: not ready to activate an exit policy

**No experimental stop/target policy is approved.** Keep canonical entry
behavior unchanged; do not connect any candidate exit lifecycle to the
paper engine. `EXECUTION_ALLOWED=False` and `PAPER_ONLY=True` remain required.
No live, paper, or broker orders are submitted by this research workflow.

The B2 lower-low proxy is audited as the previous gross leader, not the
current combined-gross leader, and is not a validated net-profit policy.
`A_B4_OPENING_HIGH_V1` now leads descriptively at +685.55 gross points; its
2025 training and validation results were negative, so it is not approved.
The B2 exact stop and target counts, path-level replays, period performance
and hypothetical transaction-cost scenarios are reported in
`EKALAYAVA_GUIDE9_B2_TRAILING_PROXY_AUDIT.md`. Its lower-low rule is not a
confirmed structural swing-low rule.

## Why activation is blocked

* The candidate comparisons and 2025 test have already been examined; the
  results are retrospective and cannot serve as a fresh selection holdout.
* Even with exact recovered candles, fills are approximated from OHLC. Actual
  bid/ask spreads, queue position, slippage, brokerage, taxes and executable
  contract multipliers are not reliably available in the historical files.
* The research does not prove stable net expectancy across independent
  periods, and the cost threshold for positive gross performance is not a
  measured transaction-cost estimate.
* No selected deterministic exit is synchronized with the paper engine.

## Supervised paper-observation plan (observation only)

Collect a consecutive, predeclared sample of at least 100 qualifying signals
over at least 60 trading sessions, whichever takes longer. This is a minimum
observation horizon to prevent stopping when the first results look favorable;
it is not a statistical guarantee, approval threshold, or authorization to
trade. Do not discard losing, incomplete, or inconvenient observations.
Capture quotes/fills and explicit costs only in a supervised paper environment.

For every observed signal, record:

| Field | Required observation |
|---|---|
| Identity | Date, canonical setup ID, exact option symbol, expiry, strike, CE/PE and ITM rank |
| Entry context | Entry timestamp, entry price, first-candle Opening High/Low, breakdown time, causal swing-high time/price, structural trough |
| Candidate snapshot | Candidate name/version, initial stop, target, formula and predeclared assumptions; store as diagnostics only |
| Path | Every completed five-minute timestamp and OHLC from entry through the observed terminal point; mark gaps and duplicates |
| Management | Each stop update, source candle, computed stop, and the first candle on which it is eligible to act |
| Execution evidence | Bid/ask or executable paper quote, simulated fill, spread, slippage, brokerage/tax inputs and source |
| Terminal outcome | Exit timestamp, observed price, exit reason, whether a target was touched while open or only after exit |
| Integrity | Exact-contract validation, missing intervals, ambiguous OHLC ordering, source and retrieval timestamp |

Before any future candidate selection, freeze its formula, selection process,
cost model and evaluation criteria. Keep the existing canonical entry and
paper-engine safety controls unchanged. A paper observation records evidence;
it does not activate the candidate's stop or target.

## Safety and code boundary

Research simulators remain separate from the paper engine. Experimental exit
configuration remains disabled unless separately and explicitly authorized
after a new evidence review. Do not enable live execution, place/modify/cancel
orders, weaken authentication or duplicate-signal protection, or use an empty
account balance as a safety control.
""",
        encoding="utf-8",
    )


def main() -> None:
    for path in (SOURCE_ROWS, SUMMARY_INPUT):
        if not path.is_file():
            raise FileNotFoundError(f"Required Guide 8 artifact is missing: {path}")
    source_rows = [
        row for row in _read_rows(SOURCE_ROWS)
        if row["policy_id"] == POLICY_ID
    ]
    audited = [_audit_row(row) for row in source_rows]
    if len(audited) != 447:
        raise RuntimeError(f"Expected 447 B-policy ledger rows, got {len(audited)}")
    if any(row["replay_matches"] is not True for row in audited
           if row["simulation_attempted"].lower() == "true"):
        raise RuntimeError("Not all simulated B-policy outcomes independently matched")
    costs = _cost_rows(audited)
    source_summary = json.loads(SUMMARY_INPUT.read_text(encoding="utf-8"))
    summary = _summary(audited, costs, source_summary)
    _write_csv(AUDIT_CSV, AUDIT_FIELDS, audited)
    _write_csv(COST_CSV, list(costs[0]), costs)
    SUMMARY_OUTPUT.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    _write_report(summary)
    print(json.dumps({
        "policy_id": POLICY_ID,
        "ledger_rows": len(audited),
        "simulated_rows": summary["resolved_exact_path_trades"],
        "replay_matches": summary["replay_matches"],
        "gross_points": summary["gross_points"],
        "break_even_round_trip_cost_points": summary[
            "break_even_round_trip_cost_points"
        ],
        "execution_allowed": False,
        "paper_only": True,
        "orders_submitted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
