import pandas as pd

from app.data_quality import align_candles,quality_report


def data():
    return pd.DataFrame([
        {"timestamp":"2026-09-01T09:15:00Z","open":100,"high":101,"low":99,"close":100,"symbol":"A"},
        {"timestamp":"2026-09-01T09:25:00Z","open":101,"high":102,"low":100,"close":101,"symbol":"A"},
        {"timestamp":"2026-09-01T09:25:00Z","open":101,"high":102,"low":100,"close":101,"symbol":"A"},
    ])


def test_quality_report_counts_gaps_duplicates_and_contracts():
    report=quality_report(data(),contract_column="symbol")

    assert report["total_candles"]==3
    assert report["duplicate_count"]==1
    assert report["missing_intervals"]==1
    assert report["contract_count"]==1
    assert report["invalid_ohlc_count"]==0


def test_alignment_uses_exact_timestamps_and_marks_missing_rows():
    underlying=data().iloc[:2]
    option=data().iloc[1:2]

    aligned=align_candles(underlying,option)

    assert len(aligned)==2
    assert set(aligned["candle_presence"])=={"both","left_only"}
    assert "underlying_close" in aligned
    assert "option_close" in aligned