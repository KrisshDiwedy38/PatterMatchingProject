"""Naive, KMP and Boyer-Moore (bad-character rule) string matching.

Every algorithm is split into a preprocess step and a search step:
    preprocess(pattern)            -> (table, preprocess_comparisons)
    search(text, pattern, table)   -> SearchResult

A comparison is counted every time a text character is checked against a
pattern character (or a pattern character against another pattern character
during KMP preprocessing), whether it matches or not.
"""

from dataclasses import dataclass


@dataclass
class SearchResult:
    matches: list[int]           # 0-based start indices of all matches (overlapping included)
    comparisons: int             # character comparisons during the search phase
    preprocess_comparisons: int  # character comparisons during preprocessing


def _no_search_needed(text: str, pattern: str) -> bool:
    """Empty pattern or pattern longer than text: nothing to search."""
    return len(pattern) == 0 or len(pattern) > len(text)


# ---------------------------------------------------------------------------
# Naive
# ---------------------------------------------------------------------------

def naive_preprocess(pattern: str) -> tuple[None, int]:
    """Naive needs no preprocessing. O(1)."""
    return None, 0


def naive_search(text: str, pattern: str, table: None = None) -> SearchResult:
    """Try every alignment and compare left to right. O(n * m) worst case."""
    if _no_search_needed(text, pattern):
        return SearchResult([], 0, 0)

    n = len(text)
    m = len(pattern)
    matches = []
    comparisons = 0

    # Slide the pattern over every possible start position in the text.
    for start in range(n - m + 1):
        j = 0
        # Compare characters left to right until a mismatch or a full match.
        while j < m:
            comparisons += 1
            if text[start + j] != pattern[j]:
                break
            j += 1
        if j == m:
            matches.append(start)

    return SearchResult(matches, comparisons, 0)


# ---------------------------------------------------------------------------
# Knuth-Morris-Pratt
# ---------------------------------------------------------------------------

def kmp_preprocess(pattern: str) -> tuple[list[int], int]:
    """Build the LPS (longest proper prefix that is also a suffix) array. O(m).

    lps[i] = length of the longest proper prefix of pattern[0..i]
             that is also a suffix of pattern[0..i].
    """
    m = len(pattern)
    lps = [0] * m
    comparisons = 0
    length = 0  # length of the current matched prefix
    i = 1

    while i < m:
        comparisons += 1
        if pattern[i] == pattern[length]:
            # The prefix grows by one character.
            length += 1
            lps[i] = length
            i += 1
        elif length > 0:
            # Fall back to the next shorter prefix that is also a suffix.
            # Do not advance i: we retry the same character.
            length = lps[length - 1]
        else:
            # No prefix matches, lps[i] stays 0.
            lps[i] = 0
            i += 1

    return lps, comparisons


def kmp_search(text: str, pattern: str, lps: list[int]) -> SearchResult:
    """Scan the text once, never moving backwards in it. O(n)."""
    if _no_search_needed(text, pattern):
        return SearchResult([], 0, 0)

    n = len(text)
    m = len(pattern)
    matches = []
    comparisons = 0
    i = 0  # index in text
    j = 0  # index in pattern

    while i < n:
        comparisons += 1
        if text[i] == pattern[j]:
            # Characters match, advance both.
            i += 1
            j += 1
            if j == m:
                # Full match ending at i - 1.
                matches.append(i - m)
                # Continue as if the last character mismatched, so overlapping
                # matches are still found.
                j = lps[j - 1]
        elif j > 0:
            # Mismatch after some matches: reuse what we know via the LPS array.
            j = lps[j - 1]
        else:
            # Mismatch on the first pattern character: move on in the text.
            i += 1

    return SearchResult(matches, comparisons, 0)


# ---------------------------------------------------------------------------
# Boyer-Moore (bad-character rule only)
# ---------------------------------------------------------------------------

def bm_preprocess(pattern: str) -> tuple[dict[str, int], int]:
    """Record the last index of each character in the pattern. O(m)."""
    last = {}
    for index in range(len(pattern)):
        last[pattern[index]] = index
    return last, 0


def bm_search(text: str, pattern: str, last: dict[str, int]) -> SearchResult:
    """Compare right to left and skip ahead using the bad-character rule.

    Best case about O(n / m), worst case O(n * m).
    """
    if _no_search_needed(text, pattern):
        return SearchResult([], 0, 0)

    n = len(text)
    m = len(pattern)
    matches = []
    comparisons = 0
    start = 0  # where the pattern currently starts in the text

    while start <= n - m:
        # Compare from the last pattern character backwards.
        j = m - 1
        while j >= 0:
            comparisons += 1
            if text[start + j] != pattern[j]:
                break
            j -= 1

        if j < 0:
            # Every character matched. Shift by 1 so overlapping matches are kept.
            matches.append(start)
            start += 1
        else:
            # Mismatch at pattern index j on text character c.
            # Line up the last occurrence of c in the pattern with it,
            # or jump past c entirely if it is not in the pattern (-1).
            c = text[start + j]
            start += max(1, j - last.get(c, -1))

    return SearchResult(matches, comparisons, 0)


ALGORITHMS = {
    "Naive":       (naive_preprocess, naive_search),
    "KMP":         (kmp_preprocess,   kmp_search),
    "Boyer-Moore": (bm_preprocess,    bm_search),
}
