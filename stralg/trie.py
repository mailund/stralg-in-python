"""Implementation of tries."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import NamedTuple, Optional, cast

LS = NamedTuple("LS", [("label", int), ("x", memoryview)])


@dataclass(eq=False)
class TrieNode:
    """Representation of a node in a trie."""

    label: Optional[int] = None
    children: dict[str, TrieNode] = field(default_factory=dict)

    # These are only needed for the Aho-Corasick algorithm, not for
    # basic use of a trie.
    parent: Optional[TrieNode] = field(default=None, repr=False)
    suffix_link: Optional[TrieNode] = field(default=None, repr=False)
    out_list: Optional[TrieNode] = field(default=None, repr=False)

    @property
    def is_root(self) -> bool:
        """Tell if this node is the root of its trie."""
        return self.parent is None

    def __getitem__(self, a: str) -> TrieNode:
        """Get the child of this node by following edge a."""
        # This just makes the code a little nicer
        # to look at, avoiding the .children[].
        return self.children[a]

    def __setitem__(self, a: str, n: TrieNode) -> None:
        """Set out-edge a to point to n."""
        self.children[a] = n

    def __contains__(self, a: str) -> bool:
        """Return True if there is a child with label a, False otherwise."""
        return a in self.children

    def to_dot(self, res: list[str]) -> list[str]:
        """Make a dot representation of the trie."""
        if self.label is None:
            res.append(f'{id(self)}[label="", shape=point]')
        else:
            res.append(f'{id(self)}[label="{self.label}", shape=circle]')

        if self.suffix_link is not None and not self.suffix_link.is_root:
            res.append(
                f"{id(self)} -> {id(self.suffix_link)}[style=dotted, color=red]"
            )  # noqa: E501 pylint:disable=line-too-long
        if self.out_list is not None:
            res.append(
                f"{id(self)} -> {id(self.out_list)}[style=dotted, color=green]"
            )  # noqa: E501 pylint:disable=line-too-long

        for k, n in self.children.items():
            res.append(f'{id(self)} -> {id(n)}[label="{k}"]')
            n.to_dot(res)
        res.append(
            "{ rank = same;"
            + ";".join(str(id(n)) for n in self.children.values())
            + "}"
        )

        return res

    def __eq__(self, other: object) -> bool:
        """Test of self is equivalent to other."""
        if not isinstance(other, TrieNode):  # pragma: no cover
            raise NotImplementedError()
        return sorted(self.children) == sorted(other.children) and all(
            self[k] == other[k] for k in self.children
        )


@dataclass(eq=False)
class Trie:
    """Representation of a trie."""

    root: TrieNode = field(default_factory=TrieNode)

    def insert(self, x: str, label: int) -> None:
        """Insert a new string x, with label, into the trie."""
        n = self.root
        for a in x:
            if a not in n:
                n[a] = TrieNode(parent=n)
            n = n[a]
        n.label = label

    def __contains__(self, x: str) -> bool:
        """Test if x is in the trie."""
        n = self.root
        for a in x:
            if a not in n:
                return False
            n = n[a]
        return n.label is not None

    def to_dot(self) -> str:
        """Create a dot representation of the trie."""
        return 'digraph { rankdir="LR" ' + "\n".join(self.root.to_dot([])) + "}"

    def __eq__(self, other: object) -> bool:
        """Test if self and other are equivalent."""
        if not isinstance(other, Trie):  # pragma: no cover
            raise NotImplementedError()
        return self.root == other.root


def depth_first_trie(*strings: str) -> Trie:
    """Build a trie in a depth-first manner."""
    # This is all it takes to build the trie.
    trie = Trie()
    for i, x in enumerate(strings):
        trie.insert(x, i)

    # If we want the suffix link and out list as well,
    # we need a breadth first traversal for that.
    queue = deque[TrieNode]([trie.root])
    while queue:
        n = queue.popleft()
        for out_edge, child in n.children.items():
            set_suffix_link(child, out_edge)
            queue.append(child)

    return trie


def set_suffix_link(node: TrieNode, in_edge: str) -> None:
    """Traverse trie to set up suffix-links and out-lists."""
    # We get the suffix link by running up the links from the
    # parent and trying to extend them. Casts are for the type
    # checker, telling them that nodes are not None
    parent = cast(TrieNode, node.parent)
    if parent.is_root:
        node.suffix_link = parent
    else:
        slink = cast(TrieNode, parent.suffix_link)
        while in_edge not in slink:
            if slink.is_root:
                # it is the root and we can't extend.
                node.suffix_link = slink
                break
            slink = cast(TrieNode, slink.suffix_link)
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
