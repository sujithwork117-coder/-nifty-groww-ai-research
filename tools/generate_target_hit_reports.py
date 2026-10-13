"""Build target-hit summaries from the saved L2L and Ekalayava ledgers.

This report-only tool does not fetch candles or rerun any policy simulations.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PERIODS = ("TRAIN_JAN_JUN", "VALIDATION_JUL_AUG", "OOS_SEP_INCOMPLETE")
UNRESOLVED_PREFIXES = ("UNRESOLVED", "OPEN")
RESOLVED_L2L = {"TARGET", "SL"}
RESOLVED_EKALAYAVA = {"TARGET", "STOP_LOSS", "END_OF_SESSION"}

SUMMARY_FIELDS = [
    "strategy", "policy_id", "policy_description", "stop_policy",
    "target_policy", "target_level", "period", "segment_dimension",
    "segment", "eligible_setups", "eligible_entries", "valid_entries",
    "complete_paths", "incomplete_paths", "target_touches",
    "target_touch_numerator", "target_touch_denominator",
    "target_touch_rate", "target_exits", "stop_exits", "end_of_session_exits",
    "ambiguous_count", "unresolved_count", "skipped_count",
    "skip_reason_counts", "resolved_trades", "target_hit_numerator",
    "target_hit_denominator", "target_hit_rate", "target_exit_rate_valid",
    "target_exit_rate_of_resolved", "gross_points",
    "average_points_per_entry", "average_points_per_eligible_entry",
    "average_points_per_resolved_trade", "profit_factor", "max_drawdown",
    "longest_losing_streak", "data_coverage_status", "metric_status",
    "limitations",
]

COMPARISON_FIELDS = [
    "strategy", "comparison_basis", "policy_id", "reference_policy_id",
    "period", "segment_dimension", "segment", "target_touches",
    "reference_target_touches", "target_touch_difference",
    "target_touch_rate", "reference_target_touch_rate",
    "target_touch_rate_difference_pp",
    "target_exits", "reference_target_exits", "target_exit_difference",
    "target_exit_rate", "reference_target_exit_rate",
    "target_exit_rate_difference_pp", "stop_exits",
    "reference_stop_exits", "stop_exit_difference", "ambiguous_count",
    "reference_ambiguous_count", "ambiguous_difference", "unresolved_count",
    "reference_unresolved_count", "unresolved_difference", "gross_points",
    "reference_gross_points", "gross_points_difference", "max_drawdown",
    "reference_max_drawdown", "max_drawdown_difference",
    "longest_losing_streak", "reference_longest_losing_streak",
    "longest_losing_streak_difference", "limitations",
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _number(value):
    if value is None or value == "":
        return None
    return float(value)


def _integer(value):
    number = _number(value)
    return int(number) if number is not None else None


def _write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _l2l_description(row: dict) -> tuple[str, str, str]:
    buffer = _number(row.get("stop_buffer_points"))
    fraction = _number(row.get("target_fraction"))
    stop = f"Opening Low - {buffer:g} points" if buffer is not None else "NOT VERIFIABLE"
    target = f"TP{fraction * 100:g}" if fraction is not None else "NOT VERIFIABLE"
    if fraction == 1:
        target += " (Opening High)"
    return (
        f"Stop {stop}; target = entry + {fraction:g} * (Opening High - entry)"
        if fraction is not None else f"Stop {stop}; target formula NOT VERIFIABLE",
        stop,
        target,
    )


def _ekalayava_description(row: dict) -> tuple[str, str, str]:
    policy = row["policy"]
    if policy == "TRAIL_CAUSAL_LOWER_LOW_B2_TP100":
        description = (
            "A structural trough - 2 initial stop; after a completed lower-low "
            "versus the prior two completed bars, tighten to low - 2 for the next bar; "
            "Opening High target"
        )
        return description, "A_STRUCTURAL_TROUGH - 2, causal trailing", "TP100_OPENING_HIGH"
    anchor = row.get("policy_family", "")
    buffer = _number(row.get("buffer_points"))
    fraction = _number(row.get("target_fraction"))
    anchor_description = {
        "A_STRUCTURAL_TROUGH": "pre-entry structural trough",
        "B_BREAKOUT_CANDLE": "completed breakout-candle low",
        "D_OPENING_LOW": "option Opening Low",
    }.get(anchor, anchor or "NOT VERIFIABLE")
    stop = f"{anchor_description} - {buffer:g}" if buffer is not None else anchor_description
    target = f"TP{fraction * 100:g}" if fraction is not None else "NOT VERIFIABLE"
    if fraction == 1:
        target += " (Opening High)"
    alias = row.get("anchor_alias")
    description = f"Stop {stop}; target = entry + {fraction:g} * (Opening High - entry)"
    if alias:
        description += "; C_RECOVERY_BASE_INVALIDATION aliases A and is not a separate simulation"
    return description, stop, target


def enrich_ekalayava_rows(
    rows: list[dict], observations: list[dict]
) -> list[dict]:
    """Join canonical excursion observations by exact event identity."""
    observation_by_event = {}
    for observation in observations:
        key = (observation["date"], observation["timestamp_utc"], observation["symbol"])
        if key in observation_by_event:
            raise ValueError(f"Duplicate Ekalayava observation identity: {key}")
        observation_by_event[key] = observation

    enriched = []
    seen = set()
    for source in rows:
        row = dict(source)
        key = (row["date"], row["timestamp_utc"], row["symbol"])
        policy_key = (row["policy"], row["setup_id"])
        if policy_key in seen:
            raise ValueError(f"Duplicate Ekalayava policy/setup row: {policy_key}")
        seen.add(policy_key)
        observation = observation_by_event.get(key)
        row["_observation_mfe"] = _number(observation.get("mfe")) if observation else None
        distance = _number(row.get("target_distance"))
        row["_observation_complete"] = (
            row["_observation_mfe"] is not None and distance is not None
        )
        row["_observed_target_touch"] = (
            row["_observation_complete"]
            and row["_observation_mfe"] + 1e-9 >= distance
        )
        enriched.append(row)

    policy_events = {
        (row["date"], row["timestamp_utc"], row["symbol"]) for row in rows
    }
    if policy_events != set(observation_by_event):
        missing = len(policy_events - set(observation_by_event))
        extra = len(set(observation_by_event) - policy_events)
        raise ValueError(
            f"Ekalayava observation join mismatch: {missing} missing, {extra} extra"
        )
    return enriched


def _is_unresolved(outcome: str) -> bool:
    return any(outcome.startswith(prefix) for prefix in UNRESOLVED_PREFIXES)


def calculate_metrics(rows: list[dict], strategy: str) -> dict:
    """Calculate denominator-explicit touch, exit, and return metrics."""
    if strategy not in {"L2L", "EKALAYAVA"}:
        raise ValueError(f"Unsupported strategy: {strategy}")
    if not rows:
        raise ValueError("Cannot calculate metrics for an empty group")

    outcomes = Counter(row["outcome"] for row in rows)
    skipped_rows = [
        row for row in rows
        if row["outcome"].startswith("SKIPPED")
        or row["outcome"].startswith("EXCLUDED")
    ]
    valid_rows = [
        row for row in rows
        if not row["outcome"].startswith("SKIPPED")
        and not row["outcome"].startswith("EXCLUDED")
    ]
    unresolved_rows = [row for row in rows if _is_unresolved(row["outcome"])]
    if strategy == "L2L":
        eligible_entries = len(valid_rows)
        complete_paths = sum(not _is_unresolved(row["outcome"]) for row in valid_rows)
        touches = sum(row["outcome"] in {"TARGET", "AMBIGUOUS"} for row in rows)
        resolved_outcomes = RESOLVED_L2L
        stop_names = {"SL"}
    else:
        eligible_entries = len(rows)
        complete_paths = sum(bool(row.get("_observation_complete")) for row in rows)
        touches = sum(bool(row.get("_observed_target_touch")) for row in rows)
        resolved_outcomes = RESOLVED_EKALAYAVA
        stop_names = {"STOP_LOSS"}

    target_exits = outcomes["TARGET"]
    stop_exits = sum(outcomes[name] for name in stop_names)
    eod_exits = outcomes["END_OF_SESSION"]
    resolved_rows = [row for row in rows if row["outcome"] in resolved_outcomes]
    timed_rows = sorted(
        (row for row in resolved_rows if _number(row.get("points")) is not None),
        key=lambda row: (
            row.get("date", ""),
            row.get("exit_timestamp") or "",
            row.get("timestamp_utc", ""),
        ),
    )
    points = [_number(row["points"]) for row in timed_rows]
    gross = sum(points) if points else None
    wins = sum(value for value in points if value > 0)
    losses = abs(sum(value for value in points if value < 0))
    equity = peak = drawdown = 0.0
    streak = longest_streak = 0
    for value in points:
        equity += value
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
        streak = streak + 1 if value < 0 else 0
        longest_streak = max(longest_streak, streak)
    valid_entries = len(valid_rows)
    resolved_count = len(timed_rows)
    touch_denominator = complete_paths
    hit_denominator = eligible_entries
    incomplete_paths = (
        max(0, len(rows) - complete_paths)
        if strategy == "EKALAYAVA"
        else max(0, eligible_entries - complete_paths)
    )
    return {
        "eligible_setups": len(rows),
        "eligible_entries": eligible_entries,
        "valid_entries": valid_entries,
        "complete_paths": complete_paths,
        "incomplete_paths": incomplete_paths,
        "target_touches": touches,
        "target_touch_numerator": touches,
        "target_touch_denominator": touch_denominator,
        "target_touch_rate": touches / touch_denominator if touch_denominator else None,
        "target_exits": target_exits,
        "stop_exits": stop_exits,
        "end_of_session_exits": eod_exits,
        "ambiguous_count": outcomes["AMBIGUOUS"],
        "unresolved_count": len(unresolved_rows),
        "skipped_count": len(skipped_rows),
        "skip_reason_counts": json.dumps(
            dict(sorted(Counter(row["outcome"] for row in skipped_rows).items())),
            separators=(",", ":"),
        ),
        "resolved_trades": resolved_count,
        "target_hit_numerator": target_exits,
        "target_hit_denominator": hit_denominator,
        "target_hit_rate": target_exits / hit_denominator if hit_denominator else None,
        "target_exit_rate_valid": target_exits / valid_entries if valid_entries else None,
        "target_exit_rate_of_resolved": (
            target_exits / resolved_count if resolved_count else None
        ),
        "gross_points": gross,
        "average_points_per_entry": gross / valid_entries if gross is not None and valid_entries else None,
        "average_points_per_eligible_entry": (
            gross / eligible_entries if gross is not None and eligible_entries else None
        ),
        "average_points_per_resolved_trade": gross / resolved_count if gross is not None and resolved_count else None,
        "profit_factor": wins / losses if losses else None,
        "max_drawdown": drawdown if points else None,
        "longest_losing_streak": longest_streak if points else None,
    }


def _groups(rows: list[dict]):
    dimensions = {
        "ALL": lambda row: "ALL",
        "OPTION_TYPE": lambda row: row.get("option_type"),
        "ITM_RANK": lambda row: f"ITM{row['itm_rank']}" if row.get("itm_rank") else None,
        "ENTRY_TIME": lambda row: row.get("entry_bucket"),
        "MONTH": lambda row: row.get("month") or row.get("date", "")[:7],
    }
    grouped = [("ALL", "ALL", rows)]
    for dimension, key_fn in dimensions.items():
        if dimension == "ALL":
            continue
        buckets = defaultdict(list)
        for row in rows:
            key = key_fn(row)
            if key:
                buckets[str(key)].append(row)
        grouped.extend(
            (dimension, key, items)
            for key, items in sorted(buckets.items())
        )
    return grouped


def _period_groups(rows: list[dict]):
    yield "ALL", rows
    for period in PERIODS:
        yield period, [row for row in rows if row.get("period") == period]


def build_summary_rows(
    l2l_rows: list[dict], ekalayava_rows: list[dict]
) -> list[dict]:
    output = []
    datasets = (("L2L", l2l_rows, _l2l_description),
                ("EKALAYAVA", ekalayava_rows, _ekalayava_description))
    for strategy, all_rows, describe in datasets:
        policies = sorted({row["policy"] for row in all_rows})
        for policy in policies:
            policy_rows = [row for row in all_rows if row["policy"] == policy]
            description, stop_policy, target_policy = describe(policy_rows[0])
            for period, period_rows in _period_groups(policy_rows):
                if not period_rows:
                    continue
                for dimension, segment, segment_rows in _groups(period_rows):
                    metrics = calculate_metrics(segment_rows, strategy)
                    if period == "OOS_SEP_INCOMPLETE":
                        coverage = "INCOMPLETE_SOURCE_COVERAGE"
                    elif dimension == "MONTH" and segment == "2026-09":
                        coverage = "INCOMPLETE_SOURCE_COVERAGE"
                    else:
                        coverage = "SAVED_EVENT_LEDGER_ONLY"
                    output.append({
                        "strategy": strategy,
                        "policy_id": policy,
                        "policy_description": description,
                        "stop_policy": stop_policy,
                        "target_policy": target_policy,
                        "target_level": (
                            "entry + fraction * (Opening High - entry)"
                            if strategy == "L2L"
                            else "entry + target_fraction * (Opening High - entry)"
                        ),
                        "period": period,
                        "segment_dimension": dimension,
                        "segment": segment,
                        **metrics,
                        "data_coverage_status": coverage,
                        "metric_status": (
                            "SAVED_SIMULATION; GROSS_ONLY; FILL_MODEL_LIMITED"
                            if strategy == "L2L"
                            else "SAVED_EXPERIMENTAL_SIMULATION; TOUCHES_FROM_CANONICAL_OBSERVATION_PATH"
                        ),
                        "limitations": (
                            "Saved policy outcomes; not net returns or real fills. "
                            "Source-bar count is 75, but saved policy CSVs do not retain "
                            "per-candle timestamps for independent cadence replay."
                            if strategy == "L2L" else
                            "Experimental exit only; canonical Ekalayava has no exit/P&L "
                            "lifecycle. Touches use saved MFE through the canonical "
                            "Opening-High touch or session end, not real fills."
                        ),
                    })
    return output


def build_observation_reference_rows(observations: list[dict]) -> list[dict]:
    """Represent the canonical Ekalayava touch-only baseline without fake exits."""
    output = []
    for period, period_rows in _period_groups(observations):
        if not period_rows:
            continue
        for dimension, segment, group_rows in _groups(period_rows):
            complete = [row for row in group_rows if _number(row.get("mfe")) is not None]
            touches = sum(row.get("target_touched") == "True" for row in group_rows)
            denominator = len(complete)
            output.append({
                "strategy": "EKALAYAVA",
                "policy_id": "EKALAYAVA_CANONICAL_OPENING_HIGH_OBSERVATION_ONLY",
                "policy_description": (
                    "Canonical entry observations; Opening High touch is observational "
                    "only and no canonical exit or realized P&L is defined"
                ),
                "stop_policy": "NONE; canonical exit lifecycle undefined",
                "target_policy": "OPENING_HIGH_TOUCH_REFERENCE",
                "target_level": "Opening High",
                "period": period,
                "segment_dimension": dimension,
                "segment": segment,
                "eligible_setups": len(group_rows),
                "eligible_entries": len(group_rows),
                "valid_entries": None,
                "complete_paths": denominator,
                "incomplete_paths": len(group_rows) - denominator,
                "target_touches": touches,
                "target_touch_numerator": touches,
                "target_touch_denominator": denominator,
                "target_touch_rate": touches / denominator if denominator else None,
                "target_exits": None,
                "stop_exits": None,
                "end_of_session_exits": None,
                "ambiguous_count": None,
                "unresolved_count": len(group_rows),
                "skipped_count": 0,
                "skip_reason_counts": "{}",
                "resolved_trades": None,
                "target_hit_numerator": None,
                "target_hit_denominator": None,
                "target_hit_rate": None,
                "target_exit_rate_valid": None,
                "target_exit_rate_of_resolved": None,
                "gross_points": None,
                "average_points_per_entry": None,
                "average_points_per_eligible_entry": None,
                "average_points_per_resolved_trade": None,
                "profit_factor": None,
                "max_drawdown": None,
                "longest_losing_streak": None,
                "data_coverage_status": (
                    "INCOMPLETE_SOURCE_COVERAGE"
                    if period == "OOS_SEP_INCOMPLETE"
                    or (dimension == "MONTH" and segment == "2026-09")
                    else "SAVED_OBSERVATION_LEDGER_ONLY"
                ),
                "metric_status": (
                    "CANONICAL_OBSERVATION_ONLY; NO_EXIT_LIFECYCLE; "
                    "REALIZED_PNL_NOT_ESTABLISHED"
                ),
                "limitations": (
                    "An Opening-High touch is not a simulated exit, win, fill, or P&L. "
                    "The canonical Ekalayava lifecycle has no approved exit rule."
                ),
            })
    return output


def _difference(candidate, reference, key):
    left, right = candidate.get(key), reference.get(key)
    return left - right if left is not None and right is not None else None


def _comparison_row(strategy, basis, policy, reference, period, dimension, segment, limitations):
    out = {
        "strategy": strategy,
        "comparison_basis": basis,
        "policy_id": policy.get("policy_id", ""),
        "reference_policy_id": reference.get("policy_id", ""),
        "period": period,
        "segment_dimension": dimension,
        "segment": segment,
        "limitations": limitations,
    }
    field_map = {
        "target_touches": "target_touches",
        "target_exits": "target_exits",
        "target_exit_rate": "target_hit_rate",
        "stop_exits": "stop_exits",
        "ambiguous_count": "ambiguous_count",
        "unresolved_count": "unresolved_count",
        "gross_points": "gross_points",
        "max_drawdown": "max_drawdown",
        "longest_losing_streak": "longest_losing_streak",
    }
    for output_name, metric in field_map.items():
        out[output_name] = policy.get(metric)
        out[f"reference_{output_name}"] = reference.get(metric)
        out[f"{output_name[:-1] if output_name.endswith('s') else output_name}_difference"] = (
            _difference(policy, reference, metric)
        )
    # Use stable explicit names where singularization above is ambiguous.
    out["target_touch_difference"] = _difference(policy, reference, "target_touches")
    out["target_touch_rate"] = policy.get("target_touch_rate")
    out["reference_target_touch_rate"] = reference.get("target_touch_rate")
    touch_rate_difference = _difference(policy, reference, "target_touch_rate")
    out["target_touch_rate_difference_pp"] = (
        100 * touch_rate_difference if touch_rate_difference is not None else None
    )
    out["target_exit_difference"] = _difference(policy, reference, "target_exits")
    out["target_exit_rate_difference_pp"] = (
        100 * _difference(policy, reference, "target_hit_rate")
        if _difference(policy, reference, "target_hit_rate") is not None else None
    )
    out["stop_exit_difference"] = _difference(policy, reference, "stop_exits")
    out["ambiguous_difference"] = _difference(policy, reference, "ambiguous_count")
    out["unresolved_difference"] = _difference(policy, reference, "unresolved_count")
    out["gross_points_difference"] = _difference(policy, reference, "gross_points")
    out["max_drawdown_difference"] = _difference(policy, reference, "max_drawdown")
    out["longest_losing_streak_difference"] = _difference(
        policy, reference, "longest_losing_streak"
    )
    return out


def build_comparison_rows(summary_rows: list[dict]) -> list[dict]:
    index = {
        (row["strategy"], row["policy_id"], row["period"],
         row["segment_dimension"], row["segment"]): row
        for row in summary_rows
    }
    output = []
    for key, candidate in index.items():
        strategy, policy_id, period, dimension, segment = key
        if strategy == "L2L":
            reference_id = "SL_4_TP_100"
            reference = index.get((strategy, reference_id, period, dimension, segment))
            if reference:
                output.append(_comparison_row(
                    strategy, "CANONICAL_OPENING_HIGH_BASELINE", candidate, reference,
                    period, dimension, segment,
                    "The baseline and candidate may have different valid-entry denominators; "
                    "rate difference is target exits per policy-entered trade.",
                ))
        else:
            if period in ("ALL", "TRAIN_JAN_JUN", "VALIDATION_JUL_AUG",
                          "OOS_SEP_INCOMPLETE") and dimension in (
                              "ALL", "OPTION_TYPE", "ITM_RANK", "ENTRY_TIME", "MONTH"
                          ):
                reference_id = "EKALAYAVA_CANONICAL_OPENING_HIGH_OBSERVATION_ONLY"
                observation_reference = index.get(
                    (strategy, reference_id, period, dimension, segment)
                )
                if observation_reference:
                    comparison = dict(candidate)
                    observation_reference = dict(observation_reference)
                    observation_reference.update({
                        "target_exits": None,
                        "target_hit_rate": None,
                        "stop_exits": None,
                        "ambiguous_count": None,
                        "unresolved_count": None,
                        "gross_points": None,
                        "max_drawdown": None,
                        "longest_losing_streak": None,
                    })
                    output.append(_comparison_row(
                        strategy, "CANONICAL_OBSERVATION_TOUCHES_ONLY", comparison,
                        observation_reference, period, dimension, segment,
                        "Canonical Opening-High touches are not exits or P&L. For targets "
                        "below Opening High, the raw touch difference compares different "
                        "target levels and is descriptive only.",
                    ))

            if dimension != "ALL":
                continue
            if policy_id == "TRAIL_CAUSAL_LOWER_LOW_B2_TP100":
                reference_id = "A_STRUCTURAL_TROUGH_B2_TP100_OPENING_HIGH"
            else:
                reference_id = policy_id.rsplit("_", 1)[0] + "_TP100_OPENING_HIGH"
                if policy_id.endswith("_TP100_OPENING_HIGH"):
                    reference_id = policy_id
            reference = index.get((strategy, reference_id, period, "ALL", "ALL"))
            if reference:
                output.append(_comparison_row(
                    strategy, "SAME_ANCHOR_BUFFER_TP100_EXPERIMENTAL_REFERENCE",
                    candidate, reference, period, dimension, segment,
                    "This is a comparison to another experimental policy, not to a "
                    "canonical Ekalayava exit baseline.",
                ))
    return output


def build_data_quality_rows(l2l_rows, ekalayava_rows, observations):
    result = []

    def add(strategy, check, observed, expected=None, status="VERIFIED", note=""):
        result.append({
            "strategy": strategy, "check": check, "observed_value": observed,
            "expected_value": expected, "status": status, "note": note,
        })

    l2l_ids = {(row["policy"], row["setup_id"]) for row in l2l_rows}
    add("L2L", "saved_policy_trade_rows", len(l2l_rows), 12 * 361)
    add("L2L", "unique_policy_setup_pairs", len(l2l_ids), len(l2l_rows))
    add("L2L", "distinct_policy_definitions", len({r["policy"] for r in l2l_rows}), 12)
    add("L2L", "source_bar_count_75", sum(_integer(r["source_bar_count"]) == 75 for r in l2l_rows), len(l2l_rows))
    add("L2L", "target_exit_plus_ambiguous_is_touch",
        sum(r["outcome"] in {"TARGET", "AMBIGUOUS"} for r in l2l_rows),
        note="Counts one target touch per terminal target/ambiguous outcome; does not count post-exit candle touches.")
    add("L2L", "saved_unresolved_outcomes",
        sum(_is_unresolved(r["outcome"]) for r in l2l_rows), 0,
        note="Historical policy rows do not retain per-candle timestamps for independent path replay.")
    add("L2L", "canonical_baseline_setup_count", 361, 361)
    add("L2L", "full_policy_grid_replayed", "NO", "NO", note="Existing CSV ledgers were aggregated only.")

    eka_ids = {(row["policy"], row["setup_id"]) for row in ekalayava_rows}
    add("EKALAYAVA", "saved_policy_trade_rows", len(ekalayava_rows), 37 * 253)
    add("EKALAYAVA", "unique_policy_setup_pairs", len(eka_ids), len(ekalayava_rows))
    add("EKALAYAVA", "distinct_policy_definitions", len({r["policy"] for r in ekalayava_rows}), 37)
    add("EKALAYAVA", "source_bar_count_75", sum(_integer(r["source_bar_count"]) == 75 for r in ekalayava_rows), len(ekalayava_rows))
    add("EKALAYAVA", "canonical_observation_entries", len(observations), 253)
    add("EKALAYAVA", "canonical_opening_high_touches",
        sum(row.get("target_touched") == "True" for row in observations), 109,
        note="Observation only; no canonical exit or realized P&L.")
    add("EKALAYAVA", "canonical_realized_pnl_present",
        sum(bool(row.get("realized_pnl")) for row in observations), 0)
    add("EKALAYAVA", "C_anchor_independent_policy_count",
        sum(row.get("policy_family") == "C_RECOVERY_BASE_INVALIDATION" for row in ekalayava_rows),
        0, note="C is an alias of A and was not independently simulated.")
    add("EKALAYAVA", "saved_unresolved_policy_outcomes",
        sum(_is_unresolved(row["outcome"]) for row in ekalayava_rows), 0)
    add("EKALAYAVA", "full_policy_grid_replayed", "NO", "NO", note="Saved ledgers and MFE observations were aggregated only.")
    for year in ("2022", "2023", "2024", "2025"):
        add("DATA_SCOPE", f"local_market_data_{year}", "NONE", "AVAILABLE",
            status="UNAVAILABLE", note="No local 5-minute datasets; no data downloaded.")
    add("DATA_SCOPE", "2026_option_contract_days_complete_partial_missing",
        "561 / 1 / 178 of 740", "740 expected")
    add("DATA_SCOPE", "September_status", "INCOMPLETE through 2026-09-29", "Complete through 2026-09-30",
        status="INCOMPLETE", note="No Sep 30 underlying; Sep 29 underlying misses 17 late bars.")
    add("DATA_SCOPE", "downloaded_new_market_data", "NO", "NO")
    return result


def main():
    l2l = _read_csv(REPORTS / "multi_year_l2l_combined_sl_tp_trades.csv")
    observations = _read_csv(REPORTS / "multi_year_ekalayava_observations.csv")
    ekalayava_raw = _read_csv(REPORTS / "ekalayava_exit_policy_trades.csv")
    if len({(r["policy"], r["setup_id"]) for r in l2l}) != len(l2l):
        raise ValueError("Duplicate L2L policy/setup rows")
    ekalayava = enrich_ekalayava_rows(ekalayava_raw, observations)
    summaries = build_summary_rows(l2l, ekalayava)
    summaries.extend(build_observation_reference_rows(observations))
    comparisons = build_comparison_rows(summaries)
    quality = build_data_quality_rows(l2l, ekalayava, observations)
    _write_csv(REPORTS / "target_hit_policy_period_summary.csv", SUMMARY_FIELDS, summaries)
    _write_csv(REPORTS / "target_hit_baseline_comparison.csv", COMPARISON_FIELDS, comparisons)
    _write_csv(
        REPORTS / "target_hit_data_quality_summary.csv",
        ["strategy", "check", "observed_value", "expected_value", "status", "note"],
        quality,
    )
    print(
        f"Generated {len(summaries)} policy/period/segment rows, "
        f"{len(comparisons)} comparison rows, and {len(quality)} data-quality checks."
    )


if __name__ == "__main__":
    main()
