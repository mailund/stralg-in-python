from test.search import small_search_suite

from .ba import border_search


def test_border_search() -> None:
    small_search_suite(border_search)
