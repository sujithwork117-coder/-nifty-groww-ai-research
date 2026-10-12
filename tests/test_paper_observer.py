from datetime import datetime
from types import SimpleNamespace

from app.paper_observer import GrowwPaperObserver


class FakeGroww:
    EXCHANGE_NSE = "NSE"
    SEGMENT_CASH = "CASH"
    SEGMENT_FNO = "FNO"

    def __init__(self, fail_symbol=None):
        self.fail_symbol = fail_symbol
        self.catalog_calls = 0

    def get_expiries(self, **kwargs):
        self.catalog_calls += 1
        return {"expiries": ["2026-10-15"]}

    def get_contracts(self, **kwargs):
        return {"contracts": [f"NSE-NIFTY-15Oct26-{strike}-{kind}"
                               for strike in (9900, 9950, 10000, 10050, 10100, 10150)
                               for kind in ("CE", "PE")]}

    def get_historical_candles(self, **kwargs):
        symbol = kwargs["groww_symbol"]
        if symbol == self.fail_symbol:
            raise ConnectionError("sanitized provider test error")
        is_option = "-CE" in symbol or "-PE" in symbol
        candles = [
            ["2026-10-12T09:15:00+05:30", 100 if is_option else 10020,
             110 if is_option else 10040, 95 if is_option else 10010, 100 if is_option else 10030, 1, 0],
            ["2026-10-12T09:20:00+05:30", 100 if is_option else 10030,
             103 if is_option else 10050, 94 if is_option else 10020, 98 if is_option else 10040, 1, 0],
            ["2026-10-12T09:25:00+05:30", 98 if is_option else 10040,
             104 if is_option else 10060, 97 if is_option else 10030, 102 if is_option else 10050, 1, 0],
            # This bucket has not closed at 09:32 and must not reach the engine.
            ["2026-10-12T09:30:00+05:30", 102 if is_option else 10050,
             108 if is_option else 10070, 100 if is_option else 10040, 106 if is_option else 10060, 1, 0],
        ]
        return {"candles": candles}


def make_config():
    return SimpleNamespace(
        execution_allowed=False, paper_only=True, kill_switch=False,
        underlying="NIFTY", itm_ranks=(2, 3), option_types=("CE", "PE"),
        level_sl_points=4, level_entry_start="09:15", level_entry_end="11:00",
        ek_start="09:15", ek_end="15:15", ekalayava_sl_buffer_points=None,
        ekalayava_experimental_exit_simulation=False, model_version="test-model",
        strategy_version="observer-test-v1", segment_cash="CASH", segment_fno="FNO",
    )


