"""
Plain searching for patterns in strings. Given a string, `x`, and a pattern (string) `p`
find all indices where `p` occurs in `x`.
"""

from .ba import border_search as border_search
from .bmh import bmh as bmh
from .kmp import kmp as kmp
from .plain import plain as plain
