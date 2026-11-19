"""Graphs from results.csv. Each function returns a matplotlib Figure so app.py can reuse it."""

import os

import pandas as pd
from matplotlib.figure import Figure

# Same colour for each algorithm in every graph.
COLORS = {"Naive": "#d62728", "KMP": "#1f77b4", "Boyer-Moore": "#2ca02c"}
ALGORITHM_ORDER = list(COLORS)


def _line_per_algorithm(ax, data: pd.DataFrame, x: str, y: str) -> None:
    """Draw one line per algorithm on the given axes."""
    for name in ALGORITHM_ORDER:
        rows = data[data["algorithm"] == name].sort_values(x)
        ax.plot(rows[x], rows[y], marker="o", label=name, color=COLORS[name])
    ax.grid(alpha=0.3)
    ax.legend()


def plot_exp1(df: pd.DataFrame) -> Figure:
    """Total time vs text length, one subplot per dataset."""
    data = df[df["experiment"] == 1]
    datasets = list(data["dataset"].unique())
    fig = Figure(figsize=(6 * len(datasets), 4.5))
    axes = fig.subplots(1, len(datasets), squeeze=False)[0]
    for ax, dataset in zip(axes, datasets):
        _line_per_algorithm(ax, data[data["dataset"] == dataset], "text_len", "total_ms")
        ax.set_title(f"{dataset}")
        ax.set_xlabel("Text length (characters)")
        ax.set_ylabel("Total time (ms)")
    fig.suptitle("Exp 1: Time vs text length (pattern length 10)")
    fig.tight_layout()
    return fig


def plot_exp2(df: pd.DataFrame) -> Figure:
    """Comparisons vs pattern length, one subplot per dataset."""
    data = df[df["experiment"] == 2]
    datasets = list(data["dataset"].unique())
    fig = Figure(figsize=(6 * len(datasets), 4.5))
    axes = fig.subplots(1, len(datasets), squeeze=False)[0]
    for ax, dataset in zip(axes, datasets):
        _line_per_algorithm(ax, data[data["dataset"] == dataset], "pattern_len", "comparisons")
        ax.set_xscale("log", base=2)
        ax.set_title(f"{dataset}")
        ax.set_xlabel("Pattern length (characters, log scale)")
        ax.set_ylabel("Character comparisons")
    fig.suptitle("Exp 2: Comparisons vs pattern length")
    fig.tight_layout()
    return fig


def plot_exp3(df: pd.DataFrame) -> Figure:
    """Grouped bars: comparisons per alphabet, one bar per algorithm."""
    data = df[df["experiment"] == 3]
    datasets = list(data["dataset"].unique())
    fig = Figure(figsize=(8, 4.5))
    ax = fig.subplots()
    width = 0.27
    for k, name in enumerate(ALGORITHM_ORDER):
        rows = data[data["algorithm"] == name].set_index("dataset").reindex(datasets)
        positions = [i + (k - 1) * width for i in range(len(datasets))]
        ax.bar(positions, rows["comparisons"], width, label=name, color=COLORS[name])
    ax.set_xticks(range(len(datasets)), datasets)
    ax.set_xlabel("Dataset (alphabet: binary=2, dna=4, english=26, ascii=95)")
    ax.set_ylabel("Character comparisons")
    ax.set_title("Exp 3: Comparisons vs alphabet size (pattern length 16)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_exp4(df: pd.DataFrame) -> Figure:
    """Worst case: comparisons vs pattern length."""
    data = df[df["experiment"] == 4]
    fig = Figure(figsize=(8, 4.5))
    ax = fig.subplots()
    _line_per_algorithm(ax, data, "pattern_len", "comparisons")
    ax.set_xlabel("Pattern length (characters)")
    ax.set_ylabel("Character comparisons")
    ax.set_title("Exp 4: Worst case (text 'aaa...a', pattern 'aa...ab')")
    fig.tight_layout()
    return fig


def plot_exp5(df: pd.DataFrame) -> Figure | None:
    """Real text: total time vs pattern length. None if there is no real-text data."""
    data = df[df["experiment"] == 5]
    if data.empty:
        return None
    fig = Figure(figsize=(8, 4.5))
    ax = fig.subplots()
    _line_per_algorithm(ax, data, "pattern_len", "total_ms")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Pattern length (characters, log scale)")
    ax.set_ylabel("Total time (ms)")
    ax.set_title("Exp 5: Real text (book)")
    fig.tight_layout()
    return fig


def plot_preprocess_vs_search(df: pd.DataFrame) -> Figure:
    """Stacked bars of preprocessing and search time (Exp 2, english, pattern length 64)."""
    data = df[(df["experiment"] == 2) & (df["dataset"] == "english") & (df["pattern_len"] == 64)]
    data = data.set_index("algorithm").reindex(ALGORITHM_ORDER)
    fig = Figure(figsize=(7, 4.5))
    ax = fig.subplots()
    ax.bar(ALGORITHM_ORDER, data["preprocess_ms"], label="Preprocessing", color="#9467bd")
    ax.bar(ALGORITHM_ORDER, data["search_ms"], bottom=data["preprocess_ms"], label="Search", color="#ff7f0e")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Preprocessing vs search time (english, pattern length 64)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


# Output filename -> plotting function (also used by app.py).
PLOTS = {
    "exp1_time_vs_text_length.png": plot_exp1,
    "exp2_comparisons_vs_pattern_length.png": plot_exp2,
    "exp3_alphabet_size.png": plot_exp3,
    "exp4_worst_case.png": plot_exp4,
    "exp5_real_text.png": plot_exp5,
    "preprocess_vs_search.png": plot_preprocess_vs_search,
}


def make_all_plots(csv_path: str = "results/results.csv", out_dir: str = "results/") -> list[str]:
    """Read the CSV and save every graph as PNG. Returns the saved paths."""
    df = pd.read_csv(csv_path)
    os.makedirs(out_dir, exist_ok=True)
    saved = []
    for filename, plot in PLOTS.items():
        fig = plot(df)
        if fig is None:
            print(f"Skipping {filename}: no data")
            continue
        path = os.path.join(out_dir, filename)
        fig.savefig(path, dpi=120)
        saved.append(path)
    return saved
