"""Bitvector."""

from __future__ import annotations

from array import array

BYTE_BITS = 8
WS = array("Q").itemsize * BYTE_BITS


def buckets_needed(items: int, bucket_size: int) -> int:
    """Return the number of buckets needed to store items."""
    return (items + bucket_size - 1) // bucket_size


class BitVector:
    size: int
    words: array[int]

    def __init__(self, size: int) -> None:
        self.size = size
        self.words = array("Q", [0] * buckets_needed(size, WS))

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
        carry = 0
        for i in range(self.size - word_offset):
            left = self.words[i] >> (WS - word_shift)
            result.words[i + word_offset] = left | carry
            carry = self.words[i + word_offset] << word_shift
        return result
