import json
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Result:
    total: int = 0
    success: int = 0
    failure: int = 0
    total_latency_ms: float = 0.0


def hit_endpoint(url: str, result: Result, lock: threading.Lock) -> None:
    start = time.perf_counter()
    ok = False
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            ok = 200 <= response.status < 400
    except (urllib.error.URLError, TimeoutError):
        ok = False
    latency_ms = (time.perf_counter() - start) * 1000

    with lock:
        result.total += 1
        result.total_latency_ms += latency_ms
        if ok:
            result.success += 1
        else:
            result.failure += 1


def run(url: str, concurrency: int, requests_per_worker: int) -> dict:
    result = Result()
    lock = threading.Lock()
    threads = []

    for _ in range(concurrency):
        thread = threading.Thread(
            target=lambda: [hit_endpoint(url, result, lock) for _ in range(requests_per_worker)],
            daemon=True,
        )
        threads.append(thread)

    started = time.perf_counter()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    duration = max(0.001, time.perf_counter() - started)

    avg_latency = result.total_latency_ms / result.total if result.total else 0.0
    rps = result.total / duration
    return {
        "target": url,
        "concurrency": concurrency,
        "requests": result.total,
        "success": result.success,
        "failure": result.failure,
        "success_rate": round(result.success / result.total, 4) if result.total else 0.0,
        "avg_latency_ms": round(avg_latency, 2),
        "duration_sec": round(duration, 2),
        "rps": round(rps, 2),
    }


if __name__ == "__main__":
    report = run(url="http://localhost:8100/health", concurrency=2, requests_per_worker=5)
    output = Path(__file__).resolve().parent / "loadtest_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
