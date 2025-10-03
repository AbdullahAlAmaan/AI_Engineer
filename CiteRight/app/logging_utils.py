import time, orjson, sys
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        t1 = time.perf_counter()
        log_json({"metric": "latency", "stage": name, "ms": round((t1 - t0) * 1000, 2)})

def log_json(payload: dict):
    sys.stdout.write(orjson.dumps(payload).decode() + "\n")
    sys.stdout.flush()

