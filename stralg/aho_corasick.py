"""Implementation of the Aho-Corasick algorithm."""

from collections import deque
from typing import Iterator

from .trie import Trie, TrieNode, depth_first_trie


def annotate_trie(trie: Trie) -> Trie:
    """Extend trie with suffix links and out-lists."""
    queue = deque([trie.root])
    while queue:
        n = queue.popleft()
        for label, child in n.children.items():
            set_suffix_link(child, label)
            queue.append(child)
    return trie


def set_suffix_link(node: TrieNode, in_edge: str) -> None:
    """Traverse trie to set up suffix-links and out-lists."""
    # We get the suffix link by running up the links from the
    # parent and trying to extend them. Asserts are for the type
    # checker, telling them that nodes are not None
    assert node.parent is not None

    if node.parent.is_root:
        node.suffix_link = node.parent
    else:
        slink = node.parent.suffix_link
        assert slink is not None
        while in_edge not in slink:
            if slink.is_root:
                # it is the root and we can't extend.
                node.suffix_link = slink
                break
            assert slink.suffix_link is not None
            slink = slink.suffix_link
        else:
            # If we break to here, we can extend.
            node.suffix_link = slink[in_edge]

    # The suffix link for non-roots should never be None
    assert node.suffix_link is not None

    # The out list either skips suffix_link or not, depending on
    # whether there is a label there or not. The out_list can be None.
    # We terminate the lists with a None.
    slink = node.suffix_link
    node.out_list = slink if slink.label is not None else slink.out_list


def occurrences(n: TrieNode) -> Iterator[int]:
    """Iterate over all occurrances in the out-list of a node."""
    if n.label is not None:
        yield n.label

    olist = n.out_list
    while olist:
        assert olist.label is not None
        yield olist.label
        olist = olist.out_list


def find_out(n: TrieNode, a: str) -> TrieNode:
    """
    Find the node we get to with an a move.

    We will end up in the node if we cannot make one,
    but that works fine with the out list reporting.
    """
    while a not in n:
        if n.is_root:
            # The root, and in here we cannot extend.
            return n
        assert n.suffix_link is not None
        n = n.suffix_link
    return n[a]


def aho_corasick(x: str, *p: str) -> Iterator[tuple[int, int]]:
    """Exact pattern matching with the Aho-Corasick algorithm."""
    trie = annotate_trie(depth_first_trie(*p))
    n = trie.root

    # If the empty string is in the trie we
    # need to handle it as a special case
    if n.label is not None:
        yield (n.label, 0)

    for i, a in enumerate(x):
        n = find_out(n, a)
        for label in occurrences(n):
            yield (label, i - len(p[label]) + 1)
