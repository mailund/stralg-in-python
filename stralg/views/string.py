"""
Strings that are mapped to bytearrays using an alphabet.
"""

from dataclasses import dataclass

from .alphabet import Alphabet


@dataclass
class String:
    alpha: Alphabet
    x: bytearray

    def __str__(self):
        return self.alpha.decode(self.x)

    @property
    def view(self) -> memoryview:
        """Return a view of the string."""
        return memoryview(self.x)
