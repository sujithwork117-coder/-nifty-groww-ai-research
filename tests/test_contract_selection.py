from unittest.mock import Mock

from app.contract_selection import discover_itm_contracts,select_daily_itm_contracts,select_itm_contracts


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
    assert {item["underlying"] for item in selected} == {"NIFTY"}


def _daily_chain(expiry, missing=()):
    from datetime import datetime
    code=datetime.strptime(expiry,"%Y-%m-%d").strftime("%d%b%y")
    return [f"NSE-NIFTY-{code}-{strike}-{kind}"
            for strike in (9900,9950,10000,10050,10100,10150)
            for kind in ("CE","PE") if (strike,kind) not in missing]


def test_daily_selector_uses_nearest_nonexpired_chain_and_rolls_by_date():
    groww=Mock()
    groww.EXCHANGE_NSE="NSE"
    groww.get_expiries.return_value={"expiries":["2026-09-08","2026-09-15"]}
    groww.get_contracts.side_effect=lambda **kw:{"contracts":_daily_chain(kw["expiry_date"])}

    expiry_day=select_daily_itm_contracts(groww,10020,"2026-09-08")
    next_day=select_daily_itm_contracts(groww,10020,"2026-09-09")

    assert expiry_day["expiry"]=="2026-09-08"
    assert next_day["expiry"]=="2026-09-15"
    assert len(expiry_day["contracts"])==4 and len(next_day["contracts"])==4
    assert [call.kwargs["expiry_date"] for call in groww.get_contracts.call_args_list]==[
        "2026-09-08","2026-09-15"]


def test_daily_selector_does_not_substitute_missing_exact_itm_rank():
    groww=Mock()
    groww.EXCHANGE_NSE="NSE"
    groww.get_expiries.return_value={"expiries":["2026-09-08"]}
    groww.get_contracts.return_value={"contracts":_daily_chain("2026-09-08",missing={(9900,"CE")})}

    result=select_daily_itm_contracts(groww,10020,"2026-09-08")

    assert ("CE",3) in result["missing"]
    assert not any(item["option_type"]=="CE" and item["itm_rank"]==3 for item in result["contracts"])
    assert {item["itm_rank"] for item in result["contracts"] if item["option_type"]=="CE"}=={2}


def test_daily_selector_rejects_symbol_from_another_expiry():
    groww=Mock()
    groww.EXCHANGE_NSE="NSE"
    groww.get_expiries.return_value={"expiries":["2026-09-08"]}
    groww.get_contracts.return_value={"contracts":_daily_chain("2026-09-15")}

    import pytest
    with pytest.raises(ValueError,match="symbol expiry does not match"):
        select_daily_itm_contracts(groww,10020,"2026-09-01")
