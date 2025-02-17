"""
Knuth-Morris-Pratt algorithm.
"""

from typing import Iterator

from .ba import border_array, filter_border


def kmp(x: str, p: str) -> Iterator[int]:
    """Run the Knuth-Morris-Pratt algorithm."""
    assert len(p) > 0, "Pattern cannot be empty"

    j = 0
    ba = filter_border(p, border_array(p))
    for i, a in enumerate(x):
        # shift down pattern...
        while a != p[j] and j > 0:
            j = ba[j - 1]

        # match one up, if we can...
        if a == p[j]:
            j += 1

        if j == len(p):
            yield i - len(p) + 1
            j = ba[j - 1]
