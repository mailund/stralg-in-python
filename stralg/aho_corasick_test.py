"""Test Aho-Corasick."""

from test.helpers import fibonacci_string, pick_random_patterns, random_string

from stralg.aho_corasick import aho_corasick
from stralg.searching import plain


def test_abc() -> None:
    """Do basic tests."""
    x = "abcabcab"
    p = ("abc", "a", "b", "")
    for label, i in aho_corasick(x, *p):
        assert x[i:].startswith(p[label])


def compare_plain(x: str, pats: list[str]) -> bool:
    """Compare with plain exact matching."""
    plain_res = list(sorted((i, j) for i, p in enumerate(pats) for j in plain(x, p)))
    ac_res = list(sorted(aho_corasick(x, *pats)))

    return plain_res == ac_res


def test_compare_plain() -> None:
    """Compare with plain exact matching."""
    for _ in range(10):
        x = random_string(100, alpha="abcd")
        # need to go through set to remove duplicates.
        # plain can handle those, but Aho-Corasick cannot
        pats = list(set(pick_random_patterns(x, 10)))
        print(f'\nCompare with plain:\nx="{x}"\nps={pats}\n\n')
        assert compare_plain(x, pats)
    for _ in range(10):
        x = random_string(100)  # try larger alphabet
        # need to go through set to remove duplicates.
        # plain can handle those, but Aho-Corasick cannot
        pats = list(set(pick_random_patterns(x, 10)))
        print(f'\nCompare with plain:\nx="{x}"\nps={pats}\n\n')
        assert compare_plain(x, pats)

    for n in range(10, 15):
        x = fibonacci_string(n)
        # need to go through set to remove duplicates.
        # plain can handle those, but Aho-Corasick cannot
        pats = list(set(pick_random_patterns(x, 10)))
        print(f'\nCompare with plain:\nx="{x}"\nps={pats}\n\n')
        assert compare_plain(x, pats)
