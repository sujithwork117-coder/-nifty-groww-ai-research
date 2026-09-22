import re

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
    parsed=[parse_contract(contract,expiry) for contract in contracts]
    parsed=[x for x in parsed if x and x["option_type"] in option_types]
    calls=sorted([x for x in parsed if x["option_type"]=="CE" and x["strike"]<underlying_open],key=lambda x:x["strike"],reverse=True)
    puts=sorted([x for x in parsed if x["option_type"]=="PE" and x["strike"]>underlying_open],key=lambda x:x["strike"])
    out=[]
    for rank in itm_ranks:
        if rank<1:raise ValueError("ITM ranks must be positive")
        if rank<=len(calls):out.append({**calls[rank-1],"itm_rank":rank})
        if rank<=len(puts):out.append({**puts[rank-1],"itm_rank":rank})
    return [{field:contract.get(field) for field in CONTRACT_FIELDS} for contract in out]

def discover_itm_contracts(groww,underlying_price,underlying="NIFTY",expiry_date=None,itm_ranks=(2,3),option_types=("CE","PE")):
    expiries=_items(groww.get_expiries(exchange=groww.EXCHANGE_NSE,underlying_symbol=underlying),"expiries")
    selected=[expiry_date] if expiry_date else expiries
    result=[]
    for expiry in selected:
        contracts=_items(groww.get_contracts(exchange=groww.EXCHANGE_NSE,underlying_symbol=underlying,expiry_date=expiry),"contracts")
        result.extend({**contract,"underlying":underlying} for contract in select_itm_contracts(contracts,underlying_price,itm_ranks,option_types,expiry))
    return result
