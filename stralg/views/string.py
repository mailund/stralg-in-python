"""
Strings that are mapped to bytearrays using an alphabet.
"""

from typing import NewType

string = NewType("string", bytearray)  # A string mapped to a bytearray.
