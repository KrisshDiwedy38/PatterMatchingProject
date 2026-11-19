# Pattern Matching Lab

An experimental framework that implements and compares three string matching algorithms:
**Naive**, **Knuth-Morris-Pratt (KMP)** and **Boyer-Moore** (bad-character rule). It generates
reproducible (seeded) datasets, profiles each algorithm (character comparisons, preprocessing
time, search time), writes the results to CSV and graphs, and includes a Streamlit dashboard
for running experiments, comparing results and stepping through each algorithm.

> Course brief: "Build an integrated experimental framework for Naïve, KMP, and Boyer-Moore
> algorithms with controlled datasets, performance profiling, and comparative analysis."

## Setup

Python 3.10+.

```
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

Optional: add a book for the real-text experiment, see [data/README.md](data/README.md).

## Running

```
pytest                       # run the tests
python main.py               # full run: results/results.csv + graphs (about 15-30 s)
python main.py --quick       # text lengths / 10, 2 repeats: fast check
python main.py --no-plots    # skip graph generation
streamlit run app.py         # dashboard
```

The dashboard has two tabs:
- **Run Experiment**: pick a dataset, text/pattern length, seed and algorithms, then compare them.
- **Compare**: your runs from this session side by side, then every graph from `results/` with a short explanation (can run a quick experiment if there are no results yet).

## Modules

| File | What it does |
|---|---|
| `algorithms.py` | The three algorithms. Each has `preprocess(pattern) -> (table, comparisons)` and `search(text, pattern, table) -> SearchResult`, registered in `ALGORITHMS`. |
| `datasets.py` | Seeded random texts (binary, DNA, English, ASCII), worst-case text/pattern, patterns taken from the text, and the book loader. |
| `profiler.py` | Runs one algorithm several times with GC disabled; reports median preprocessing and search times plus comparison counts. |
| `benchmark.py` | The five experiments (as constants), a check that all algorithms find the same matches, and the CSV writer. |
| `plots.py` | Builds every graph from the CSV; each function returns a matplotlib Figure (reused by the dashboard). |
| `main.py` | Runs the whole pipeline and prints a summary. |
| `app.py` | Streamlit dashboard. |
| `tests/test_algorithms.py` | Correctness tests against a simple reference implementation. |

## Experiments

Each experiment changes one variable and keeps the rest fixed (seed 42, 5 repeats).

1. **Text length scaling** (DNA, English; 10k to 500k characters, pattern 10): all three are
   linear in the text length on random text; shows the constant factors.
2. **Pattern length** (DNA, English; pattern 2 to 128, text 100k): Boyer-Moore gets *faster* with
   longer patterns because it can skip further; Naive and KMP do not benefit.
3. **Alphabet size** (binary, DNA, English, ASCII; text 100k, pattern 16): larger alphabets give
   earlier mismatches and bigger bad-character shifts, which helps Boyer-Moore most.
4. **Worst case** (`aaa...a` text, `aa...ab` pattern, text 50k): Naive's comparisons grow with
   pattern length (O(n·m)), while KMP stays linear (O(n)).
5. **Real text** (a Gutenberg book, first 200k characters, pattern 4 to 64): how the algorithms
   behave on natural language.

Results go to `results/results.csv` with columns:
`experiment, dataset, text_len, pattern_len, algorithm, comparisons, preprocess_comparisons, preprocess_ms, search_ms, total_ms, num_matches`.
