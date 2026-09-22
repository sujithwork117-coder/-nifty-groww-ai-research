from dataclasses import dataclass
from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv()

def _secret_file_values(path="secrets.txt"):
    values={}
    secret_file=Path(path)
    if not secret_file.exists():return values
    for raw_line in secret_file.read_text(encoding="utf-8").splitlines():
        line=raw_line.strip()
        if not line or line.startswith("#"):continue
        if "=" in line:
            key,value=line.split("=",1);key=key.strip();value=value.strip()
            if key in {"GROWW_API_KEY","GROWW_API_SECRET","GROWW_TOTP"}:values[key]=value
        elif " - " in line:
            label,value=line.split(" - ",1);label=label.strip().lower().replace(" ","_")
            key={"api_key":"GROWW_API_KEY","api_secret":"GROWW_API_SECRET","totp":"GROWW_TOTP"}.get(label)
            if key:values[key]=value.strip()
    return values

_secret_values=_secret_file_values()
def _credential(name):
    return os.getenv(name) or _secret_values.get(name,"")

def _csv(name, cast=str):
    return [cast(x.strip()) for x in os.getenv(name, "").split(",") if x.strip()]
@dataclass(frozen=True)
class Config:
    api_key: str=_credential("GROWW_API_KEY")
    api_secret: str=_credential("GROWW_API_SECRET")
    totp: str=_credential("GROWW_TOTP")
    underlying: str=os.getenv("UNDERLYING","NIFTY")
    exchange: str=os.getenv("EXCHANGE","NSE")
    segment_fno: str=os.getenv("SEGMENT_FNO","FNO")
    segment_cash: str=os.getenv("SEGMENT_CASH","CASH")
    candle_interval: str=os.getenv("CANDLE_INTERVAL","5minute")
    history_days: int=int(os.getenv("HISTORY_DAYS","30"))
    history_chunk_days: int=int(os.getenv("HISTORY_CHUNK_DAYS","14"))
    itm_ranks: tuple=tuple(_csv("ITM_RANKS",int) or [2,3])
    option_types: tuple=tuple(_csv("OPTION_TYPES") or ["CE","PE"])
    expiry_date: str=os.getenv("EXPIRY_DATE","")
    level_sl_points: float=float(os.getenv("LEVEL_SL_POINTS","4"))
    level_entry_start: str=os.getenv("LEVEL_ENTRY_START","09:15")
    level_entry_end: str=os.getenv("LEVEL_ENTRY_END","11:00")
    ek_start: str=os.getenv("EKALAYAVA_START","09:15")
    ek_end: str=os.getenv("EKALAYAVA_END","15:15")
    execution_allowed: bool=os.getenv("EXECUTION_ALLOWED","false").lower()=="true"
    paper_only: bool=os.getenv("PAPER_ONLY","true").lower()=="true"
    kill_switch: bool=os.getenv("KILL_SWITCH","false").lower()=="true"
    model_version: str=os.getenv("MODEL_VERSION","v001")
CFG=Config()
if CFG.execution_allowed or not CFG.paper_only:
    raise RuntimeError("SAFETY LOCK: research build requires EXECUTION_ALLOWED=false and PAPER_ONLY=true.")
