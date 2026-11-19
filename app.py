"""Streamlit dashboard: run experiments and compare results."""

import os

import pandas as pd
import streamlit as st

import benchmark
import plots
from algorithms import ALGORITHMS
from datasets import BOOK_PATH, DATASET_NAMES, get_dataset, pattern_from_text, worst_case_pattern
from profiler import profile

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "results.csv")

# Saved graph -> (tab label, question it answers, takeaway).
GRAPHS = {
    "exp1_time_vs_text_length.png": (
        "Text length", "Does doubling the text double the time?",
        "All three grow linearly with text length; Boyer-Moore's skips make its line the flattest.",
    ),
    "exp2_comparisons_vs_pattern_length.png": (
        "Pattern length", "Do longer patterns help?",
        "Longer patterns let Boyer-Moore skip further, so its comparisons fall. "
        "Naive and KMP stay roughly flat at about one comparison per text character.",
    ),
    "exp3_alphabet_size.png": (
        "Alphabet", "Does the kind of text matter?",
        "Bigger alphabets mean earlier mismatches and bigger bad-character shifts. "
        "Boyer-Moore benefits most; on binary text its skips are short.",
    ),
    "exp4_worst_case.png": (
        "Worst case", "What happens on nasty input ('aaa...a' text, 'aa...ab' pattern)?",
        "Naive re-checks the whole pattern at every position, so it grows with pattern length. "
        "KMP stays linear in the text length. Boyer-Moore also stays low here: "
        "it checks right to left and the final 'b' fails straight away.",
    ),
    "exp5_real_text.png": (
        "Real text", "Does it hold on a real book, not random letters?",
        "On real English text Boyer-Moore gets faster as the pattern gets longer.",
    ),
    "preprocess_vs_search.png": (
        "Preprocessing", "Is building the tables expensive?",
        "Preprocessing is O(m) and tiny next to the O(n) search, so it barely shows on the bars.",
    ),
}

TABLE_COLUMNS = {
    "run": st.column_config.NumberColumn("Run", format="#%d"),
    "dataset": st.column_config.TextColumn("Dataset"),
    "text_len": st.column_config.NumberColumn("Text length", format="localized"),
    "pattern_len": st.column_config.NumberColumn("Pattern length"),
    "seed": st.column_config.NumberColumn("Seed", format="%d"),
    "algorithm": st.column_config.TextColumn("Algorithm"),
    "comparisons": st.column_config.NumberColumn("Comparisons", format="localized"),
    "preprocess_ms": st.column_config.NumberColumn("Preprocess", format="%.3f ms"),
    "search_ms": st.column_config.NumberColumn("Search", format="%.3f ms"),
    "total_ms": st.column_config.NumberColumn("Total", format="%.3f ms"),
    "num_matches": st.column_config.NumberColumn("Matches"),
}


def _grouped_bars(container, df: pd.DataFrame, value: str) -> None:
    """Bar chart with one group per run label and one bar per algorithm, in run order."""
    wide = df.pivot_table(index="label", columns="algorithm", values=value, sort=False)
    wide = wide[[name for name in plots.ALGORITHM_ORDER if name in wide.columns]]
    container.bar_chart(wide, color=[plots.COLORS[name] for name in wide.columns], stack=False, sort=False)


def _clear_runs() -> None:
    st.session_state.run_history = []


st.set_page_config(page_title="Pattern Matching Lab", page_icon="🔎", layout="wide")
st.title("🔎 Pattern Matching Lab")
st.caption(":red[**Naive**] vs :blue[**KMP**] vs :green[**Boyer-Moore**] (bad-character rule). "
           "Run your own tests, then compare them with the saved experiments.")
tab_run, tab_compare = st.tabs([":material/science: Run Experiment", ":material/bar_chart: Compare"])

