"""Single entry point: run experiments, save CSV, make graphs, print a summary."""

import argparse
import os
import time

import benchmark
import plots

RESULTS_DIR = "results"
CSV_PATH = os.path.join(RESULTS_DIR, "results.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pattern Matching Lab pipeline")
    parser.add_argument("--quick", action="store_true", help="small sizes, fast check")
    parser.add_argument("--no-plots", action="store_true", help="skip graph generation")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    start = time.perf_counter()

    df = benchmark.run_experiments(quick=args.quick)
    benchmark.save_results(df, CSV_PATH)
    saved = [] if args.no_plots else plots.make_all_plots(CSV_PATH, RESULTS_DIR)

    elapsed = time.perf_counter() - start
    print("\n=== Summary ===")
    print(f"Runs: {len(df)} ({df['experiment'].nunique()} experiments)")
    print(f"Time taken: {elapsed:.1f} s")
    print(f"CSV: {CSV_PATH}")
    print(f"Graphs: {len(saved)} saved in {RESULTS_DIR}/" if saved else "Graphs: skipped")

    # Fewest total comparisons per experiment.
    totals = df.groupby(["experiment", "algorithm"])["comparisons"].sum().unstack()
    totals["fewest comparisons"] = totals.idxmin(axis=1)
    totals.index = [f"{i}. {benchmark.EXPERIMENT_NAMES[i]}" for i in totals.index]
    print("\nTotal comparisons per experiment:")
    print(totals.to_string())


if __name__ == "__main__":
    main()