def test_observer_selects_exact_daily_contracts_processes_closed_bars_and_recovers(tmp_path):
    groww = FakeGroww()
    now = datetime.fromisoformat("2026-10-12T09:32:00+05:30")
    observer = GrowwPaperObserver(groww, make_config(), tmp_path)
    status = observer.run_once(now)

    assert status["health"] == "HEALTHY"
    assert status["selected_expiry"] == "2026-10-15"
    assert len(status["selected_contracts"]) == 4
    assert len(status["signals"]) == 4
    assert all(event["strategy_version"] == "observer-test-v1" for event in status["signals"])
    assert all(event["setup_id"] == event["event_id"] for event in status["signals"])
    assert all(event["close_time"].endswith("09:30:00+05:30") for event in status["signals"])
    assert all(value.endswith("09:25:00+05:30") for value in status["last_option_candles"].values())
    assert observer.run_once(now)["signals"] == status["signals"]

    restarted = GrowwPaperObserver(groww, make_config(), tmp_path)
    resumed = restarted.run_once(now)
    assert resumed["signals"] == []
    journal = list(tmp_path.rglob("paper_journal.jsonl"))[0]
    records = [__import__("json").loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
    assert sum(record["event_type"] == "SIGNAL" for record in records) == 4
    assert sum(record["event_type"] == "DUPLICATE_CANDLES_SUPPRESSED" for record in records) == 4


def test_observer_skips_failed_exact_contract_and_keeps_other_streams_running(tmp_path):
    fail = "NSE-NIFTY-15Oct26-9950-CE"
    groww = FakeGroww(fail_symbol=fail)
    observer = GrowwPaperObserver(groww, make_config(), tmp_path)
    status = observer.run_once(datetime.fromisoformat("2026-10-12T09:30:00+05:30"))

    assert status["health"] == "DEGRADED_OPTION_DATA"
    assert len(status["selected_contracts"]) == 4
    assert len(status["signals"]) == 3
    assert {item["symbol"] for item in status["skipped"] if "symbol" in item} == {fail}
    assert status["paper_positions"][fail]["stale"] is True


def test_observer_quarantines_invalid_candle_sequence_and_continues(tmp_path):
    class InvalidBarGroww(FakeGroww):
        def get_historical_candles(self, **kwargs):
            payload = super().get_historical_candles(**kwargs)
            if kwargs["groww_symbol"] == "NSE-NIFTY-15Oct26-9950-CE":
                payload["candles"][1][0] = "2026-10-12T09:22:00+05:30"
            return payload

    observer = GrowwPaperObserver(InvalidBarGroww(), make_config(), tmp_path)
    status = observer.run_once(datetime.fromisoformat("2026-10-12T09:32:00+05:30"))

    assert status["health"] == "DEGRADED_OPTION_DATA"
    assert len(status["signals"]) == 3
    assert status["paper_positions"]["NSE-NIFTY-15Oct26-9950-CE"]["stale"] is True
    assert any(item["reason"].startswith("INVALID_CANDLE_SEQUENCE_") for item in status["skipped"])


def test_observer_marks_stale_option_stream_and_disables_its_entries(tmp_path):
    class StaleOptionGroww(FakeGroww):
        def get_historical_candles(self, **kwargs):
            payload = super().get_historical_candles(**kwargs)
            if kwargs["groww_symbol"] == "NSE-NIFTY-15Oct26-9950-CE":
                payload["candles"] = payload["candles"][:2]
            return payload

    observer = GrowwPaperObserver(StaleOptionGroww(), make_config(), tmp_path)
    status = observer.run_once(datetime.fromisoformat("2026-10-12T09:32:00+05:30"))

    assert status["health"] == "DEGRADED_OPTION_DATA"
    stale_symbol = "NSE-NIFTY-15Oct26-9950-CE"
    assert status["paper_positions"][stale_symbol]["stale"] is True
    state_file = list(tmp_path.rglob("*.json"))
    engine_state = next(__import__("json").loads(path.read_text()) for path in state_file
                        if __import__("json").loads(path.read_text()).get("symbol") == stale_symbol)
    assert engine_state["entries_disabled"] is True
    assert engine_state["data_quality_status"] == "STALE_OPTION_CANDLES"
    records = [__import__("json").loads(line) for line in
               list(tmp_path.rglob("paper_journal.jsonl"))[0].read_text().splitlines()]
    assert any(record["event_type"] == "STALE_CANDLE_FEED" and record["symbol"] == stale_symbol
               for record in records)


def test_observer_run_forever_reauthenticates_after_transient_failure(tmp_path):
    class FailOnceGroww(FakeGroww):
        def __init__(self):
            super().__init__()
            self.underlying_calls = 0

        def get_historical_candles(self, **kwargs):
            if kwargs["groww_symbol"] == "NSE-NIFTY":
                self.underlying_calls += 1
                if self.underlying_calls == 1:
                    raise ConnectionError("transient")
            return super().get_historical_candles(**kwargs)

    first = FailOnceGroww()
    replacement = FakeGroww()
    created = []
    sleeps = []
    times = iter([
        datetime.fromisoformat("2026-10-12T09:32:00+05:30"),
        datetime.fromisoformat("2026-10-12T09:32:00+05:30"),
    ])
    clock_calls = []
    observer = GrowwPaperObserver(
        first, make_config(), tmp_path,
        groww_factory=lambda: (created.append(True) or replacement),
    )
    status = observer.run_forever(
        poll_seconds=2, max_backoff_seconds=8,
        now_fn=lambda: (clock_calls.append(True) or next(times)),
        stop_requested=lambda: len(clock_calls) >= 2,
        sleeper=sleeps.append,
    )

    assert created == [True]
    assert sleeps == [2, 2]
    assert status["health"] == "STOPPED_BY_OPERATOR"
    assert len(status["signals"]) == 4
    journal = list(tmp_path.rglob("paper_journal.jsonl"))[0]
    events = [__import__("json").loads(line)["event_type"] for line in journal.read_text().splitlines()]
    assert "RECONNECT_ATTEMPT" in events
    assert "READ_ONLY_CLIENT_RECREATED" in events
