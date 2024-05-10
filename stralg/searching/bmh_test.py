from test.search import search_suite

from .bmh import bmh, jump_table


def test_jump_table() -> None:
    p = "abcc"
    assert jump_table(p) == {"a": 3, "b": 2, "c": 1}


def test_bmh_search() -> None:
    search_suite(bmh)
