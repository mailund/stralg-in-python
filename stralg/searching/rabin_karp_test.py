from test.search import search_suite

from .rabin_karp import h, hash_str, rabin_karp, rabin_karp_rem, rabin_karp_sentinel


def test_hash() -> None:
    assert h("a") == h("a")
    assert hash_str("a") == h("a")
    assert hash_str("ab") == h("b") ^ h("a").lrot()
    assert (
        hash_str("ab")
        == hash_str("b") ^ hash_str("a").lrot()
        == h("b") ^ hash_str("a").lrot()
    )

    for x in ("a", "ab", "aabb", "abcdefg"):
        assert hash_str(x) ^ h(x[0]).lrot(len(x) - 1) == hash_str(x[1:])


def test_rabin_karp_search() -> None:
    search_suite(rabin_karp)


def test_rabin_karp_sentinel_search() -> None:
    search_suite(rabin_karp_sentinel)


def test_rabin_karp_rem_search() -> None:
    search_suite(rabin_karp_rem)
