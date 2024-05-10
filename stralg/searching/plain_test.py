from test.search import search_suite

from .plain import plain


def test_plain_search() -> None:
    search_suite(plain)
