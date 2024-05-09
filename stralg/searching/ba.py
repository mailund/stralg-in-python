"""
Searching using border arrays.

"""

from typing import Iterator


def border_array(x: str) -> list[int]:
    """Construct the border array for x."""
    ba = [0] * len(x)
    for j in range(1, len(x)):
        b = ba[j - 1]
        while b > 0 and x[j] != x[b]:
            b = ba[b - 1]
        ba[j] = b + 1 if x[j] == x[b] else 0
    return ba


def filter_border(p: str, ba: list[int]) -> list[int]:
    """
    Construct the strict border array for p.

    A struct border array is one where the border cannot
    match on the next character. If b is the length of the
    longest border for p[:i+1], it means p[:b] == p[i-b:i+1],
    but for a strict border, it must be the longest border
    such that p[b] != p[i+1].
    """
    for j, b in enumerate(ba[:-1]):
        if p[b] == p[j + 1] and b > 0:
            ba[j] = ba[b - 1]
    return ba


def border_search(x: str, p: str) -> Iterator[int]:
    """
    Search algorithm based on the border array.

    The algorithm runs in O(n + m) where n = len(x) and m = len(p).
    """
    assert len(p) > 0, "Pattern cannot be empty"

    # Build the border array
    ba = filter_border(p, border_array(p))

    # Now search...
    b = 0
    for i, a in enumerate(x):
        while b > 0 and p[b] != a:
            b = ba[b - 1]
        b = b + 1 if p[b] == a else 0
        if b == len(p):
            yield i - len(p) + 1
            b = ba[b - 1]
