from growwapi import GrowwAPI
from .config import CFG

def authenticate(config=CFG):
    api_key=config.api_key.strip()
    api_secret=config.api_secret.strip()
    totp=config.totp.strip()
    if not api_key:
        raise RuntimeError("Set GROWW_API_KEY in .env")
    if api_secret and totp:
        raise RuntimeError("Set only one of GROWW_API_SECRET or GROWW_TOTP")
    if not api_secret and not totp:
        raise RuntimeError("Set GROWW_API_SECRET or GROWW_TOTP in .env")

    try:
        token=GrowwAPI.get_access_token(
            api_key=api_key,
            secret=api_secret or None,
            totp=totp or None,
        )
    except Exception as exc:
        raise RuntimeError(f"Groww authentication failed: {exc}") from exc
    if not token:
        raise RuntimeError("Groww authentication returned an empty access token")
    return GrowwAPI(token)
