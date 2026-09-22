from growwapi import GrowwAPI
from .config import CFG
def authenticate():
    if not CFG.api_key or not CFG.api_secret:
        raise RuntimeError("Set GROWW_API_KEY and GROWW_API_SECRET in .env")
    token=GrowwAPI.get_access_token(api_key=CFG.api_key,secret=CFG.api_secret)
    return GrowwAPI(token)
