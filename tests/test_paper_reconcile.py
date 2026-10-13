import json
from datetime import datetime, timedelta
import subprocess
import sys

from app.paper_reconcile import reconcile_session
from app.paper_shadow import CANDIDATES, EkalayavaShadowBook


T0 = "2026-10-13T09:15:00+05:30"


def _signal():
    return {
        "event_type": "SIGNAL",
        "strategy": "EKALAYAVA",
        "event_id": "setup-1",
        "setup_id": "setup-1",
        "date": "2026-10-13",
        "timestamp": T0,
        "strategy_version": "test-v1",
        "symbol": "NSE-NIFTY-15Oct26-25000-CE",
        "expiry": "2026-10-15",
        "strike": 25000,
        "option_type": "CE",
        "itm_rank": 2,
        "entry": 100.0,
        "opening_high": 120.0,
        "structural_low_candidate": 90.0,
    }


def _write_json(path, payload):
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _make_session(root, *, high=130, low=99):
    root.mkdir()
    signal = _signal()
    health = {"missing_contracts": [], "status": "OK"}
    _write_json(root / "observer_health.json", health)
    _write_json(root / "contract.state.json", {"ekalayava": {"signal": signal}})
    book = EkalayavaShadowBook(root / "contract.shadow.json", root / "paper_journal.jsonl")
    book.observe_signal(signal)
    stamp = datetime.fromisoformat(T0)
    book.advance({
        "timestamp": stamp + timedelta(minutes=5),
        "close_time": stamp + timedelta(minutes=10),
        "open": 100,
        "high": high,
        "low": low,
        "close": 105,
        "completed": True,
        "symbol": signal["symbol"],
    })
    records = [json.loads(line) for line in (root / "paper_journal.jsonl").read_text().splitlines()]
    records.append({
        "record_id": "canonical-signal-1",
        "event_id": "setup-1",
        "setup_id": "setup-1",
        "event_type": "SIGNAL",
        "strategy": "EKALAYAVA",
        "timestamp": T0,
    })
    records.append({
        "record_id": "candle-1",
        "event_type": "CANDLE_OBSERVED",
        "timestamp": T0,
        "close_time": (stamp + timedelta(minutes=5)).isoformat(),
        "stream": "OPTIONS",
        "symbol": signal["symbol"],
        "open": 100,
        "high": high,
        "low": low,
        "close": 105,
        "data_provenance": "synthetic fixture",
        "source_retrieved_at": T0,
    })
    (root / "paper_journal.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in records),
        encoding="utf-8",
    )
    return root


def test_reconcile_counts_seven_candidate_targets_and_is_deterministic(tmp_path):
    root = _make_session(tmp_path / "session")
    first = reconcile_session(root)
    second = reconcile_session(root)

    assert first == second
    assert first["integrity_ok"] is True
    assert len(first["candidate_outcomes"]) == 7
    for candidate in CANDIDATES:
        counts = first["candidate_outcomes"][candidate["candidate_id"]]
        assert counts["target_exits"] == 1
        assert counts["stop_exits"] == 0
        assert counts["ambiguous"] == 0
        assert counts["gross_hypothetical_points"] > 0
        assert counts["null_point_outcomes"] == 0
    assert first["missing_quote_records"] > 0
    assert first["missing_fill_or_cost_records"] > 0
    assert first["actual_fill_records"] == 0
    assert first["actual_fill_status"] == "NOT_RECORDED"
    assert first["transaction_cost_status"] == "NOT_RECORDED"


def test_reconcile_preserves_ambiguous_and_incomplete_path_findings(tmp_path):
    root = _make_session(tmp_path / "session", high=125, low=80)
    result = reconcile_session(root)

    assert result["integrity_ok"] is True
    assert all(item["ambiguous"] == 1
               for item in result["candidate_outcomes"].values())
    assert any("candle path incomplete" in warning
               for warning in result["data_quality_warnings"])
    assert all(item["null_point_outcomes"] == 1
               for item in result["candidate_outcomes"].values())


