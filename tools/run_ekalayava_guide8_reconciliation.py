"""Produce exact outcome and target-touch counts for Guide 8.

This is an offline accounting pass over the fixed Guide 7 candidate set plus
the archived fractional TP25 policy. It does not select or tune policies.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

from app.research_ekalayava_exits import simulate_ekalayava_exit
from tools.run_ekalayava_guide7_research import (
    IST,
    OPTION_ROOT_2025,
    POLICIES,
    REPORTS,
    ROOT,
    SOURCE_2025,
    _add_event_bars,
    _build_2025_events,
    _choose_exact_session,
    _load_option_files,
    _metrics,
    _read_csv,
    _simulate_event,
    _write_csv,
)


ARCHIVED_TP25 = {
    "policy_id": "A_STRUCTURAL_TROUGH_B4_TP25",
    "family": "ARCHIVED_FRACTIONAL_OPENING_HIGH",
    "buffer": 4.0,
    "target_kind": "FRACTIONAL_OPENING_HIGH",
    "target_parameter": 0.25,
    "trailing": False,
}
ALL_POLICIES = (*POLICIES, ARCHIVED_TP25)
EXIT_CATEGORIES = {
    "TARGET", "STOP_LOSS", "AMBIGUOUS", "END_OF_SESSION",
}
UNRESOLVED_PREFIX = "UNRESOLVED"
EXCLUDED_PREFIX = "EXCLUDED"


def _target(policy: dict, entry: float, stop: float, opening_high: float) -> float:
    if policy["target_kind"] == "FRACTIONAL_OPENING_HIGH":
        return entry + float(policy["target_parameter"]) * (opening_high - entry)
    if policy["target_kind"] == "FIXED_25":
        return entry + float(policy["target_parameter"])
    if policy["target_kind"] == "OPENING_HIGH":
        return opening_high
    if policy["target_kind"] == "RR":
        risk = entry - stop
        if risk <= 0:
            return entry
        return entry + risk * float(policy["target_parameter"])
    raise ValueError(f"Unsupported target kind: {policy['target_kind']}")


def _classify_target_touch(
    bars: list[dict],
    entry_timestamp: object,
    target: float | None,
    result: dict,
    path_status: str,
) -> tuple[str, str | None]:
    if target is None:
        return "UNVERIFIABLE_NO_TARGET_LEVEL", None
    entry_stamp = pd.Timestamp(entry_timestamp)
    exit_stamp = (
        pd.Timestamp(result["exit_timestamp"])
        if result.get("exit_timestamp") else None
    )
    future = [
        bar for bar in bars
        if pd.Timestamp(bar["timestamp"]) > entry_stamp
        and float(bar["high"]) >= target
    ]
    first_touch = min(
        future, key=lambda bar: pd.Timestamp(bar["timestamp"]),
    ) if future else None
    if first_touch is None:
        if path_status != "COMPLETE_POST_ENTRY_PATH":
            return "UNVERIFIABLE_INCOMPLETE_PATH", None
        return "NOT_TOUCHED", None

    touch_stamp = pd.Timestamp(first_touch["timestamp"])
    exit_category = result.get("outcome")
    if exit_category == "AMBIGUOUS" and exit_stamp == touch_stamp:
        return "ORDER_AMBIGUOUS_ON_EXIT_BAR", touch_stamp.isoformat()
    if exit_stamp is not None and touch_stamp > exit_stamp:
        return "TOUCHED_AFTER_EXIT", touch_stamp.isoformat()
    if exit_category == "TARGET" and exit_stamp == touch_stamp:
        return "TOUCHED_WHILE_OPEN_TARGET_EXIT", touch_stamp.isoformat()
    if exit_stamp is not None and touch_stamp <= exit_stamp:
        return "TOUCHED_WHILE_OPEN", touch_stamp.isoformat()
    return "TOUCHED_WHILE_OPEN", touch_stamp.isoformat()


def _run_policy(event: dict, bars: list[dict], policy: dict) -> dict:
    if policy["policy_id"] != ARCHIVED_TP25["policy_id"]:
        result = _simulate_event(event, bars, policy)
        target = result.get("target")
    else:
        entry = float(event["entry"])
        anchor = event.get("observed_reversal_structure_low")
        if anchor is None or pd.isna(anchor):
            result = {
                "outcome": "EXCLUDED_ANCHOR_UNAVAILABLE",
                "reason": "structural_trough_missing",
            }
            target = None
        else:
            stop = float(anchor) - 4.0
            target = _target(policy, entry, stop, float(event["opening_high"]))
            result = simulate_ekalayava_exit(
                bars,
                entry_timestamp=pd.Timestamp(event["timestamp"]).to_pydatetime(),
                entry=entry,
                initial_stop=stop,
                target=target,
                expected_last_timestamp=pd.Timestamp(
                    f"{event['date']} 15:25", tz=IST,
                ).to_pydatetime(),
            )
            result.update({
                "initial_stop": stop,
                "target": target,
                "initial_risk": entry - stop,
            })

    touch_class, touch_time = _classify_target_touch(
        bars, event["timestamp"], target, result, event["path_status"],
    )
    return {
        "dataset": event["dataset"],
        "period": event["period"],
        "date": event["date"],
        "setup_id": event["setup_id"],
        "symbol": event["symbol"],
        "option_type": event.get("option_type", ""),
        "itm_rank": event.get("itm_rank", ""),
        "policy_id": policy["policy_id"],
        "family": policy["family"],
        "path_status": event["path_status"],
        "simulation_attempted": True,
        "outcome": result["outcome"],
        "reason": result.get("reason", ""),
        "entry_timestamp_utc": pd.Timestamp(event["timestamp"]).isoformat(),
        "initial_stop": result.get("initial_stop", ""),
        "target": target if target is not None else "",
        "initial_risk": result.get("initial_risk", ""),
        "points": result.get("points", ""),
        "exit_timestamp": result.get("exit_timestamp", ""),
        "target_touch_class": touch_class,
        "target_touch_timestamp": touch_time or "",
        "source_path": event.get("source_path", ""),
    }


def _no_path_row(observation: dict, policy: dict, path_status: str) -> dict:
    invalid = path_status == "INVALID_OR_MISMATCHED"
    return {
        "dataset": "EXISTING_2026_ENTRY_LEDGER",
        "period": observation["period"],
        "date": observation["date"],
        "setup_id": observation["setup_id"],
        "symbol": observation["symbol"],
        "option_type": observation.get("option_type", ""),
        "itm_rank": observation.get("itm_rank", ""),
        "policy_id": policy["policy_id"],
        "family": policy["family"],
        "path_status": path_status,
        "simulation_attempted": False,
        "outcome": (
            "EXCLUDED_INVALID_OR_MISMATCHED"
            if invalid else "UNRESOLVED_NO_EXACT_PATH"
        ),
        "reason": (
            "exact_contract_metadata_mismatch"
            if invalid else "exact_contract_post_entry_candles_unavailable"
        ),
        "entry_timestamp_utc": observation["timestamp_utc"],
        "initial_stop": "",
        "target": "",
        "initial_risk": "",
        "points": "",
        "exit_timestamp": "",
        "target_touch_class": "UNVERIFIABLE_NO_EXACT_PATH",
        "target_touch_timestamp": "",
        "source_path": "",
    }


def _canonical_opening_high_touches(events: list[dict]) -> list[dict]:
    records = []
    for event in events:
        bars = event.get("_bars", [])
        after_entry = [
            bar for bar in bars
            if pd.Timestamp(bar["timestamp"]) > pd.Timestamp(event["timestamp"])
        ]
        touches = [
            bar for bar in after_entry
            if float(bar["high"]) >= float(event["opening_high"])
        ]
        first = min(
            touches, key=lambda bar: pd.Timestamp(bar["timestamp"]),
        ) if touches else None
        records.append({
            "dataset": event["dataset"],
            "period": event["period"],
            "date": event["date"],
            "setup_id": event["setup_id"],
            "symbol": event["symbol"],
            "path_status": event["path_status"],
            "opening_high": event["opening_high"],
            "opening_high_touch": (
                "TOUCHED" if first is not None
                else "NOT_TOUCHED" if event["path_status"] == "COMPLETE_POST_ENTRY_PATH"
                else "UNVERIFIABLE_INCOMPLETE_PATH"
            ),
            "first_touch_timestamp": (
                pd.Timestamp(first["timestamp"]).isoformat() if first else ""
            ),
        })
    return records


def _period_groups(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["period"]].append(row)
        groups[row["dataset"]].append(row)
        groups["COMBINED_2025_H2_2026_LEDGER"].append(row)
    return groups


def _candidate_counts(rows: list[dict], eligible: int) -> dict:
    counts = Counter(row["outcome"] for row in rows)
    simulated = [row for row in rows if row["simulation_attempted"]]
    invalid = sum(
        row["outcome"].startswith(EXCLUDED_PREFIX) for row in rows
    )
    missing_path = sum(
        not row["simulation_attempted"]
        and row["outcome"].startswith(UNRESOLVED_PREFIX)
        for row in rows
    )
    unresolved_with_path = sum(
        row["outcome"].startswith(UNRESOLVED_PREFIX) for row in simulated
    )
    unresolved = unresolved_with_path + missing_path
    target = counts["TARGET"]
    stop = counts["STOP_LOSS"]
    ambiguous = counts["AMBIGUOUS"]
    eod = counts["END_OF_SESSION"]
    other = sum(
        1 for row in simulated
        if row["outcome"] not in EXIT_CATEGORIES
        and not row["outcome"].startswith(UNRESOLVED_PREFIX)
        and not row["outcome"].startswith(EXCLUDED_PREFIX)
    )
    points = [
        float(row["points"]) for row in rows
        if row["points"] not in ("", None) and row["outcome"] in EXIT_CATEGORIES
    ]
    wins = [point for point in points if point > 0]
    losses = [point for point in points if point < 0]
    performance_rows = [
        {
            "date": row["date"],
            "entry_timestamp_utc": row["entry_timestamp_utc"],
            "exit_timestamp": row["exit_timestamp"] or None,
            "outcome": row["outcome"],
            "points": (
                float(row["points"]) if row["points"] not in ("", None) else None
            ),
            "initial_risk": (
                float(row["initial_risk"])
                if row["initial_risk"] not in ("", None) else None
            ),
        }
        for row in rows
    ]
    performance = _metrics(performance_rows)
    touch_counts = Counter(row["target_touch_class"] for row in rows)
    resolved_outcome_count = target + stop + ambiguous + eod + other
    simulated_valid_count = len(simulated) - sum(
        row["outcome"].startswith(EXCLUDED_PREFIX) for row in simulated
    )
    unverifiable_touches = sum(
        value for key, value in touch_counts.items()
        if key.startswith("UNVERIFIABLE")
    )
    return {
        "detected_entry_setups": eligible,
        "eligible_entries": eligible,
        "simulated_entries_with_exact_path": len(simulated) - invalid,
        "simulation_attempts_with_path": len(simulated),
        "no_exact_path_entries": missing_path,
        "target_exits": target,
        "stop_loss_exits": stop,
        "ambiguous_exits": ambiguous,
        "end_of_session_exits": eod,
        "other_exits": other,
        "unresolved_entries": unresolved,
        "unresolved_after_simulation": unresolved_with_path,
        "invalid_or_excluded_entries": invalid,
        "gross_points": sum(points),
        "resolved_outcomes_with_points": len(points),
        "mean_points_per_resolved_outcome": performance["mean_points_resolved"],
        "median_points_per_resolved_outcome": performance["median_points_resolved"],
        "win_rate_resolved": len(wins) / len(points) if points else None,
        "profit_factor": (
            sum(wins) / abs(sum(losses)) if losses and sum(losses) else None
        ),
        "max_drawdown": performance["max_drawdown"],
        "longest_losing_streak": performance["longest_losing_streak"],
        "target_touched_while_open": (
            touch_counts["TOUCHED_WHILE_OPEN_TARGET_EXIT"]
            + touch_counts["TOUCHED_WHILE_OPEN"]
        ),
        "target_touch_order_ambiguous": touch_counts["ORDER_AMBIGUOUS_ON_EXIT_BAR"],
        "target_touched_after_exit": touch_counts["TOUCHED_AFTER_EXIT"],
        "target_not_touched": touch_counts["NOT_TOUCHED"],
        "target_touch_unverifiable": unverifiable_touches,
        "target_exit_rate_of_eligible": target / eligible if eligible else None,
        "target_exit_rate_of_simulated": (
            target / simulated_valid_count if simulated_valid_count else None
        ),
        "stop_exit_rate_of_simulated": (
            stop / simulated_valid_count if simulated_valid_count else None
        ),
        "ambiguous_rate_of_simulated": (
            ambiguous / simulated_valid_count if simulated_valid_count else None
        ),
        "end_of_session_rate_of_simulated": (
            eod / simulated_valid_count if simulated_valid_count else None
        ),
        "unresolved_rate_of_eligible": (
            unresolved / eligible if eligible else None
        ),
        "no_exact_path_rate_of_eligible": (
            missing_path / eligible if eligible else None
        ),
        "target_touched_while_open_rate_of_simulated": (
            (touch_counts["TOUCHED_WHILE_OPEN_TARGET_EXIT"]
             + touch_counts["TOUCHED_WHILE_OPEN"]) / simulated_valid_count
            if simulated_valid_count else None
        ),
        "target_touched_after_exit_rate_of_simulated": (
            touch_counts["TOUCHED_AFTER_EXIT"] / simulated_valid_count
            if simulated_valid_count else None
        ),
        "target_touch_unverifiable_rate_of_eligible": (
            unverifiable_touches / eligible if eligible else None
        ),
        "resolved_outcome_count": resolved_outcome_count,
        "eligible_outcome_reconciliation_delta": eligible - (
            target + stop + ambiguous + eod + other + unresolved + invalid
        ),
        "simulated_outcome_reconciliation_delta": len(simulated) - (
            target + stop + ambiguous + eod + other + unresolved_with_path + invalid
        ),
    }


def _write_markdown(
    path: Path,
    count_rows: list[dict],
    opening_touch_rows: list[dict],
    verification: dict,
) -> None:
    path_counts: dict[str, Counter] = defaultdict(Counter)
    for row in opening_touch_rows:
        path_counts[row["dataset"]][row["path_status"]] += 1
    exact_2026 = path_counts["EXISTING_2026_ENTRY_LEDGER"]
    exact_2025 = path_counts["GROWW_2025_H2"]
    total_2026 = sum(exact_2026.values())
    missing_2026 = exact_2026["NO_USABLE_POST_ENTRY_PATH"]
    available_2026 = (
        exact_2026["COMPLETE_POST_ENTRY_PATH"]
        + exact_2026["PARTIAL_POST_ENTRY_PATH"]
    )
    total_with_paths = sum(
        row["simulated_entries_with_exact_path"]
        for row in count_rows
        if row["period"] == "COMBINED_2025_H2_2026_LEDGER"
        and row["policy_id"] == "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1"
    )
    eligible_total = sum(
        row["eligible_entries"]
        for row in count_rows
        if row["period"] == "COMBINED_2025_H2_2026_LEDGER"
        and row["policy_id"] == "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1"
    )
    lines = [
        "# Ekalayava Target/Stop Count Reconciliation",
        "",
        "## Decision and scope",
        "",
        "**No exit policy is approved.** The six Guide 7 candidates and the",
        "archived fractional `A_STRUCTURAL_TROUGH_B4_TP25` policy were each",
        "accounted once on the fixed candidate set. This accounting does not",
        "change the prior validation selection or select a policy from test",
        "results. The additional November–December counts for non-selected",
        "candidates are descriptive only; they are not used for ranking or",
        "tuning.",
        "",
        f"The combined ledger has {eligible_total} recorded eligible entry observations:",
        "194 independently redetected on exact 2025 H2 contract paths and 253",
        f"from the saved 2026 entry ledger. The exact-path inventory has "
        f"{exact_2025['COMPLETE_POST_ENTRY_PATH']} complete and "
        f"{exact_2025['PARTIAL_POST_ENTRY_PATH']} partial 2025 entry paths, plus "
        f"{available_2026} exact 2026 paths out of {total_2026}; "
        f"{missing_2026} saved 2026 entries have no exact path after the bounded "
        "recovery attempt. The 2026 entry signals themselves were not all",
        "independently redetected.",
        "The canonical detector/ledger records entry signals, not all",
        "pre-entry candidate formations or rejected setups; those skipped",
        "formation counts are not available and are not estimated.",
        "",
        "Outcome categories are mutually exclusive. `simulated_entries_with_exact_path`",
        "counts valid candidate replays on available paths; `unresolved_entries`",
        "also includes any missing-path observations. Consequently the",
        "eligible-entry reconciliation includes missing paths, while the",
        "simulated-entry reconciliation excludes them. Negative reconciliation",
        "deltas indicate an accounting defect and must be zero.",
        "",
        "## Overall counts by candidate",
        "",
        "| Candidate | Target | Stop | Ambiguous | EOD | Other | Unresolved | Eligible | Simulated with path | Gross points | Approval |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    overall_rows = [
        row for row in count_rows
        if row["period"] == "COMBINED_2025_H2_2026_LEDGER"
    ]
    for row in overall_rows:
        lines.append(
            f"| {row['policy_id']} | {row['target_exits']} | "
            f"{row['stop_loss_exits']} | {row['ambiguous_exits']} | "
            f"{row['end_of_session_exits']} | {row['other_exits']} | "
            f"{row['unresolved_entries']} | {row['eligible_entries']} | "
            f"{row['simulated_entries_with_exact_path']} | "
            f"{row['gross_points']:.2f} | Not approved |"
        )
    lines.extend([
        "",
        "The combined table includes 2025 H2 plus the full saved 2026 ledger.",
        f"Every policy has {eligible_total} eligible entries; "
        f"{total_with_paths} have exact paths to run, including "
        f"{exact_2025['PARTIAL_POST_ENTRY_PATH']} partial 2025 paths. "
        f"{missing_2026} saved 2026 entries remain without exact paths. Candidate "
        "gross totals include only resolved simulations, not",
        "missing or unresolved paths. A positive gross total is not evidence",
        "of net profitability.",
        "",
        "### Strongest experimental candidate (not approved)",
        "",
    ])
    gross_leader = max(overall_rows, key=lambda row: row["gross_points"])
    leader_by_period = {
        row["period"]: row for row in count_rows
        if row["policy_id"] == gross_leader["policy_id"]
    }
    leader_2026 = leader_by_period["EXISTING_2026_ENTRY_LEDGER"]
    lines.extend([
        f"`{gross_leader['policy_id']}` has the highest combined gross points "
        f"({gross_leader['gross_points']:.2f}) among the fixed candidates; its",
        f"combined PF is {gross_leader['profit_factor']:.3f} and drawdown is "
        f"{gross_leader['max_drawdown']:.2f}. This descriptive lead is not",
        "stable across the chronological slices:",
        f"* Training: {leader_by_period['TRAIN_2025_JUL_AUG']['gross_points']:.2f} "
        f"gross points (PF {leader_by_period['TRAIN_2025_JUL_AUG']['profit_factor']:.3f}).",
        f"* Validation: {leader_by_period['VALIDATION_2025_SEP_OCT']['gross_points']:.2f} "
        f"(PF {leader_by_period['VALIDATION_2025_SEP_OCT']['profit_factor']:.3f}).",
        f"* Test: {leader_by_period['TEST_2025_NOV_DEC']['gross_points']:.2f} "
        f"(PF {leader_by_period['TEST_2025_NOV_DEC']['profit_factor']:.3f}).",
        f"* Saved 2026 entries ({leader_2026['simulated_entries_with_exact_path']}/"
        f"{leader_2026['eligible_entries']} exact paths): "
        f"{leader_2026['gross_points']:.2f} gross points.",
        "The additional all-candidate test replays are retrospective count",
        "accounting; no test results were used to change or retune the frozen",
        "candidate definitions. The lead remains unapproved for the paper",
        "engine or trading.",
        "",
        "### Target-touch reconciliation by candidate (combined ledger)",
        "",
        "| Candidate | Touched while open | Ambiguous touch order | Touched after exit | Not touched | Unverifiable |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in overall_rows:
        lines.append(
            f"| {row['policy_id']} | {row['target_touched_while_open']} | "
            f"{row['target_touch_order_ambiguous']} | "
            f"{row['target_touched_after_exit']} | {row['target_not_touched']} | "
            f"{row['target_touch_unverifiable']} |"
        )
    lines.extend([
        "",
        "## Period results",
        "",
        "Counts are policy-specific; target exits across different candidates",
        "must not be added. `Unresolved` includes missing exact-path entries.",
        "",
        "| Period | Candidate | Eligible | Simulated with path | Target | Stop | Ambiguous | EOD | Other | Unresolved | Gross points | Win rate | PF | Max DD | Longest loss streak |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in count_rows:
        if row["period"] == "COMBINED_2025_H2_2026_LEDGER":
            continue
        win_rate = (
            f"{row['win_rate_resolved']:.1%}"
            if row["win_rate_resolved"] is not None else "n/a"
        )
        pf = (
            f"{row['profit_factor']:.3f}"
            if row["profit_factor"] is not None else "n/a"
        )
        lines.append(
            f"| {row['period']} | {row['policy_id']} | "
            f"{row['eligible_entries']} | "
            f"{row['simulated_entries_with_exact_path']} | "
            f"{row['target_exits']} | {row['stop_loss_exits']} | "
            f"{row['ambiguous_exits']} | {row['end_of_session_exits']} | "
            f"{row['other_exits']} | {row['unresolved_entries']} | "
            f"{row['gross_points']:.2f} | {win_rate} | {pf} | "
            f"{row['max_drawdown']:.2f} | {row['longest_losing_streak']} |"
        )
    touch_counts = Counter(row["opening_high_touch"] for row in opening_touch_rows)
    lines.extend([
        "",
        "## Canonical Opening-High touch observations",
        "",
        f"* Recorded entry observations: **{len(opening_touch_rows)}**.",
        f"* Opening High touched on the observed post-entry path: **{touch_counts['TOUCHED']}**.",
        f"* Complete paths with no touch: **{touch_counts['NOT_TOUCHED']}**.",
        f"* Touch rate among verifiable paths: **{touch_counts['TOUCHED'] / max(1, touch_counts['TOUCHED'] + touch_counts['NOT_TOUCHED']):.1%}** "
        f"({touch_counts['TOUCHED']}/"
        f"{touch_counts['TOUCHED'] + touch_counts['NOT_TOUCHED']}).",
        f"* Incomplete or missing paths where touch is not verifiable: "
        f"**{sum(value for key, value in touch_counts.items() if key.startswith('UNVERIFIABLE'))}**.",
        "",
        "These are observational price touches, not policy exits or wins. Policy",
        "target-touch classifications are separately recorded in",
        "`reports/ekalayava_guide8_candidate_trade_outcomes.csv` and summarized",
        "in `reports/ekalayava_guide8_candidate_counts.csv`.",
        "",
        "## Previous 2R holdout reconciliation",
        "",
        f"The existing 69-row 2R test ledger was matched against an independent",
        f"rerun of the exact 2025 entry paths: {verification['matching_rows']}/",
        f"{verification['existing_rows']} rows matched on outcome, points and",
        "exit timestamp. Reproduced outcomes: "
        f"{verification['counts'].get('TARGET', 0)} targets, "
        f"{verification['counts'].get('STOP_LOSS', 0)} stops, "
        f"{verification['counts'].get('END_OF_SESSION', 0)} end-of-session, "
        f"{verification['counts'].get('AMBIGUOUS', 0)} ambiguous, and "
        f"{verification['unresolved']} unresolved. Gross points: "
        f"{verification['gross_points']:.2f}; maximum drawdown: "
        f"{verification['max_drawdown']:.2f}; longest losing streak: "
        f"{verification['longest_losing_streak']}. The reported 21/40/8",
        "result is therefore reproduced.",
        "",
        f"The archived fractional TP25 replay matched "
        f"{verification['archived_tp25_matches']}/"
        f"{verification['archived_tp25_comparable']} available exact-path",
        "events on outcome, points, and exit timestamp. This does not verify",
        "archived outcomes for entries without exact paths.",
        "",
        "## Category and denominator rules",
        "",
        "* The candidate count CSV explicitly names each percentage denominator:",
        "  exit rates of eligible entries or simulated entries, unresolved rate",
        "  of eligible entries, and win rate of resolved outcomes with points.",
        "  Percentages must not be compared without checking that denominator.",
        "* A target touch is counted as an actual target exit only when the",
        "  simulator exited at target. Later touches after a stop are recorded",
        "  separately. Same-bar stop/target collisions are ambiguous, and the",
        "  target-touch ordering for that bar is not asserted.",
        "* Partial/missing candle paths are not interpolated. A target touch",
        "  not observed on an incomplete path is unverifiable, not a no-touch.",
        "* End-of-session close is experimental. Fees, spreads, slippage, taxes",
        "  and account sizing are unavailable; points are gross only.",
        "* Detailed rows, period counts, and rerun output are available in the",
        "  accompanying CSV/JSON artifacts. Reproduce with",
        "  `.venv/bin/python -m tools.run_ekalayava_guide8_reconciliation`.",
        "",
        "## Independent reproduction details",
        "",
        f"* 2025 exact-path rows replayed across each candidate: "
        f"{verification['2025_candidate_rows']}.",
        f"* Exact 2026 paths: {verification['2026_complete_paths']}/"
        f"{total_2026}.",
        f"* Archived fractional TP25 exact-path reproductions: "
        f"{verification['archived_tp25_matches']}/"
        f"{verification['archived_tp25_comparable']}.",
        (
            "* Saved-ledger outcomes remain unresolved where exact paths are missing."
            if missing_2026 else
            "* All 2026 saved entries have exact paths; 2025 partial paths remain"
        ),
        (
            "  explicitly partial and were not extended or interpolated."
            if not missing_2026 else
            "  explicitly unresolved and were not imputed."
        ),
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    manifest_path = SOURCE_2025 / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("Bounded 2025 Groww manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("phase") != "options_complete":
        raise RuntimeError("2025 exact-contract retrieval is not complete")

    index_2025, _ = _load_option_files([OPTION_ROOT_2025])
    events_2025, _ = _build_2025_events(index_2025)
    _add_event_bars(events_2025, index_2025)
    for event in events_2025:
        event["dataset"] = "GROWW_2025_H2"

    index_2026, _ = _load_option_files([
        ROOT / "data" / "raw" / "options",
        ROOT / "data" / "runs",
        ROOT / "data" / "derived" / "final_jan_sep_2026" / "assembled" / "options",
        ROOT / "data" / "derived" / "ekalayava_guide9_2026_groww" / "options",
    ])
    observations = _read_csv(REPORTS / "multi_year_ekalayava_observations.csv")
    events_2026 = []
    no_path_records = []
    coverage_2026 = []
    for observation in observations:
        stamp = pd.Timestamp(observation["timestamp_utc"]).tz_convert("UTC")
        status, source_path, bars, _ = _choose_exact_session(
            observation["symbol"], observation["date"], stamp,
            float(observation["entry"]), index_2026,
        )
        coverage_2026.append({
            "setup_id": observation["setup_id"],
            "path_status": status,
        })
        if status not in {"COMPLETE_POST_ENTRY_PATH", "PARTIAL_POST_ENTRY_PATH"}:
            no_path_records.extend(
                _no_path_row(observation, policy, status)
                for policy in ALL_POLICIES
            )
            continue
        event = {
            **observation,
            "dataset": "EXISTING_2026_ENTRY_LEDGER",
            "timestamp": stamp,
            "date": observation["date"],
            "setup_id": observation["setup_id"],
            "entry": float(observation["entry"]),
            "opening_high": float(observation["opening_high"]),
            "observed_reversal_structure_low": (
                float(observation["structural_low_candidate"])
                if observation.get("structural_low_candidate") else None
            ),
            "path_status": status,
            "source_path": source_path or "",
            "option_type": observation.get("option_type", ""),
            "itm_rank": observation.get("itm_rank", ""),
            "_bars": bars,
        }
        events_2026.append(event)

    outcome_rows = []
    for event in (*events_2025, *events_2026):
        bars = event.get("_bars", [])
        for policy in ALL_POLICIES:
            outcome_rows.append(_run_policy(event, bars, policy))
    outcome_rows.extend(no_path_records)
    outcome_rows.sort(
        key=lambda row: (
            row["policy_id"], row["date"], row["entry_timestamp_utc"],
            row["symbol"],
        )
    )

    opening_touch_rows = _canonical_opening_high_touches(
        list(events_2025) + list(events_2026)
    )
    opening_touch_rows.extend({
        "dataset": "EXISTING_2026_ENTRY_LEDGER",
        "period": observation["period"],
        "date": observation["date"],
        "setup_id": observation["setup_id"],
        "symbol": observation["symbol"],
        "path_status": status,
        "opening_high": observation["opening_high"],
        "opening_high_touch": "UNVERIFIABLE_NO_EXACT_PATH",
        "first_touch_timestamp": "",
    } for observation in observations
        for status in [
            next(row["path_status"] for row in coverage_2026
                 if row["setup_id"] == observation["setup_id"])
        ]
        if status not in {"COMPLETE_POST_ENTRY_PATH", "PARTIAL_POST_ENTRY_PATH"})

    grouped = _period_groups(outcome_rows)
    eligible_by_group: dict[str, int] = defaultdict(int)
    ledger_entries = [
        {
            "dataset": event["dataset"],
            "period": event["period"],
            "setup_id": event["setup_id"],
        }
        for event in events_2025
    ] + [
        {
            "dataset": "EXISTING_2026_ENTRY_LEDGER",
            "period": observation["period"],
            "setup_id": observation["setup_id"],
        }
        for observation in observations
    ]
    for event in ledger_entries:
        eligible_by_group[event["period"]] += 1
        eligible_by_group[event["dataset"]] += 1
        eligible_by_group["COMBINED_2025_H2_2026_LEDGER"] += 1
    count_rows = []
    for group, group_rows in grouped.items():
        for policy in ALL_POLICIES:
            selected = [row for row in group_rows if row["policy_id"] == policy["policy_id"]]
            count_rows.append({
                "period": group,
                "policy_id": policy["policy_id"],
                "family": policy["family"],
                **_candidate_counts(selected, eligible_by_group[group]),
            })
    count_rows.sort(key=lambda row: (row["period"], row["policy_id"]))

    previous_test = _read_csv(REPORTS / "ekalayava_guide7_test_results.csv")
    selected_test = [
        row for row in outcome_rows
        if row["period"] == "TEST_2025_NOV_DEC"
        and row["policy_id"] == "C_B2_2R_V1"
    ]
    comparison_by_setup = {row["setup_id"]: row for row in selected_test}
    reproduced = []
    for saved in previous_test:
        current = comparison_by_setup.get(saved["setup_id"])
        if current is None:
            continue
        points_match = (
            saved["points"] == "" and current["points"] == ""
            or saved["points"] != "" and current["points"] != ""
            and math.isclose(float(saved["points"]), float(current["points"]), abs_tol=1e-8)
        )
        time_match = (
            not saved["exit_timestamp"] and not current["exit_timestamp"]
            or bool(saved["exit_timestamp"]) and bool(current["exit_timestamp"])
            and pd.Timestamp(saved["exit_timestamp"]).tz_convert("UTC")
            == pd.Timestamp(current["exit_timestamp"]).tz_convert("UTC")
        )
        reproduced.append({
            "setup_id": saved["setup_id"],
            "matches": (
                saved["outcome"] == current["outcome"]
                and points_match and time_match
            ),
            "outcome": current["outcome"],
            "points": current["points"],
            "exit_timestamp": current["exit_timestamp"],
        })
    verification_metrics = _metrics([
        {
            "date": row["date"],
            "entry_timestamp_utc": row["entry_timestamp_utc"],
            "exit_timestamp": row["exit_timestamp"] or None,
            "outcome": row["outcome"],
            "points": float(row["points"]) if row["points"] not in ("", None) else None,
        }
        for row in selected_test
    ])
    test_outcomes = Counter(row["outcome"] for row in selected_test)
    archived_rows = _read_csv(REPORTS / "ekalayava_exit_policy_trades.csv")
    archived_map = {
        (
            row["symbol"], row["date"],
            pd.Timestamp(row["timestamp_utc"]).tz_convert("UTC").value,
            row["policy"],
        ): row
        for row in archived_rows
        if row["policy"] == ARCHIVED_TP25["policy_id"]
    }
    archive_comparisons = []
    for row in outcome_rows:
        if (row["dataset"] != "EXISTING_2026_ENTRY_LEDGER"
                or row["policy_id"] != ARCHIVED_TP25["policy_id"]
                or row["path_status"] != "COMPLETE_POST_ENTRY_PATH"):
            continue
        saved = archived_map.get((
            row["symbol"], row["date"],
            pd.Timestamp(row["entry_timestamp_utc"]).tz_convert("UTC").value,
            ARCHIVED_TP25["policy_id"],
        ))
        if saved is None:
            continue
        points_match = (
            saved["points"] == "" and row["points"] == ""
            or saved["points"] != "" and row["points"] != ""
            and math.isclose(float(saved["points"]), float(row["points"]), abs_tol=1e-8)
        )
        time_match = (
            not saved["exit_timestamp"] and not row["exit_timestamp"]
            or bool(saved["exit_timestamp"]) and bool(row["exit_timestamp"])
            and pd.Timestamp(saved["exit_timestamp"]).tz_convert("UTC")
            == pd.Timestamp(row["exit_timestamp"]).tz_convert("UTC")
        )
        archive_comparisons.append(
            saved["outcome"] == row["outcome"] and points_match and time_match
        )

    if len(reproduced) != len(previous_test):
        raise RuntimeError(
            f"Expected to reconcile all {len(previous_test)} saved 2R test rows; "
            f"matched only {len(reproduced)} by setup ID"
        )
    if any(not row["matches"] for row in reproduced):
        raise RuntimeError("At least one saved 2R test outcome failed exact replay")
    if any(row["eligible_outcome_reconciliation_delta"] != 0
           or row["simulated_outcome_reconciliation_delta"] != 0
           for row in count_rows):
        raise RuntimeError("Candidate exit categories failed count reconciliation")

    REPORTS.mkdir(parents=True, exist_ok=True)
    _write_csv(
        REPORTS / "ekalayava_guide8_candidate_trade_outcomes.csv",
        list(outcome_rows[0]), outcome_rows,
    )
    _write_csv(
        REPORTS / "ekalayava_guide8_candidate_counts.csv",
        list(count_rows[0]), count_rows,
    )
    _write_csv(
        REPORTS / "ekalayava_guide8_canonical_opening_high_touches.csv",
        list(opening_touch_rows[0]), opening_touch_rows,
    )
    _write_csv(
        REPORTS / "ekalayava_guide8_test_reproduction.csv",
        list(reproduced[0]) if reproduced else ["setup_id", "matches", "outcome"],
        reproduced,
    )
    verification = {
        "existing_rows": len(previous_test),
        "matching_rows": sum(row["matches"] for row in reproduced),
        "counts": dict(test_outcomes),
        "unresolved": verification_metrics["unresolved"],
        "gross_points": verification_metrics["gross_points"],
        "max_drawdown": verification_metrics["max_drawdown"],
        "longest_losing_streak": verification_metrics["longest_losing_streak"],
        "2025_candidate_rows": len(events_2025) * len(ALL_POLICIES),
        "2026_complete_paths": sum(
            row["path_status"] == "COMPLETE_POST_ENTRY_PATH"
            for row in coverage_2026
        ),
        "archived_tp25_comparable": len(archive_comparisons),
        "archived_tp25_matches": sum(archive_comparisons),
    }
    (REPORTS / "ekalayava_guide8_reconciliation_summary.json").write_text(
        json.dumps({
            "candidate_count_rows": len(count_rows),
            "entry_observations_2025": len(events_2025),
            "entry_observations_2026": len(observations),
            "exact_2025_complete_paths": sum(
                event["path_status"] == "COMPLETE_POST_ENTRY_PATH"
                for event in events_2025
            ),
            "exact_2025_partial_paths": sum(
                event["path_status"] == "PARTIAL_POST_ENTRY_PATH"
                for event in events_2025
            ),
            "exact_2026_paths": verification["2026_complete_paths"],
            "2026_missing_exact_paths": len(observations) - verification["2026_complete_paths"],
            "candidate_ids": [policy["policy_id"] for policy in ALL_POLICIES],
            "test_reproduction": verification,
            "execution_allowed": False,
            "paper_only": True,
            "orders_submitted": False,
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_markdown(
        REPORTS / "EKALAYAVA_TARGET_SL_COUNT_RECONCILIATION.md",
        count_rows, opening_touch_rows, verification,
    )
    print(json.dumps({
        "entries_2025": len(events_2025),
        "entries_2026": len(observations),
        "exact_2026_paths": verification["2026_complete_paths"],
        "test_reproduced": f"{verification['matching_rows']}/{verification['existing_rows']}",
        "test_counts": dict(test_outcomes),
        "candidate_count_rows": len(count_rows),
        "all_reconciliation_deltas_zero": True,
    }, indent=2))


if __name__ == "__main__":
    main()
