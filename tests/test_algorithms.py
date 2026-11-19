import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms import ALGORITHMS, bm_preprocess, kmp_preprocess
from datasets import ALPHABETS, worst_case_pattern, worst_case_text


def reference(text: str, pattern: str) -> list[int]:
    """All overlapping match positions using str.startswith."""
    if not pattern:
        return []
    return [i for i in range(len(text)) if text.startswith(pattern, i)]


def run(name: str, text: str, pattern: str):
    preprocess, search = ALGORITHMS[name]
    table, _ = preprocess(pattern)
    return search(text, pattern, table)


ALL = list(ALGORITHMS)

CASES = [
    ("xxabcxx", "abc", [2]),                  # match in the middle
    ("abcdef", "xyz", []),                    # no match
    ("abXabYab", "ab", [0, 3, 6]),            # multiple non-overlapping
    ("aaaa", "aa", [0, 1, 2]),                # overlapping
    ("hello", "hello", [0]),                  # pattern equals text
    ("hi", "hello", []),                      # pattern longer than text
    ("banana", "a", [1, 3, 5]),               # single-character pattern
    ("abxxxab", "ab", [0, 5]),                # match at start and end
]


@pytest.mark.parametrize("name", ALL)
@pytest.mark.parametrize("text,pattern,expected", CASES)
def test_known_cases(name, text, pattern, expected):
    assert run(name, text, pattern).matches == expected


@pytest.mark.parametrize("name", ALL)
def test_empty_pattern(name):
    result = run(name, "abc", "")
    assert result.matches == []
    assert result.comparisons == 0


@pytest.mark.parametrize("name", ALL)
def test_pattern_longer_than_text_no_comparisons(name):
    assert run(name, "ab", "abc").comparisons == 0


def test_randomised_against_reference():
    rng = random.Random(1234)
    alphabets = list(ALPHABETS.values())
    for _ in range(200):
        alphabet = rng.choice(alphabets)
        # Small alphabets often so there are plenty of matches.
        text = "".join(rng.choice(alphabet[:3]) for _ in range(rng.randint(0, 60)))
        pattern = "".join(rng.choice(alphabet[:3]) for _ in range(rng.randint(1, 6)))
        expected = reference(text, pattern)
        for name in ALL:
            assert run(name, text, pattern).matches == expected, (name, text, pattern)


def test_kmp_lps():
    assert kmp_preprocess("abacab")[0] == [0, 0, 1, 0, 1, 2]
    assert kmp_preprocess("aaaa")[0] == [0, 1, 2, 3]
    assert kmp_preprocess("abcd")[0] == [0, 0, 0, 0]


def test_bm_last_occurrence():
    assert bm_preprocess("abacab")[0] == {"a": 4, "b": 5, "c": 3}


def test_worst_case_naive_beats_kmp_in_comparisons():
    text = worst_case_text(1000)
    pattern = worst_case_pattern(10)
    assert run("Naive", text, pattern).comparisons > run("KMP", text, pattern).comparisons
