"""Constructing and using suffix trees."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Optional, TypeGuard, cast

from ..views import Alphabet, String

# SECTION Suffix Tree representation


@dataclass
class Inner:
    """An inner node."""

    edge_label: memoryview  # slice of underlying bytearray
    parent: Optional[Inner] = field(default=None, init=False, repr=False)

    suffix_link: Optional[Inner] = field(default=None, init=False, repr=False)
    children: dict[int, Node] = field(default_factory=dict, init=False, repr=False)

    def add_children(self, *children: Node) -> None:
        """Add children to this inner node."""
        for child in children:
            self.children[child.edge_label[0]] = child
            child.parent = self

    def out_child(self, edge: memoryview) -> Node:
        """Find the child we go to if we follow the first letter in edge."""
        return self.children[edge[0]]

    def to_dot(self, alpha: Alphabet) -> Iterator[str]:
        """Get a dot representation for the tree rooted here."""
        if self.parent is None:  # Root node
            yield f'{id(self)}[label="", shape=circle, style=filled, fillcolor=grey]'  # noqa: E501
        else:
            elab = alpha.decode(self.edge_label)
            yield f'{id(self)}[label="", shape=point]'
            yield f'{id(self.parent)} -> {id(self)}[label="{elab}"]'
        if self.suffix_link:
            yield f"{id(self)} -> {id(self.suffix_link)}[style=dashed, color=red]"  # noqa
        for child in self.children.values():
            yield from child.to_dot(alpha)

    def __iter__(self) -> Iterator[int]:
        """Iterate through all leaves in the tree rooted here."""
        # You could make it more efficient by sorting once
        # and keeping the table sorted, but for experimenting
        # this if fine...
        for x in sorted(self.children):
            yield from self.children[x]

    def __eq__(self, other: object) -> bool:
        """Test if two nodes are equivalent."""
        if (
            not is_inner(other) or self.edge_label != other.edge_label
        ):  # pragma: no cover
            return False

        # Equal if sorted children are equal.
        my_children = list(sorted(self.children.items()))
        others_children = list(sorted(other.children.items()))
        return len(my_children) == len(others_children) and all(
            a == b for a, b in zip(my_children, others_children)
        )


class Leaf:
    """A leaf in a suffix tree."""

    edge_label: memoryview  # slice of underlying bytearray
    parent: Optional[Inner] = field(default=None, init=False, repr=False)

    leaf_label: int

    def __init__(self, leaf_label: int, edge_label: memoryview):
        """Create a leaf."""
        self.leaf_label = leaf_label
        self.edge_label = edge_label

    def to_dot(self, alpha: Alphabet) -> Iterator[str]:
        """Get the dot representation of the leaf."""
        lab = alpha.decode(self.edge_label)
        yield f"{id(self)}[label={self.leaf_label}, shape=circle]"
        yield f'{id(self.parent)} -> {id(self)}[label="{lab}"]'

    def __iter__(self) -> Iterator[int]:
        """Iterate through all the leaves rooted in this node."""
        yield self.leaf_label

    def __eq__(self, other: object) -> bool:
        """Test if two nodes are equivalent."""
        return is_leaf(other) and (
            self.edge_label == other.edge_label and self.leaf_label == other.leaf_label
        )


Node = Inner | Leaf


def is_inner(n: Any) -> TypeGuard[Inner]:
    """Test if a node is an inner node."""
    return isinstance(n, Inner)


def is_leaf(n: Any) -> TypeGuard[Leaf]:
    """Test if a node is a leaf."""
    return isinstance(n, Leaf)


@dataclass
class SuffixTree:
    """A suffix tree."""

    s: String
    root: Inner

    def search(self, p: str) -> Iterator[int]:
        """Find all occurences of p in the suffix tree."""
        try:
            p_ = self.s.alpha.as_string(p).view
        except KeyError:
            # when we can't map, we don't get hits
            return

        n, j, _, y = tree_search(self.root, p_)
        if len(j) == len(y):
            # We search all the way through the last string,
            # so we have a match
            yield from iter(n)

    def __contains__(self, p: str) -> bool:
        """Test if string p is in the tree."""
        return next(self.search(p), -1) != -1

    def to_dot(self) -> str:
        """Get a dot representation of a tree."""
        return (
            'digraph { rankdir="LR" ' + "\n".join(self.root.to_dot(self.s.alpha)) + "}"
        )  # noqa

    def __eq__(self, other: object) -> bool:
        """Test if two trees are equivalent."""
        if not isinstance(other, SuffixTree):  # pragma: no cover
            return False
        return self.root == other.root


# !SECTION

# SECTION Searching in a suffix tree


def shared_prefix(x: memoryview, y: memoryview) -> memoryview:
    """
    Return the shared prefix of x and y.
    """
    for i, (a, b) in enumerate(zip(x, y)):
        if a != b:
            return x[:i]
    else:
        # matched all the way through. Return the shortest string
        return x if len(x) < len(y) else y


@dataclass
class NodeResult:
    node: Inner
    remaining_query: memoryview
    complete_match: bool


@dataclass
class EdgeResult:
    node: Node
    matched: memoryview
    rest_of_edge: memoryview
    remaining_query: memoryview
    complete_match: bool


SearchResult = NodeResult | EdgeResult


def tree_search(
    n: Inner, p: memoryview
) -> tuple[Node, memoryview, memoryview, memoryview]:
    """Search for p down the tree rooted in n.

    Returns
        - The node we tried to search towards (or from if we cannot get out of a node)
        - The pattern we tried to match (a suffix of p)
        - The part of the edge we could match
        - The part of the edge remaining.
    """
    while p and p[0] in n.children:
        child = n.out_child(p)
        q = shared_prefix(child.edge_label, p)
        if len(q) == len(p) or len(q) < len(child.edge_label):
            return child, q, child.edge_label[len(q) :], p

        assert is_inner(child)
        n, p = child, p[len(q) :]

    return n, p[0:0], p[0:0], p


def tree_fastsearch(n: Inner, p: memoryview) -> tuple[Node, int, memoryview]:
    """Do a fast scan after p starting at n."""
    # In the special case that x is empty (which we guarantee
    # that it isn't after this point), we match the entire
    # local tree, so we have to report that.
    if not p:
        return n, 0, p

    while True:
        assert p[0] in n.children, "With fast scan, there should always be an out-edge"
        child = n.out_child(p)
        # This is the fast scan jump (instead of scanning)
        i = min(len(child.edge_label), len(p))
        if i == len(p):
            return child, i, p

        assert is_inner(child)
        n, p = child, p[i:]


def break_edge(leaf_label: int, n: Node, k: int, z: memoryview) -> Leaf:
    """
    Break an edge in two.

    Break the edge to node `n`, `k` characters down, adding a new leaf
    with label `label` with edge `z`. Returns the new leaf.
    """
    new_n = Inner(n.edge_label[:k])  # The node that splits the edge
    new_leaf = Leaf(leaf_label, z)  # Remaining bit of other path
    n.edge_label = n.edge_label[k:]  # Move start of n forward

    assert n.parent is not None  # n must have a parent (n != root)
    n.parent.add_children(new_n)  # New node replaces n in n's parent
    new_n.add_children(n, new_leaf)  # Make n and new leaf children of new

    return new_leaf


# !SECTION

# SECTION Naive construction algorithm


def naive_st_construction(s: String) -> SuffixTree:
    """
    Naive construction algorithm.

    Construct a suffix tree by searching from the root
    down to the insertion point for each suffix in `s`.
    """
    x = s.view
    root = Inner(x[0:0])

    # Insert suffixes one at a time...
    for i in range(len(x)):
        n, j, _, y = tree_search(root, x[i:])
        if len(j) == 0:
            # We couldn't get out of the node
            assert is_inner(n)
            n.add_children(Leaf(i, y))
        elif len(j) < len(y):
            # We had a mismatch on the edge
            break_edge(i, n, len(j), y[len(j) :])
        else:  # pragma: no cover
            # With the sentinel, we should never match completely
            assert False, "We can't match completely here"

        # n, y, j, z = tree_search(root, x[i:])
        # if z is None:
        #     # We couldn't get out of the node
        #     assert is_inner(n)
        #     n.add_children(Leaf(i, y))
        # elif len(j) < len(y):
        #     # We had a mismatch on the edge
        #     break_edge(i, n, len(j), z)
        # else:  # pragma: no cover
        #     # With the sentinel, we should never match completely
        #     assert False, "We can't match completely here"

    return SuffixTree(s, root)


# !SECTION

# SECTION McCreights construction algorithm


def mccreight_st_construction(s: String) -> SuffixTree:
    """
    Construct a suffix tree with McCreight's algorithm.

    Construct a suffix tree by searching from the root
    down to the insertion point for each suffix in `s`,
    but exploiting suffix links and fast scan along the way.
    """
    x = s.view
    root = Inner(x[0:0])
    v = Leaf(0, x)
    root.add_children(v)
    root.suffix_link = root

    # Insert suffixes one at a time...
    for i in range(1, len(x)):
        # Idea: split x[i:] into y+z+w where we jump
        # past y, then fast-scan through z, and then
        # slow-scan through w.
        # In the general case, y is the suffix of the path
        # down to v.parent.parent, z is the label on
        # v.parent and w is the label on v. There's
        # just some special cases to deal with it...

        p = v.parent
        assert p is not None, "A leaf should always have a parent"

        # If we already have a suffix link, then that is
        # the node we should slow scan from.
        if p.suffix_link is not None:
            # z_node is the node we would get from scanning
            # through y + z, so from here we need to scan
            # for z (later in the function)
            z_node = p.suffix_link
            w = v.edge_label if p is not root else x[i:]

        else:
            # Otherwise, we need to fast scan to find z_node.
            # p can't be the root here, because the root has a
            # suffix link
            assert p.parent is not None, "p can't be the root."
            assert p.parent.suffix_link, "Parent's parent must have a suffix link"

            # Jumping to pp.suffix_link gets us past a, so now we get z and w
            # (with the special case if p is the root) and then we are
            # ready to scan for z_node
            z = p.edge_label if p.parent is not root else p.edge_label[1:]
            w = v.edge_label

            # Fast scan to new starting point
            n, j, z_res = tree_fastsearch(p.parent.suffix_link, z)
            assert j == len(z_res), "Fast scan should always find a match"
            z_node = cast(Inner, n)  # For type checker...

            if len(z_node.edge_label) != j:
                # We ended the search on an edge, so we can directly
                # insert the new leaf
                v = break_edge(i, z_node, j, w)
                p.suffix_link = v.parent
                continue  # Process next suffix...

            # If we landed on a node, then that is p's suffix link
            p.suffix_link = z_node

        # If we are here, we need to slow-scan, and we do that by
        # searching from y_node after the remainder of the suffix, z.
        n, j, _, w_res = tree_search(z_node, w)
        assert len(j) != len(w_res), "We can't match completely here."
        if len(j) == 0:
            # Mismatch on a node...
            assert isinstance(n, Inner), "Mismatch on a node must be on an inner node."
            v = Leaf(i, w_res)
            n.add_children(v)
        elif len(j) < len(w_res):
            # Mismatch on an edge
            v = break_edge(i, n, len(j), w_res[len(j) :])
        # n, w_res, j, _ = tree_search(z_node, w)
        # assert j != len(w_res), "We can't match completely here."
        # if len(j) == 0:
        #     # Mismatch on a node...
        #     assert isinstance(n, Inner), "Mismatch on a node must be on an inner node."
        #     v = Leaf(i, w_res)
        #     n.add_children(v)
        # elif len(j) < len(w_res):
        #     # Mismatch on an edge
        #     v = break_edge(i, n, len(j), w_res[len(j) :])

    return SuffixTree(s, root)


# !SECTION

# SECTION LCP construction algorithm


def search_up(n: Node, length: int) -> tuple[Node, int]:
    """Move length up the tree starting at node n."""
    while length and len(n.edge_label) <= length:
        assert n.parent is not None  # This is mostly for the type checker...
        length -= len(n.edge_label)
        n = n.parent
    # Depth down the edge depends on whether we reached
    depth = 0 if length == 0 else len(n.edge_label) - length
    return n, depth


def lcp_st_construction(s: String, sa: list[int], lcp: list[int]) -> SuffixTree:
    """Construct a suffix tree from the suffix and lcp arrays."""
    x = s.view
    root = Inner(x[0:0])
    v = Leaf(sa[0], x[sa[0] :])
    root.add_children(v)

    for i in range(1, len(sa)):
        n, depth = search_up(v, len(x) - sa[i - 1] - lcp[i])
        if depth == 0:
            # It is, but the type checker doesn't know yet...
            assert isinstance(n, Inner)

            v = Leaf(sa[i], x[sa[i] + lcp[i] :])
            n.add_children(v)
        else:
            v = break_edge(sa[i], n, depth, x[sa[i] + lcp[i] :])

    return SuffixTree(s, root)


# !SECTION
