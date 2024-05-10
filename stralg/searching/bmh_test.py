from test.search import search_suite

from .bmh import bmh


def test_bmh_search() -> None:
    search_suite(bmh)
