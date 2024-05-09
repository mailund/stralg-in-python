from test.search import small_search_suite

from .kmp import kmp


def test_kmp_search() -> None:
    small_search_suite(kmp)
