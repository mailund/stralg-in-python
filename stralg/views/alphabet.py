"""Implements code for mapping strings to smaller alphabets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class String:
    alpha: Alphabet
    x: bytearray | memoryview

    def __str__(self):
        return self.alpha.decode(self.x)

    def __len__(self):
        return len(self.x)

    def __eq__(self, other: object) -> bool:
        match other:
            case str():
                return self.alpha.decode(self.x) == other
            case String():
                return self.alpha == other.alpha and self.x == other.x
            case _:
                return False

    def __getitem__(self, i: int | slice) -> String:
        match i:
            case slice():
                return String(self.alpha, self.x[i])
            case int():
                return String(self.alpha, self.view[i : i + 1])

    @property
    def view(self) -> memoryview:
        """Return a view of the string."""
        return memoryview(self.x)


class Alphabet:
    """Handles mapping from strings to smaller alphabets."""

    _map: dict[str, int]
    _revmap: dict[int, str]

    def __init__(self, reference: str) -> None:
        """
        Create an alphabet with the letters found in reference.

        An alphabet always has a sentinel symbol, byte zero, regardless of
        whether it is found in reference.
        """
        self._map = {
            a: i + 1  # reserve space for sentinel
            for i, a in enumerate(sorted(set(reference)))
        }
        self._revmap = {i: a for a, i in self._map.items()}
        # sentinel
        self._map[chr(0)] = 0
        self._revmap[0] = "•"  # just a printable symbol unlikely to be in the string

        # We save some space by packing strings into bytearrays,
        # but that means that we must fit the entire alphabet
        # into a byte (or do some other encoding that I do not
        # feel up to implementing right now).
        assert len(self._map) <= 256, "Cannot handle alphabets we cannot fit into bytes"

    def __len__(self) -> int:
        """Return the number of letters in the alphabet."""
        return len(self._map)

    def encode(self, x: str, *, with_sentinel: bool) -> bytearray:
        """
        Map the characters in x to their corresponding letters in the alphabet.

        The result is returned as a bytearray. If x contains a letter not in
        the alphabet, map raises a KeyError.
        """
        return (
            bytearray([self._map[a] for a in x] + [0])
            if with_sentinel
            else bytearray(self._map[a] for a in x)
        )

    def decode(self, x: Iterable[int]) -> str:
        """
        Map from alphabet to original alphabet.

        Maps a character from the alphabet back to the corresponding
        character in the reference used to create the alphabet.
        """
        return "".join(self._revmap[i] for i in x)

    def as_string(self, x: str, *, with_sentinel: bool = False) -> String:
        """Map a string to the alphabet."""
        return String(self, self.encode(x, with_sentinel=with_sentinel))

    @staticmethod
    def map_string(x: str, *, with_sentinel: bool = True) -> String:
        """
        Create mapped string with corresponding alphabet.

        Creates an alphabet from x, maps x to theh alphabet,
        then returns the mapped string and the alphabet.
        """
        return Alphabet(x).as_string(x, with_sentinel=with_sentinel)
