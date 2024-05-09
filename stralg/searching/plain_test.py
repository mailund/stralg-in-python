from test.search import small_search_suite

from .plain import plain


def test_plain_search() -> None:
    small_search_suite(plain)
