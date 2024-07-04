from __future__ import annotations

from typing import Iterator


class Word:
    w: int

    WS: int = 32  # Word size used for hash
    WORD_SIZE_MASK = WS - 1  # Mask for mapping integers to the range of word bits
    WORD_MASK = (1 << WS) - 1  # Mask for mapping integers to words

    def __init__(self, w: int = 0) -> None:
        self.w = w & self.WORD_MASK  # Mask integers to word size

    def __str__(self) -> str:
        return format(self.w, "0x")

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Word) and self.w == value.w

    def __xor__(self, other: Word) -> Word:
        return Word(self.w ^ other.w)

    def lrot(self, k: int = 1) -> Word:
        k &= self.WORD_SIZE_MASK  # don't rotate multiples of words
        return Word((self.w << k) | (self.w >> (self.WS - k)))


def h(a: str) -> Word:
    assert len(a) == 1, "Only single characters allowed"
    return Word(ord(a))


def hash_str(s: str) -> Word:
    w = Word()
    for c in s:
        w = w.lrot() ^ h(c)
    return w


def rabin_karp(x: str, p: str) -> Iterator[int]:
    m, hp = len(p), hash_str(p)
    n, hx = len(x), hash_str(x[:m])

    for i in range(n - m):
        if hp == hx and p == x[i : i + m]:
            yield i
        hx = hx.lrot() ^ h(x[i]).lrot(m) ^ h(x[i + m])

    if hp == hx and p == x[n - m :]:
        yield n - m


def rabin_karp_sentinel(x: str, p: str) -> Iterator[int]:
    x += "\0"  # Add sentinel to the end of x
    m, hp = len(p), hash_str(p)
    n, hx = len(x), hash_str(x[:m])

    for i in range(n - m):
        if hp == hx and p == x[i : i + m]:
            yield i
        hx = hx.lrot() ^ h(x[i]).lrot(m) ^ h(x[i + m])


def rabin_karp_rem(x: str, p: str) -> Iterator[int]:
    m, hp = len(p), hash_str(p)
    n, hx = len(x), hash_str(x[: m - 1])  # Computing hash of the first m-1 characters

    rem = Word(0)  # Initial character to remove is zero (no character).
    for i in range(n - m + 1):
        hx, rem = hx.lrot() ^ rem.lrot(m) ^ h(x[i + m - 1]), h(x[i])
        if hp == hx and p == x[i : i + m]:
            yield i
