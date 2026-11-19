"""Run one algorithm with timing over several repetitions."""

import gc
import statistics
import time

from algorithms import ALGORITHMS


def profile(algorithm_name: str, text: str, pattern: str, repeats: int = 5) -> dict:
    """Time preprocessing and search separately, `repeats` times, and report medians.

    Garbage collection is disabled while measuring so it cannot add noise.
    Comparison counts are deterministic, so they come from the last run.
    """
    preprocess, search = ALGORITHMS[algorithm_name]
    preprocess_times = []
    search_times = []

    gc.disable()
    try:
        for _ in range(repeats):
            t0 = time.perf_counter()
            table, preprocess_comparisons = preprocess(pattern)
            t1 = time.perf_counter()
            result = search(text, pattern, table)
            t2 = time.perf_counter()
            preprocess_times.append((t1 - t0) * 1000)
            search_times.append((t2 - t1) * 1000)
    finally:
        gc.enable()

    preprocess_ms = statistics.median(preprocess_times)
    search_ms = statistics.median(search_times)
    return {
        "algorithm": algorithm_name,
        "matches": result.matches,
        "num_matches": len(result.matches),
        "comparisons": result.comparisons,
        "preprocess_comparisons": preprocess_comparisons,
        "preprocess_ms": preprocess_ms,
        "search_ms": search_ms,
        "total_ms": preprocess_ms + search_ms,
    }
