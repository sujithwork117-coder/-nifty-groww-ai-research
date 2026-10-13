import csv
from datetime import date, datetime, time, timedelta
import json
from types import SimpleNamespace

import pandas as pd

import run_research


def test_inventory_counts_rows_once_and_handles_mixed_timestamp_zones(tmp_path):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    for name, timestamp in (
        ("naive.csv", "2026-01-02T09:15:00"),
        ("aware.csv", "2026-01-02T09:20:00+05:30"),
    ):
        with (raw / name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["timestamp"])
            writer.writeheader()
            writer.writerow({"timestamp": timestamp})

    result = run_research._inventory_data(tmp_path)

    assert result["files_inspected"] == 2
    assert result["rows_across_file_copies_by_year"]["2026"] == {
        "rows_across_files": 2,
        "files_with_rows": 2,
    }
    assert result["earliest_timestamp"] == "2026-01-02T03:45:00+00:00"
    assert result["latest_timestamp"] == "2026-01-02T03:50:00+00:00"


def test_fetch_history_bounds_and_filters_provider_rows(tmp_path, monkeypatch, capsys):
    from app import groww_auth, groww_data

    requested_day = datetime.now(run_research.IST).date() - timedelta(days=1)
    earlier_day = requested_day - timedelta(days=1)
    session_start = datetime.combine(requested_day, time(9, 15), run_research.IST)
    expected_timestamps = [
        (session_start + timedelta(minutes=5 * index)).astimezone(run_research.timezone.utc)
        for index in range(75)
    ]
    candles = [
        [f"{earlier_day.isoformat()} 09:15:00", 100, 101, 99, 100],
        [f"{requested_day.isoformat()} 08:55:00", 100, 101, 99, 100],
    ]
    candles.extend([
        [(session_start + timedelta(minutes=5 * index)).strftime("%Y-%m-%d %H:%M:%S"),
         100, 101, 99, 100]
        for index in range(75)
    ])
    payload = {"candles": candles}
    monkeypatch.setattr(run_research, "ROOT", tmp_path)
    monkeypatch.setattr(run_research, "_historical_source_paths", lambda _: [])
    monkeypatch.setattr(
        run_research, "_load_existing_history",
        lambda *_: (
            pd.DataFrame(columns=groww_data.DATA_COLUMNS), set()
        ),
    )
    monkeypatch.setattr(
        run_research, "_session_gaps",
        lambda _, available: [
            stamp for stamp in expected_timestamps if stamp not in available
        ],
    )
    monkeypatch.setattr(groww_auth, "authenticate", lambda _: SimpleNamespace(
        get_user_profile=lambda: {"read_only": True}
    ))
    monkeypatch.setattr(groww_data, "_fetch", lambda *_: payload)

    result = run_research.fetch_history(requested_day, requested_day)

    assert result == 0
    derived = pd.read_csv(
        tmp_path / "data" / "derived" / "groww_history" / "NIFTY.csv"
    )
    assert len(derived) == 75
    assert derived["timestamp"].iloc[0] == (
        f"{requested_day.isoformat()} 03:45:00+00:00"
    )
    assert derived["timestamp"].iloc[-1] == (
        f"{requested_day.isoformat()} 09:55:00+00:00"
    )
    manifest = json.loads(
        (tmp_path / "data" / "derived" / "groww_history" /
         "NIFTY.manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["request_responses_complete"] is True
    assert manifest["row_count_in_requested_range"] == 75
    assert manifest["coverage_complete_for_supported_sessions"] is True
    assert "status" in capsys.readouterr().out


def test_empty_history_response_is_partial_not_success(tmp_path, monkeypatch, capsys):
    from app import groww_auth, groww_data

    requested_day = datetime.now(run_research.IST).date() - timedelta(days=1)
    monkeypatch.setattr(run_research, "ROOT", tmp_path)
    monkeypatch.setattr(run_research, "_historical_source_paths", lambda _: [])
    monkeypatch.setattr(
        run_research, "_load_existing_history",
        lambda *_: (
            pd.DataFrame(columns=groww_data.DATA_COLUMNS), set()
        ),
    )
    monkeypatch.setattr(run_research, "_session_gaps", lambda *_: [object()])
    monkeypatch.setattr(groww_auth, "authenticate", lambda _: SimpleNamespace(
        get_user_profile=lambda: {"read_only": True}
    ))
    monkeypatch.setattr(groww_data, "_fetch", lambda *_: {"candles": []})

    result = run_research.fetch_history(requested_day, requested_day)

    assert result == 2
    assert '"status": "PARTIAL"' in capsys.readouterr().out
    manifest = json.loads(
        (tmp_path / "data" / "derived" / "groww_history" /
         "NIFTY.manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["request_responses_complete"] is False
    assert manifest["requests"][0]["status"] == "EMPTY_RESPONSE"


def test_fetch_history_rejects_oversized_range_before_authentication(monkeypatch):
    from app import groww_auth

    auth_called = False

    def unexpected_auth(_):
        nonlocal auth_called
        auth_called = True
        raise AssertionError("authentication must not run for rejected input")

    monkeypatch.setattr(groww_auth, "authenticate", unexpected_auth)
    today = datetime.now(run_research.IST).date()

    result = run_research.fetch_history(
        today - timedelta(days=31), today, symbol="NIFTY"
    )

    assert result == 2
    assert auth_called is False


def test_cli_default_dispatches_to_offline_workflow(monkeypatch):
    monkeypatch.setattr(run_research, "default_workflow", lambda: 17)

    assert run_research.main([]) == 17


def test_grouping_splits_at_chunk_boundary_and_weekends():
    start = date(2026, 1, 5)
    days = [start + timedelta(days=offset) for offset in range(17)]

    groups = run_research._missing_date_groups(days)

    assert all((group[-1] - group[0]).days < run_research.HISTORY_CHUNK_DAYS
               for group in groups)
    assert [group[0] for group in groups] == [start, start + timedelta(days=14)]