def test_reconcile_distinguishes_zero_points_from_absent_points(tmp_path):
    root = _make_session(tmp_path / "session")
    journal = root / "paper_journal.jsonl"
    rows = [json.loads(line) for line in journal.read_text().splitlines()]
    candidate_id = CANDIDATES[0]["candidate_id"]
    terminal = next(row for row in rows
                    if row.get("event_type") == "SHADOW_CANDIDATE_EXIT"
                    and row.get("candidate_id") == candidate_id)
    terminal["hypothetical_points"] = 0.0
    candidate_snapshot = json.loads(terminal["candidate_state_json"])
    candidate_snapshot["points"] = 0.0
    terminal["candidate_state_json"] = json.dumps(candidate_snapshot, sort_keys=True)
    (root / "contract.shadow.json").write_text(
        json.dumps({
            "version": 1,
            "candidates": {
                key: ({**candidate, "points": 0.0} if candidate["candidate_id"] == candidate_id
                      else candidate)
                for key, candidate in json.loads(
                    (root / "contract.shadow.json").read_text(encoding="utf-8")
                )["candidates"].items()
            },
        }),
        encoding="utf-8",
    )
    journal.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    result = reconcile_session(root)
    counts = result["candidate_outcomes"][candidate_id]
    assert counts["zero_point_outcomes"] == 1
    assert counts["null_point_outcomes"] == 0


def test_reconcile_detects_duplicate_and_malformed_records(tmp_path):
    root = _make_session(tmp_path / "session")
    journal = root / "paper_journal.jsonl"
    rows = [json.loads(line) for line in journal.read_text().splitlines()]
    rows.append(rows[-1])
    rows.append({"record_id": "bad-candle", "event_type": "CANDLE_OBSERVED",
                 "timestamp": "not-a-time"})
    journal.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    result = reconcile_session(root)
    assert result["integrity_ok"] is False
    assert any("duplicate record_id" in error for error in result["integrity_errors"])
    assert any("journal line" in error for error in result["integrity_errors"])


def test_reconcile_detects_missing_strategy_and_candidate_states(tmp_path):
    root = _make_session(tmp_path / "session")
    (root / "contract.state.json").unlink()
    shadow_path = root / "contract.shadow.json"
    state = json.loads(shadow_path.read_text(encoding="utf-8"))
    missing_key = next(key for key, candidate in state["candidates"].items()
                       if candidate["candidate_id"] == CANDIDATES[0]["candidate_id"])
    del state["candidates"][missing_key]
    shadow_path.write_text(json.dumps(state), encoding="utf-8")

    result = reconcile_session(root)

    assert result["integrity_ok"] is False
    assert result["canonical_signals_missing_state"]
    assert result["canonical_signals_missing_shadow_state"]["setup-1"] == [
        CANDIDATES[0]["candidate_id"]
    ]


def test_reconcile_detects_gaps_and_conflicting_terminal_events(tmp_path):
    root = _make_session(tmp_path / "session")
    journal = root / "paper_journal.jsonl"
    rows = [json.loads(line) for line in journal.read_text().splitlines()]
    candle = next(row for row in rows if row["event_type"] == "CANDLE_OBSERVED")
    rows.append(dict(
        candle,
        record_id="candle-2",
        timestamp="2026-10-13T09:35:00+05:30",
        close_time="2026-10-13T09:40:00+05:30",
    ))
    exits = [row for row in rows if row["event_type"] == "SHADOW_CANDIDATE_EXIT"]
    conflict = dict(exits[0], record_id="conflicting-exit", outcome="STOP_LOSS")
    conflict_snapshot = json.loads(conflict["candidate_state_json"])
    conflict_snapshot["outcome"] = "STOP_LOSS"
    conflict["candidate_state_json"] = json.dumps(conflict_snapshot, sort_keys=True)
    rows.append(conflict)
    journal.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    result = reconcile_session(root)
    assert result["integrity_ok"] is False
    assert result["candidate_terminal_conflicts"]
    assert result["candle_streams"][0]["gaps"]


def test_reconciliation_cli_emits_json_and_returns_nonzero_on_integrity_failure(tmp_path):
    root = tmp_path / "session"
    root.mkdir()
    _write_json(root / "observer_health.json", {"missing_contracts": []})
    (root / "paper_journal.jsonl").write_text("{malformed json}\n", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "-m", "tools.reconcile_paper_session", str(root)],
        capture_output=True,
        check=False,
        text=True,
    )

    result = json.loads(completed.stdout)
    assert completed.returncode == 2
    assert result["integrity_ok"] is False
    assert "Integrity: FAIL" in completed.stderr


def test_reconcile_loads_observer_health_from_parent_of_date_scoped_journal(tmp_path):
    base = tmp_path / "observer"
    base.mkdir()
    root = _make_session(base / "2026-10-13")
    (root / "observer_health.json").replace(base / "observer_health.json")

    result = reconcile_session(root)

    assert result["integrity_ok"] is True
    assert result["health_snapshot_location"] == "observer_parent"
