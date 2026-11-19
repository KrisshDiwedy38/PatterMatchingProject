"""Experiment definitions. Each experiment varies one variable and fixes the rest."""

import os

import pandas as pd

from algorithms import ALGORITHMS
from datasets import get_dataset, load_real_text, pattern_from_text, worst_case_pattern
from profiler import profile

SEED = 42
REPEATS = 5

EXPERIMENT_NAMES = {
    1: "Text length scaling",
    2: "Pattern length",
    3: "Alphabet size",
    4: "Worst case",
    5: "Real text",
}

# Experiment settings (full-size; --quick divides text lengths by 10).
EXP1_DATASETS = ["dna", "english"]
EXP1_TEXT_LENS = [10_000, 50_000, 100_000, 250_000, 500_000]
EXP1_PATTERN_LEN = 10

EXP2_DATASETS = ["dna", "english"]
EXP2_PATTERN_LENS = [2, 4, 8, 16, 32, 64, 128]
EXP2_TEXT_LEN = 100_000

EXP3_DATASETS = ["binary", "dna", "english", "ascii"]
EXP3_TEXT_LEN = 100_000
EXP3_PATTERN_LEN = 16

EXP4_PATTERN_LENS = [2, 4, 8, 16, 32, 64]
EXP4_TEXT_LEN = 50_000

EXP5_PATTERN_LENS = [4, 8, 16, 32, 64]
EXP5_TEXT_LEN = 200_000

CSV_COLUMNS = [
    "experiment", "dataset", "text_len", "pattern_len", "algorithm", "comparisons",
    "preprocess_comparisons", "preprocess_ms", "search_ms", "total_ms", "num_matches",
]


def _run_case(experiment: int, dataset: str, text: str, pattern: str, repeats: int) -> list[dict]:
    """Profile every algorithm on one (text, pattern) pair and check they agree."""
    rows = []
    first_name = None
    first_matches = None
    for name in ALGORITHMS:
        result = profile(name, text, pattern, repeats)
        if first_matches is None:
            first_name, first_matches = name, result["matches"]
        elif result["matches"] != first_matches:
            raise AssertionError(
                f"{name} and {first_name} disagree on matches: experiment {experiment}, "
                f"dataset={dataset}, text_len={len(text)}, pattern_len={len(pattern)}"
            )
        rows.append({
            "experiment": experiment,
            "dataset": dataset,
            "text_len": len(text),
            "pattern_len": len(pattern),
            "algorithm": name,
            **{key: result[key] for key in CSV_COLUMNS[5:]},
        })
        print(f"[Exp {experiment}] {dataset} | text_len={len(text)} | pattern_len={len(pattern)} | {name} done")
    return rows


def run_experiments(quick: bool = False) -> pd.DataFrame:
    """Run all five experiments and return one row per (case, algorithm)."""
    scale = 10 if quick else 1
    repeats = 2 if quick else REPEATS
    rows = []

    # Exp 1: text length scaling.
    for dataset in EXP1_DATASETS:
        for text_len in EXP1_TEXT_LENS:
            text = get_dataset(dataset, text_len // scale, SEED)
            pattern = pattern_from_text(text, EXP1_PATTERN_LEN, SEED)
            rows += _run_case(1, dataset, text, pattern, repeats)

    # Exp 2: pattern length.
    for dataset in EXP2_DATASETS:
        text = get_dataset(dataset, EXP2_TEXT_LEN // scale, SEED)
        for pattern_len in EXP2_PATTERN_LENS:
            pattern = pattern_from_text(text, pattern_len, SEED)
            rows += _run_case(2, dataset, text, pattern, repeats)

    # Exp 3: alphabet size.
    for dataset in EXP3_DATASETS:
        text = get_dataset(dataset, EXP3_TEXT_LEN // scale, SEED)
        pattern = pattern_from_text(text, EXP3_PATTERN_LEN, SEED)
        rows += _run_case(3, dataset, text, pattern, repeats)

    # Exp 4: worst case ("aaa...a" text, "aa...ab" pattern).
    text = get_dataset("worst_case", EXP4_TEXT_LEN // scale, SEED)
    for pattern_len in EXP4_PATTERN_LENS:
        rows += _run_case(4, "worst_case", text, worst_case_pattern(pattern_len), repeats)

    # Exp 5: real text (skipped if there is no book).
    book = load_real_text()
    if book is None:
        print("[Exp 5] WARNING: data/book.txt not found, skipping real-text experiment (see data/README.md)")
    else:
        text = book[:EXP5_TEXT_LEN // scale]
        for pattern_len in EXP5_PATTERN_LENS:
            pattern = pattern_from_text(text, pattern_len, SEED)
            rows += _run_case(5, "real_text", text, pattern, repeats)

    return pd.DataFrame(rows, columns=CSV_COLUMNS)


def save_results(df: pd.DataFrame, path: str = "results/results.csv") -> None:
    """Write the results to CSV with the fixed column order."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df[CSV_COLUMNS].to_csv(path, index=False)
