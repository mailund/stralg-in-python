from test.search import small_search_suite

from .bmh import bmh


def test_bmh_search() -> None:
    small_search_suite(bmh)
