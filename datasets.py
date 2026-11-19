"""Seeded dataset and pattern generators, plus a real-text loader.

Every generator uses its own random.Random(seed), never the global random
state, so results are reproducible.
"""

import os
import random
import string

ALPHABETS = {
    "binary":  "01",
    "dna":     "ACGT",
    "english": string.ascii_lowercase,
    # Printable ASCII without tabs/newlines etc., but keeping the space.
    "ascii":   "".join(c for c in string.printable if c not in string.whitespace) + " ",
}

DATASET_NAMES = ["binary", "dna", "english", "ascii", "worst_case", "real_text"]
BOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "book.txt")


def random_text(length: int, alphabet: str, seed: int) -> str:
    """Uniformly random text over the given alphabet."""
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(length))


def worst_case_text(length: int) -> str:
    """'aaaa...a': forces Naive to re-compare almost the whole pattern each time."""
    return "a" * length


def worst_case_pattern(length: int) -> str:
    """'aa...ab': matches everywhere until the very last character."""
    return "a" * (length - 1) + "b"


def pattern_from_text(text: str, length: int, seed: int) -> str:
    """Random substring of the text, so there is at least one match."""
    rng = random.Random(seed)
    start = rng.randint(0, len(text) - length)
    return text[start:start + length]


def load_real_text(path: str = BOOK_PATH) -> str | None:
    """Read a book, lowercase it and collapse whitespace. None if the file is missing."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", errors="ignore") as f:
        return " ".join(f.read().lower().split())


def get_dataset(name: str, length: int, seed: int) -> str:
    """Return a text of `length` characters for the named dataset."""
    if name == "worst_case":
        return worst_case_text(length)
    if name == "real_text":
        book = load_real_text()
        if book is None:
            raise FileNotFoundError(f"{BOOK_PATH} not found, see data/README.md")
        return book[:length]
    if name in ALPHABETS:
        return random_text(length, ALPHABETS[name], seed)
    raise ValueError(f"Unknown dataset: {name}")
