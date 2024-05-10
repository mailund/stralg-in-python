"""
Boyer-Moore-Horspool algorithm for string searching.
"""

import collections
from typing import Iterator


def jump_table(p: str) -> dict[str, int]:
    """Create jump table for Boyer-Moore-Horspool algorithm."""
    # Table tracking the last occurrence of each character in the pattern.
    # The table contains the index, from the right, of the right-most occurrence
    # of a character, except for the last character in the pattern.
    # Characters that are not in the pattern will map to the length of the pattern.
    jump: dict[str, int] = collections.defaultdict(lambda: len(p))
    for j, a in enumerate(p[:-1]):  # skip last index!
        jump[a] = len(p) - j - 1

    return jump


def bmh(x: str, p: str) -> Iterator[int]:
    """Run the Boyer-Moore-Horspool algorithm."""
    assert len(p) > 0, "Pattern must not be empty."

    jump = jump_table(p)
    i, j = 0, 0
    while i < len(x) - len(p) + 1:
        for j in reversed(range(len(p))):
            if x[i + j] != p[j]:
                break  # mismatch, so abandon this attempt
        else:
            # We made it through the whole pattern without a mismatch.
            yield i

        i += jump[x[i + len(p) - 1]]
