from __future__ import annotations

from typing import Any, Iterator


class BitVector:
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

    def __lshift__(self, other: int) -> BitVector:
        assert other >= 0, "Negative shift count"
        return BitVector(self.size, self.bits << other)

    def __add__(self, other: Any) -> BitVector:
        return BitVector(self.size, self.bits + int(other))

    def __or__(self, other: Any) -> BitVector:
        return BitVector(self.size, self.bits | int(other))

    def __and__(self, other: Any) -> BitVector:
        return BitVector(self.size, self.bits & int(other))

    def __invert__(self) -> BitVector:
        return BitVector(self.size, ~self.bits & self.mask)

    def __getitem__(self, index: int) -> bool:
        return (self.bits & (1 << index)) != 0


def match_bv(p: str, a: str) -> BitVector:
    """Return a bitvector of locations where p[j] == a."""
    bits = 0
    for b in reversed(p):
        bits = (bits << 1) + int(a == b)
    return BitVector(len(p), bits)


def shift_and(x: str, p: str) -> Iterator[int]:
    assert len(p) > 0, "Pattern cannot be empty"

    missing = BitVector(len(p), 0)
    t = {a: match_bv(p, a) for a in set(p)}

    status = BitVector(len(p), 0)
    for i, a in enumerate(x):
        match = t[a] if a in t else missing
        status = ((status << 1) + 1) & match
        if status[len(p) - 1]:
            yield i - len(p) + 1


def shift_or(x: str, p: str) -> Iterator[int]:
    assert len(p) > 0, "Pattern cannot be empty"

    missing = BitVector(len(p), ~0)
    t = {a: ~match_bv(p, a) for a in set(p)}

    bv = BitVector(len(p), ~0)
    for i, a in enumerate(x):
        match = t[a] if a in t else missing
        bv = (bv << 1) | match
        if not bv[len(p) - 1]:
            yield i - len(p) + 1
