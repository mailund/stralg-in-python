from test.search import search_suite

from .ba import border_search


def test_border_search() -> None:
    search_suite(border_search)
