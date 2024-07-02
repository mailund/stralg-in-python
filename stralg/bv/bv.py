"""Bitvector."""

from __future__ import annotations

from array import array
from typing import Any

TYPECODE = "B"  # Q
BYTE_BITS = 8
WS = array(TYPECODE).itemsize * BYTE_BITS


def buckets_needed(items: int, bucket_size: int) -> int:
    """Return the number of buckets needed to store items."""
    return (items + bucket_size - 1) // bucket_size


class BitVector:
    size: int
    words: array[int]

    def __init__(self, size: int) -> None:
        self.size = size
        self.words = array(TYPECODE, [0] * buckets_needed(size, WS))

    def __len__(self) -> int:
        return self.size

    def __str__(self) -> str:
        words = reversed([format(word, f"0{WS}b") for word in self.words])
        return " ".join(words)

    __repr__ = __str__

    def __getitem__(self, index: int) -> bool:
        bucket = index // WS
        offset = index % WS
        return (self.words[bucket] & (1 << offset)) != 0

    def __setitem__(self, index: int, value: bool) -> None:
        bucket = index // WS
        offset = index % WS
        if value:
            self.words[bucket] |= 1 << offset
        else:
            self.words[bucket] &= ~(1 << offset)

    def __lshift__(self, other: int) -> BitVector:
        assert other >= 0, "Negative shift count"
        result = BitVector(self.size)
        word_offset = other // WS
        word_shift = other % WS
        mask = (1 << WS) - 1
        carry = 0
        for i in range(len(self.words) - word_offset):
            w = (self.words[i] << word_shift) & mask
            result.words[i + word_offset] = w | carry
            carry = self.words[i] >> (WS - word_shift)
        return result


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


p = "aba"
x = "ababa"

t = {a: match_bv(p, a) for a in set(p)}
bv = IntBitVector(len(p), 0)
for i, a in enumerate(x):
    bv = ((bv << 1) + 1) & t[a]
    print(f"bv{i} = {bv}", "*" if bv[len(p) - 1] else "")

print()

t = {a: ~match_bv(p, a) for a in set(p)}
bv = IntBitVector(len(p), ~0)
for i, a in enumerate(x):
    bv = (bv << 1) | t[a]
    print(f"bv{i} = {bv}", "*" if not bv[len(p) - 1] else "")
