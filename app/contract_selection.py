import re
def parse_contract(symbol):
    m=re.match(r"^NSE-NIFTY-(\d{2}[A-Za-z]{3}\d{2})-(\d+(?:\.\d+)?)-(CE|PE)$",symbol)
    if not m:return None
    return {"symbol":symbol,"expiry_token":m.group(1),"strike":float(m.group(2)),"option_type":m.group(3)}
def select_itm_contracts(contracts,underlying_open,itm_ranks=(2,3),option_types=("CE","PE")):
    p=[parse_contract(s) for s in contracts]
    p=[x for x in p if x and x["option_type"] in option_types]
    calls=sorted([x for x in p if x["option_type"]=="CE" and x["strike"]<underlying_open],key=lambda x:x["strike"],reverse=True)
    puts=sorted([x for x in p if x["option_type"]=="PE" and x["strike"]>underlying_open],key=lambda x:x["strike"])
    out=[]
    for r in itm_ranks:
        if r<=len(calls): out.append({**calls[r-1],"itm_rank":r})
        if r<=len(puts): out.append({**puts[r-1],"itm_rank":r})
    return out
