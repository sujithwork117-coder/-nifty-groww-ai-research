from unittest.mock import Mock

from app.contract_selection import discover_itm_contracts,select_itm_contracts


def symbols():
    return [
        "NSE-NIFTY-26SEP26-25000-CE", "NSE-NIFTY-26SEP26-24900-CE", "NSE-NIFTY-26SEP26-24800-CE",
        "NSE-NIFTY-26SEP26-25200-PE", "NSE-NIFTY-26SEP26-25300-PE", "NSE-NIFTY-26SEP26-25400-PE",
        "NSE-NIFTY-26SEP26-25500-CE", "NSE-NIFTY-26SEP26-24500-PE",
    ]


def test_selects_only_second_and_third_itm():
    selected=select_itm_contracts(symbols(),25100)

    assert {(item["option_type"],item["itm_rank"]) for item in selected} == {("CE",2),("CE",3),("PE",2),("PE",3)}
    assert all(item["strike"]<25100 for item in selected if item["option_type"]=="CE")
    assert all(item["strike"]>25100 for item in selected if item["option_type"]=="PE")
    assert all(item["expiry"] is None for item in selected)


def test_discovery_retrieves_expiries_and_contracts():
    groww=Mock()
    groww.EXCHANGE_NSE="NSE"
    groww.get_expiries.return_value={"expiries":["2026-09-24"]}
    groww.get_contracts.return_value={"contracts":[
        {"trading_symbol": symbol, "expiry_date":"2026-09-24"} for symbol in symbols()
    ]}

    selected=discover_itm_contracts(groww,25100)

    groww.get_expiries.assert_called_once_with(exchange="NSE",underlying_symbol="NIFTY")
    groww.get_contracts.assert_called_once_with(exchange="NSE",underlying_symbol="NIFTY",expiry_date="2026-09-24")
    assert len(selected)==4
    assert {item["expiry"] for item in selected} == {"2026-09-24"}