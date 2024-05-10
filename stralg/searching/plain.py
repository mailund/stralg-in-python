"""
Simplest searching algorithm.
"""

from typing import Iterator


def plain(x: str, p: str) -> Iterator[int]:
    """
    Plain searching for patterns in strings. Given a string, `x`, and a pattern (string) `p`
    find all indices where `p` occurs in `x`.

    If n = len(x) and m = len(p), the time complexity of this algorithm is O(n * m).
    """
    for i in range(len(x) - len(p) + 1):  # runs O(n - m) times
        if x[i : i + len(p)] == p:  # comparison in O(m)
            yield i
