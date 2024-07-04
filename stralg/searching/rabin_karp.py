from __future__ import annotations

from typing import Iterator


class Word:
    w: int
    ws: int
    mask: int

    def __init__(self, w: int = 0, ws: int = 32) -> None:
        self.ws = ws
        self.mask = (1 << ws) - 1
        self.w = w & self.mask

    def __str__(self) -> str:
        return format(self.w, "0x")

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Word) and self.w == value.w and self.ws == value.ws

    def __lor__(self, other: Word) -> Word:
        return Word(self.w | other.w, self.ws)

    def __xor__(self, other: Word) -> Word:
        return Word(self.w ^ other.w, self.ws)

    def lrot(self, k: int = 1) -> Word:
        k %= self.ws  # don't rotate multiples of words
        return Word((self.w << k) | (self.w >> (self.ws - k)), self.ws)


def h(a: str, ws: int = 32) -> Word:
    return Word(ord(a), ws)


def hash_str(s: str, ws: int = 32) -> Word:
    w = Word()
    for c in s:
        w = w.lrot() ^ h(c, ws)
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
