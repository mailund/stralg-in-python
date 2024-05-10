"""
Functions for testing plain search algorithms.
"""

import random
import string
from typing import Callable as Fn
from typing import Iterable

SearchAlgorithm = Fn[[str, str], Iterable[int]]


def _cmp_results(
    x: str, p: str, results: Iterable[int], expected: Iterable[int]
) -> None:
    """
    Compare the results of a search with the expected results.
    """
    res = list(sorted(results))
    exp = list(sorted(expected))
    assert len(res) == len(exp)
    for r, e in zip(res, exp):
        assert (
            r == e
        ), f"Error searching for {p} in {x}. Expected {exp}, got {res} ({r} != {e})"


def small_search_suite(search: SearchAlgorithm) -> None:
    """
    Test the search algorithm.
    """
    x = "abracadabra"
    p = "abr"
    expected: list[int] = [0, 7]
    _cmp_results(x, p, search(x, p), expected)

    x = "abracadabra"
    p = "a"
    expected = [0, 3, 5, 7, 10]
    _cmp_results(x, p, search(x, p), expected)

    x = "abracadabra"
    p = "dab"
    expected = [6]
    _cmp_results(x, p, search(x, p), expected)

    x = "abracadabra"
    p = "x"
    expected = []
    _cmp_results(x, p, search(x, p), expected)

    x = "abracadabra"
    p = "abracadabra"
    expected = [0]
    _cmp_results(x, p, search(x, p), expected)

    x = "abracadabra"
    p = "abracadabrax"
    expected = []
    _cmp_results(x, p, search(x, p), expected)

    x = "abracadabra"
    p = "abracadabrax"
    expected = []
    _cmp_results(x, p, search(x, p), expected)


def random_string_suite(search: SearchAlgorithm) -> None:
    """
    Test the search algorithm with random strings.
    """

    for _ in range(100):
        n = random.randint(1, 100)
        m = random.randint(1, n)
        x = "".join(random.choices(string.ascii_lowercase, k=n))
        p = "".join(random.choices(string.ascii_lowercase, k=m))
        expected = [i for i in range(n) if x[i : i + m] == p]
        _cmp_results(x, p, search(x, p), expected)


def search_suite(search: SearchAlgorithm) -> None:
    """
    Run the search suite.
    """
    small_search_suite(search)
    random_string_suite(search)
