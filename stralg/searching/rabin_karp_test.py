from test.search import search_suite

from .rabin_karp import Word, h, hash_str, rabin_karp


def test_lrot() -> None:
    h = Word(2 + 8 + 32, ws=8)
    assert format(h.w, "08b") == "00101010"
    assert format(h.lrot(1).w, "08b") == "01010100"
    assert format(h.lrot(2).w, "08b") == "10101000"
    assert format(h.lrot(3).w, "08b") == "01010001"


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
