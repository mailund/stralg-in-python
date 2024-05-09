"""
Boyer-Moore-Horspool algorithm for string searching.
"""

import collections
from typing import Iterator


def bmh(x: str, p: str) -> Iterator[int]:
    """Run the Boyer-Moore-Horspool algorithm."""
    # Can't handle empty strings directly
    if not p:
        yield from range(len(x) + 1)
        return

    jump: dict[str, int] = collections.defaultdict(lambda: len(p))
    for j, a in enumerate(p[:-1]):  # skip last index!
        jump[a] = len(p) - j - 1

    i, j = 0, 0
    while i < len(x) - len(p) + 1:
        for j in reversed(range(len(p))):
            if x[i + j] != p[j]:
                break
        else:
            yield i

        i += jump[x[i + len(p) - 1]]
