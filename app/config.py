from dataclasses import dataclass
from dotenv import load_dotenv
import os
load_dotenv()
def _csv(name, cast=str):
    return [cast(x.strip()) for x in os.getenv(name, "").split(",") if x.strip()]
@dataclass(frozen=True)
class Config:
    api_key: str=os.getenv("GROWW_API_KEY","")
    api_secret: str=os.getenv("GROWW_API_SECRET","")
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
