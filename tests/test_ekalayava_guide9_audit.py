from tools.run_ekalayava_guide9_audit import _max_drawdown, _net_metrics


def test_round_trip_cost_sensitivity_subtracts_one_cost_per_trade():
    rows = [{"points": 10.0}, {"points": -4.0}]

    no_cost = _net_metrics(rows, 0.0)
    one_point = _net_metrics(rows, 1.0)

    assert no_cost["gross_points"] == 6.0
    assert one_point["net_points_scenario"] == 4.0
    assert one_point["net_expectancy_per_trade_scenario"] == 2.0


def test_drawdown_uses_the_chronological_cumulative_equity_path():
    assert _max_drawdown([5.0, -8.0, 4.0]) == 8.0
