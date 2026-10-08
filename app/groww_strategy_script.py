# Groww-side PAPER/OBSERVATION script. No order APIs are used.
EXECUTION_ALLOWED=False
PAPER_ONLY=True

def hard_lock():
    if EXECUTION_ALLOWED or not PAPER_ONLY: raise RuntimeError("Execution disabled.")

def on_completed_5m_candle(candle,engine,nifty_price=None):
    hard_lock()
    if candle.get("completed") is not True:
        raise ValueError("Only finalized 5-minute candles may be processed")
    return engine.process_candle(candle,nifty_price=nifty_price)
