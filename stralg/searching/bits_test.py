from test.search import search_suite

from .bits import shift_and, shift_or


def test_shift_and_search() -> None:
    search_suite(shift_and)


def test_shift_or_search() -> None:
    search_suite(shift_or)