# ---------------------------------------------------------------------------
# Tab 1: Run Experiment
# ---------------------------------------------------------------------------
with tab_run:
    datasets = [d for d in DATASET_NAMES if d != "real_text" or os.path.exists(BOOK_PATH)]

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1], gap="large")
        dataset = col1.selectbox("Dataset", datasets)
        seed = col1.number_input("Seed", value=42, step=1)
        text_len = col2.slider("Text length", 1_000, 500_000, 100_000, step=1_000)
        pattern_len = col2.slider("Pattern length", 2, 128, 16)
        chosen = col3.pills("Algorithms", list(ALGORITHMS), selection_mode="multi", default=list(ALGORITHMS))
        clicked = col3.button("Run", type="primary", icon=":material/play_arrow:",
                              disabled=not chosen, width="stretch")
        if "real_text" not in datasets:
            st.caption("real_text hidden: data/book.txt not found (see data/README.md).")

    if clicked:
        with st.spinner("Running..."):
            text = get_dataset(dataset, text_len, int(seed))
            if dataset == "worst_case":
                pattern = worst_case_pattern(pattern_len)
            else:
                pattern = pattern_from_text(text, pattern_len, int(seed))
            results = [profile(name, text, pattern) for name in chosen]
        st.session_state.run_results = results
        st.session_state.run_label = dataset

        # Remember this run for the Compare tab: one row per algorithm.
        history = st.session_state.setdefault("run_history", [])
        run_no = history[-1]["run"] + 1 if history else 1
        for r in results:
            history.append({
                "run": run_no, "dataset": dataset, "text_len": text_len, "pattern_len": pattern_len,
                "seed": int(seed), "algorithm": r["algorithm"], "comparisons": r["comparisons"],
                "total_ms": r["total_ms"], "num_matches": r["num_matches"],
            })

    if "run_results" in st.session_state:
        results = st.session_state.run_results
        if any(r["matches"] != results[0]["matches"] for r in results):
            st.error("Algorithms disagree on match positions!")
        table = pd.DataFrame(results)[
            ["algorithm", "comparisons", "preprocess_ms", "search_ms", "total_ms", "num_matches"]
        ].set_index("algorithm")

        # One tile per algorithm: comparisons, and how that compares to Naive (green = fewer).
        naive = table["comparisons"].get("Naive")
        for tile, (name, row) in zip(st.columns(len(table)), table.iterrows()):
            delta = None
            if naive and name != "Naive":
                delta = f"{row['comparisons'] / naive - 1:+.0%} vs Naive"
            tile.metric(name, f"{int(row['comparisons']):,}", delta, delta_color="inverse", border=True,
                        help=f"Character comparisons. Total time {row['total_ms']:.2f} ms.")

        st.success(
            f"Fewest comparisons: **{table['comparisons'].idxmin()}**. "
            f"Fastest: **{table['total_ms'].idxmin()}**.",
            icon=":material/emoji_events:",
        )

        chart = table.reset_index()
        chart["label"] = st.session_state.run_label
        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.write("**Comparisons**")
            _grouped_bars(st, chart, "comparisons")
        with c2.container(border=True):
            st.write("**Total time (ms)**")
            _grouped_bars(st, chart, "total_ms")

        st.dataframe(table.reset_index(), hide_index=True, column_config=TABLE_COLUMNS)

# ---------------------------------------------------------------------------
# Tab 2: Compare
# ---------------------------------------------------------------------------
with tab_compare:
    runs = st.session_state.get("run_history", [])
    with st.container(border=True):
        st.subheader(":material/history: Your runs")
        if not runs:
            st.caption("Run a test in the Run Experiment tab and it will show up here.")
        else:
            runs_df = pd.DataFrame(runs)
            # Short labels so they stay horizontal; full settings are in the table below.
            runs_df["label"] = [f"#{r.run} {r.dataset}" for r in runs_df.itertuples()]
            c1, c2 = st.columns(2)
            c1.write("**Comparisons**")
            _grouped_bars(c1, runs_df, "comparisons")
            c2.write("**Total time (ms)**")
            _grouped_bars(c2, runs_df, "total_ms")
            st.dataframe(runs_df.drop(columns="label"), hide_index=True, column_config=TABLE_COLUMNS)
            st.button("Clear runs", icon=":material/delete:", type="tertiary", on_click=_clear_runs)

    st.subheader(":material/insights: Saved experiments")
    if not os.path.exists(CSV_PATH):
        st.info("No results yet. Run `python main.py` first, or run a quick version here.")
        if st.button("Run quick experiments", icon=":material/bolt:"):
            with st.spinner("Running quick experiments..."):
                benchmark.save_results(benchmark.run_experiments(quick=True), CSV_PATH)
            st.rerun()
    else:
        df = pd.read_csv(CSV_PATH)
        st.caption("Each experiment changes one thing and keeps the rest fixed (seed 42, 5 repeats).")
        graph_tabs = st.tabs([f"{i}. {label}" for i, (label, _, _) in enumerate(GRAPHS.values(), 1)])
        for graph_tab, (filename, (label, question, takeaway)) in zip(graph_tabs, GRAPHS.items()):
            with graph_tab:
                st.markdown(f"**Question:** {question}")
                fig = plots.PLOTS[filename](df)
                if fig is None:
                    st.warning("No data: data/book.txt was missing when the results were generated.")
                    continue
                st.info(takeaway, icon=":material/lightbulb:")
                # Natural size (100 px per inch) so single-panel graphs don't blow up to full width.
                st.pyplot(fig, width=int(fig.get_figwidth() * 100))
        with st.expander("Raw CSV"):
            st.dataframe(df, hide_index=True)
