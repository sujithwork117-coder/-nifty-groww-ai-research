import re
from decimal import Decimal, ROUND_FLOOR

CONTRACT_FIELDS=("symbol","expiry","strike","option_type","itm_rank")

def _items(payload,key):
    if isinstance(payload,dict):
        value=payload.get(key)
        if value is not None:return value if isinstance(value,list) else [value]
        for nested in ("data","result"):
            if nested in payload:return _items(payload[nested],key)
    return payload if isinstance(payload,list) else []

def _symbol_parts(symbol):
    match=re.search(r"(?:NSE-)?NIFTY-(?:\d{2}[A-Za-z]{3}\d{2})-(\d+(?:\.\d+)?)-(CE|PE)$",str(symbol))
    if not match:return None
    return float(match.group(1)),match.group(2)

def parse_contract(contract,expiry=None):
    if isinstance(contract,str):
        symbol=contract
        parts=_symbol_parts(symbol)
        if not parts:return None
        strike,option_type=parts
        return {"symbol":symbol,"expiry":expiry,"strike":strike,"option_type":option_type}
    if not isinstance(contract,dict):return None
    symbol=contract.get("symbol") or contract.get("trading_symbol") or contract.get("groww_symbol")
    parts=_symbol_parts(symbol) if symbol else None
    strike=contract.get("strike",contract.get("strike_price"))
    option_type=contract.get("option_type",contract.get("instrument_type"))
    if parts:
        strike=strike if strike is not None else parts[0]
        option_type=option_type if option_type in ("CE","PE") else parts[1]
    if not symbol or strike is None or option_type not in ("CE","PE"):return None
    return {"symbol":symbol,"expiry":contract.get("expiry",contract.get("expiry_date",expiry)),
            "strike":float(strike),"option_type":option_type}

def select_itm_contracts(contracts,underlying_open,itm_ranks=(2,3),option_types=("CE","PE"),expiry=None):
    selected, _, _ = select_itm_contracts_from_ladder(
        contracts, underlying_open, itm_ranks, option_types, expiry)
    return selected


def select_itm_contracts_from_ladder(contracts, underlying_open, itm_ranks=(2, 3),
                                     option_types=("CE", "PE"), expiry=None):
    """Select only exact 2nd/3rd strikes on the catalog's observed strike grid.

    The historical contracts endpoint can return a sparse set. Ranking that
    sparse list would silently substitute a farther strike, so missing ladder
    entries are omitted and reported by the caller as unavailable.
    """
    if any(rank < 1 for rank in itm_ranks):
        raise ValueError("ITM ranks must be positive")
    parsed = [parse_contract(contract, expiry) for contract in contracts]
    parsed = [item for item in parsed if item and item["option_type"] in option_types]
    strikes = sorted({Decimal(str(item["strike"])) for item in parsed})
    increments = [b - a for a, b in zip(strikes, strikes[1:]) if b > a]
    if not increments:
        return [], None, {}
    step = min(increments)
    offset = strikes[0] % step
    spot = Decimal(str(underlying_open))
    below = offset + ((spot - offset) / step).to_integral_value(rounding=ROUND_FLOOR) * step
    if below >= spot:
        below -= step
    above = below + step
    expected = {}
    for rank in itm_ranks:
        expected[("CE", rank)] = below - (rank - 1) * step
        expected[("PE", rank)] = above + (rank - 1) * step
    out = []
    for (option_type, rank), strike in expected.items():
        match = next((item for item in parsed if item["option_type"] == option_type
                      and Decimal(str(item["strike"])) == strike), None)
        if match:
            out.append({**{field: match.get(field) for field in CONTRACT_FIELDS}, "itm_rank": rank})
    return out, float(step), {f"{kind}_ITM{rank}": float(strike)
                              for (kind, rank), strike in expected.items()}

def discover_itm_contracts(groww,underlying_price,underlying="NIFTY",expiry_date=None,itm_ranks=(2,3),option_types=("CE","PE")):
    expiries=_items(groww.get_expiries(exchange=groww.EXCHANGE_NSE,underlying_symbol=underlying),"expiries")
    selected=[expiry_date] if expiry_date else expiries
    result=[]
    for expiry in selected:
        contracts=_items(groww.get_contracts(exchange=groww.EXCHANGE_NSE,underlying_symbol=underlying,expiry_date=expiry),"contracts")
        selected, _, _ = select_itm_contracts_from_ladder(
            contracts, underlying_price, itm_ranks, option_types, expiry)
        result.extend({**contract,"underlying":underlying} for contract in selected)
    return result
