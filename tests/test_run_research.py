import csv
from datetime import date, datetime, time, timedelta
import json
from types import SimpleNamespace

import pandas as pd

import run_research


def test_year_study_retrieves_supported_months_sequentially_and_skips_old_ones(
    tmp_path, monkeypatch,
):
    from app import year_research

    now = datetime(2026, 10, 13, 17, 0, tzinfo=year_research.IST)
    fetched_months = []

    def fake_request(client, symbol, segment, expected, expected_days,
                     year, month, raw_dir, root):
        assert client is not None and expected_days
        assert raw_dir.is_relative_to(root / "data" / "raw")
        fetched_months.append((year, month, symbol, segment))
        frame = pd.DataFrame({
            "timestamp": sorted(expected),
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
            "volume": None, "oi": None,
        })
        return frame, {"status": "DATA_RETURNED", "rows": len(frame)}

    monkeypatch.setattr(year_research, "_request_month", fake_request)
    monkeypatch.setattr(
        year_research, "_collect_contract_catalog",
        lambda *_: {"expiry_queries": [], "chains": []},
    )
    monkeypatch.setattr(
        year_research, "_fetch_option_month",
        lambda *_: {
            "requested_contracts": 0, "contracts": [], "unavailable_days": [],
        },
    )
    progress = []

    result = year_research.collect_year(
        object(), 2026, tmp_path, now=now, progress=progress.append,
    )

    assert [month for _, month, symbol, _ in fetched_months if symbol == "NIFTY"] == [
        7, 8, 9, 10,
    ]
    assert all(segment == "CASH" for _, _, symbol, segment in fetched_months
               if symbol == "NIFTY")
    assert [item["status"] for item in result["months"][:6]] == [
        "OUTSIDE_GROWW_FIVE_MINUTE_HISTORY_WINDOW"
    ] * 6
    assert [item["status"] for item in result["months"][-2:]] == [
        "FUTURE_MONTH", "FUTURE_MONTH",
    ]
    assert len([line for line in progress if "skipped:" in line]) == 8
    assert len([line for line in progress if "finished:" in line]) == 4
    assert (tmp_path / result["underlying_csv"]).is_file()


def test_complete_local_year_manifest_avoids_repeat_groww_fetch(tmp_path):
    from app import year_research

    now = datetime(2026, 10, 13, 17, 0, tzinfo=year_research.IST)
    base = tmp_path / "data" / "derived" / "groww_history"
    base.mkdir(parents=True)
    (base / "contract_catalog_2026.json").write_text(
        json.dumps({"2026-10-29": [{"symbol": "NSE-NIFTY-29Oct26-25000-CE"}]}),
        encoding="utf-8",
    )
    months = []
    earliest = now.date() - timedelta(days=year_research.HISTORY_WINDOW_DAYS)
    for month in range(1, 13):
        first, last = year_research._month_dates(2026, month)
        if first > now.date():
            continue
        start, end = max(first, earliest), min(last, now.date())
        if start > end:
            continue
        days = [
            date(2026, month, day)
            for day in range(start.day, end.day + 1)
            if year_research.DEFAULT_NSE_CALENDAR.session_for(
                date(2026, month, day)
            )
        ]
        expected_count = len(year_research._expected_stamps(days, now))
        if expected_count:
            months.append({
                "month": f"2026-{month:02d}",
                "status": "COMPLETE",
                "requested_start": start.isoformat(),
                "requested_end": end.isoformat(),
                "underlying_expected_bars": expected_count,
            })
    (base / "year_study_2026.manifest.json").write_text(
        json.dumps({"months": months}), encoding="utf-8",
    )

    assert year_research.local_year_study_complete(2026, tmp_path, now=now)


def test_month_request_keeps_only_expected_completed_interval(tmp_path, monkeypatch):
    from app import year_research

    day = date(2026, 10, 12)
    payload = {
        "candles": [
            ["2026-10-12 08:55:00", 100, 101, 99, 100],
            ["2026-10-12 09:15:00", 100, 101, 99, 100],
            ["2026-10-12 09:20:00", 100, 101, 99, 100],
        ]
    }
    expected_stamp = pd.Timestamp("2026-10-12 03:45:00+00:00")
    monkeypatch.setattr(year_research, "_fetch", lambda *_: payload)

    frame, request = year_research._request_month(
        object(), "NIFTY", "CASH", {expected_stamp}, {day},
        2026, 10, tmp_path / "raw", tmp_path,
    )

    assert len(frame) == 1
    assert frame["timestamp"].iloc[0] == expected_stamp
    assert request["status"] == "DATA_RETURNED"
    assert (tmp_path / request["raw_payload"]).is_file()


