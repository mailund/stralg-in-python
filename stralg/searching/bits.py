from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterator


class IntBitVector:
    size: int
    bits: int
    mask: int

    def __init__(self, size: int, bits: int = 0) -> None:
        self.size = size
        self.mask = (1 << size) - 1
        self.bits = bits & self.mask

    def __str__(self) -> str:
        return format(self.bits, f"0{self.size}b")

    __repr__ = __str__

    def __int__(self) -> int:
        return self.bits

    def __lshift__(self, other: int) -> IntBitVector:
        assert other >= 0, "Negative shift count"
        return IntBitVector(self.size, self.bits << other)

    def __add__(self, other: Any) -> IntBitVector:
        return IntBitVector(self.size, self.bits + int(other))

    def __or__(self, other: Any) -> IntBitVector:
        return IntBitVector(self.size, self.bits | int(other))

    def __and__(self, other: Any) -> IntBitVector:
        return IntBitVector(self.size, self.bits & int(other))

    def __invert__(self) -> IntBitVector:
        return IntBitVector(self.size, ~self.bits & self.mask)

    def __getitem__(self, index: int) -> bool:
        return (self.bits & (1 << index)) != 0


def match_bv(p: str, a: str) -> IntBitVector:
    """Return a bitvector of locaations where p[j] == a."""
    bits = 0
    for b in p:
        bits = (bits << 1) + int(a == b)
    return IntBitVector(len(p), bits)


def shift_and(x: str, p: str) -> Iterator[int]:
    t: dict[str, IntBitVector] = defaultdict(lambda: IntBitVector(len(p), 0))
    t.update({a: match_bv(p, a) for a in set(p)})
    print(t)

    bv = IntBitVector(len(p), 0)
    for i, a in enumerate(x):
        bv = ((bv << 1) + 1) & t[a]
        if bv[len(p) - 1]:
            yield i - len(p) + 1


def shift_or(x: str, p: str) -> Iterator[int]:
    t: dict[str, IntBitVector] = defaultdict(lambda: IntBitVector(len(p), ~0))
    t.update({a: ~match_bv(p, a) for a in set(p)})
    print(t)

    bv = IntBitVector(len(p), ~0)
    for i, a in enumerate(x):
        print(a, t[a])
        bv = (bv << 1) | t[a]
        if not bv[len(p) - 1]:
            yield i - len(p) + 1
