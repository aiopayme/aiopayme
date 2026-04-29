import time

def time_to_payme(ts: int | float | None = None) -> int:
    if ts is None:
        return int(time.time() * 1000)
    return int(ts * 1000)

def time_from_payme(ms: int) -> float:
    return ms / 1000