def test_fresh_year_analysis_reuses_period_engine_and_seven_candidate_set(tmp_path):
    from app import year_research
    from app.groww_data import DATA_COLUMNS

    stamps = pd.date_range(
        "2026-10-12 09:15", periods=75, freq="5min", tz=run_research.IST,
    ).tz_convert("UTC")
    base = tmp_path / "data" / "derived" / "groww_history"
    options_dir = base / "options"
    options_dir.mkdir(parents=True)
    underlying = pd.DataFrame({
        "timestamp": stamps,
        "open": 25020.0, "high": 25030.0, "low": 25010.0, "close": 25020.0,
        "volume": None, "oi": None,
    })
    underlying.to_csv(base / "NIFTY.csv", index=False)

    contracts = []
    for strike, kind in (
        (24950, "CE"), (24900, "CE"), (25100, "PE"), (25150, "PE"),
    ):
        symbol = f"NSE-NIFTY-15Oct26-{strike}-{kind}"
        contracts.append({
            "symbol": symbol, "expiry": "2026-10-15",
            "strike": strike, "option_type": kind,
        })
        pd.DataFrame({
            "timestamp": stamps,
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
            "volume": None, "oi": None,
        }, columns=DATA_COLUMNS).to_csv(options_dir / f"{symbol}.csv", index=False)
    (base / "contract_catalog_2026.json").write_text(
        json.dumps({"2026-10-15": contracts}), encoding="utf-8",
    )

    result = year_research.analyze_year(2026, tmp_path)

    assert result["status"] == "ANALYZED"
    assert result["data_completeness"]["fully_usable_days"] == 1, json.dumps({
        "data_completeness": result["data_completeness"],
        "contract_day_coverage": result["contract_day_coverage"],
        "missing_data": result["missing_data"],
    }, indent=2)
    assert result["ekalayava_seven_candidate_shadow"]["unique_canonical_signals"] == 0
    assert len(result["ekalayava_seven_candidate_shadow"]["results"]) == 7


def test_year_study_does_not_authenticate_in_offline_mode(tmp_path, monkeypatch):
    from app import year_research

    monkeypatch.setattr(run_research, "ROOT", tmp_path)
    monkeypatch.setattr(run_research, "_inventory_data", lambda: {})
    monkeypatch.setattr(
        run_research, "_study_evidence",
        lambda years: {"requested_years": years},
    )

    def fake_build_report(title, payload, summary):
        assert title.startswith("NIFTY") and summary
        assert payload["command"] == "study"
        return tmp_path / "report.json", tmp_path / "report.md"

    monkeypatch.setattr(
        run_research, "_build_report", fake_build_report,
    )
    monkeypatch.setattr(
        year_research, "analyze_year",
        lambda year, root: {
            "status": "INSUFFICIENT_DATA", "year": year, "root": str(root),
        },
    )

    assert run_research.study([2025], offline=True) == 0


def test_explicit_year_study_authenticates_and_fetches_missing_data(
    tmp_path, monkeypatch,
):
    from app import groww_auth, year_research

    client = SimpleNamespace(get_user_profile=lambda: {"read_only": True})
    calls = []
    monkeypatch.setattr(run_research, "ROOT", tmp_path)
    monkeypatch.setattr(run_research, "_inventory_data", lambda: {})
    monkeypatch.setattr(
        run_research, "_study_evidence",
        lambda years: {"requested_years": years},
    )

    def fake_build_report(title, payload, summary):
        assert title.startswith("NIFTY") and summary
        assert payload["command"] == "study"
        return tmp_path / "report.json", tmp_path / "report.md"

    monkeypatch.setattr(
        run_research, "_build_report", fake_build_report,
    )
    monkeypatch.setattr(
        year_research, "year_has_fetchable_sessions",
        lambda year: year == 2026,
    )
    monkeypatch.setattr(
        year_research, "local_year_study_complete",
        lambda year, root: year == 999 or root == tmp_path and False,
    )

    def fake_authenticate(config):
        assert config is run_research.CFG
        return client

    monkeypatch.setattr(groww_auth, "authenticate", fake_authenticate)

    def fake_collect(authenticated_client, year, root, progress):
        assert callable(progress)
        calls.append((authenticated_client, year, root))
        return {"months": []}

    monkeypatch.setattr(
        year_research, "collect_year", fake_collect,
    )
    monkeypatch.setattr(
        year_research, "analyze_year",
        lambda year, root: {
            "status": "ANALYZED", "year": year, "root": str(root),
        },
    )

    assert run_research.study([2026]) == 0
    assert calls == [(client, 2026, tmp_path)]


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
