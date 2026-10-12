import json

from app.journal import PAPER_RECORD_FIELDS, append_paper_record


def test_paper_journal_is_idempotent_and_persists_complete_json_lines(tmp_path):
    path = tmp_path / "paper_journal.jsonl"
    event = {
        "record_id": "record-1", "event_id": "signal-1", "setup_id": "signal-1",
        "event_type": "SIGNAL", "strategy": "EKALAYAVA", "symbol": "exact-symbol",
        "date": "2026-10-12", "timestamp": "2026-10-12T09:30:00+05:30",
        "entry": 105.5, "structural_low_price": 99.0,
        "structural_low_distance_points": 6.5, "paper_only": True,
    }

    assert append_paper_record(event, path, "test-model") is True
    assert append_paper_record(event, path, "test-model") is False
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert set(record) == set(PAPER_RECORD_FIELDS)
    assert record["setup_id"] == "signal-1"
    assert record["structural_low_distance_points"] == 6.5
    assert record["execution"] is None
    assert record["paper_only"] is True


def test_paper_journal_can_append_after_an_incomplete_trailing_line(tmp_path):
    path = tmp_path / "paper_journal.jsonl"
    path.write_text('{"partial":', encoding="utf-8")
    event = {"record_id": "record-2", "event_id": "signal-2", "event_type": "SIGNAL"}

    assert append_paper_record(event, path, "test-model") is True
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == '{"partial":'
    assert json.loads(lines[1])["record_id"] == "record-2"
