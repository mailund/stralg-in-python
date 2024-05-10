from test.search import search_suite

from .kmp import kmp


def test_kmp_search() -> None:
    search_suite(kmp)
