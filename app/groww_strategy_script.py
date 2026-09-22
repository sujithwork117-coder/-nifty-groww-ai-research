# Groww-side PAPER/OBSERVATION script. No order APIs are used.
EXECUTION_ALLOWED=False
PAPER_ONLY=True
def hard_lock():
    if EXECUTION_ALLOWED or not PAPER_ONLY: raise RuntimeError("Execution disabled.")
def on_completed_5m_candle(candle,opening_high,opening_low):
    hard_lock()
    if candle["low"]<opening_low and candle["close"]>candle["open"]:
        return {"strategy":"LEVEL_TO_LEVEL","paper_entry":candle["close"],
                "paper_sl":opening_low-4.0,"paper_target":opening_high,
                "execution":"DISABLED"}
    return None
