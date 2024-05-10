from dataclasses import dataclass

from ..views import String
from .suffix_tree import (
    Inner,
    Leaf,
    SearchResult,
    SuffixTree,
    break_edge,
    edge,
    is_inner,
    node,
    tree_search,
)


def tree_fastsearch(n: Inner, p: memoryview) -> SearchResult:
    """Do a fast scan after p starting at n."""
    while p:
        assert p[0] in n.children, "With fast scan, there should always be an out-edge"
        child = n.out_child(p)
        # This is the fast scan jump (instead of scanning)
        i = min(len(child.edge_label), len(p))
        if i == len(p):
            return edge(child, child.edge_label[:i], child.edge_label[i:], p)

        assert is_inner(child)
        n, p = child, p[i:]

    return node(n, p)


@dataclass
class ZLoc:
    z_node: Inner
    w: memoryview


def z_node(root: Inner, x: memoryview, i: int, v: Leaf) -> Leaf | ZLoc:
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
        # for z
        return ZLoc(z_node=p.suffix_link, w=v.edge_label if p is not root else x[i:])

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

        # Fast scan to new starting point, z_node. Short-circuit if the mismatch is on an edge
        match tree_fastsearch(p.parent.suffix_link, z):
            case edge(z_node, match, rest, _) if len(rest) > 0:
                # mismatch on the edge so we can break immidiately
                v = break_edge(i, z_node, len(match), w)
                p.suffix_link = v.parent
                # continue  # Process next suffix...
                return v

            case edge(z_node, _, _, _) | node(z_node, _):
                # mostly for type checking, but it should always be true
                assert is_inner(z_node)

                # If we landed on a node, then that is p's suffix link
                p.suffix_link = z_node

        return ZLoc(z_node, w)


def v_node(root: Inner, x: memoryview, i: int, v: Leaf) -> Leaf:
    """Insert suffix x[i:] into the suffix tree."""

    match z_node(root, x, i, v):
        case Leaf() as v:
            pass
        case ZLoc(zn, w):
            match tree_search(zn, w):
                case node(n, y) if y:
                    n.add_children(v := Leaf(i, y))
                case edge(n, z, w, y) if len(z) < len(y):
                    v = break_edge(i, n, len(z), y[len(z) :])
                case _:  # pragma: no cover
                    assert False, "We can't match completely here"

    return v


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
        v = v_node(root, x, i, v)

    return SuffixTree(s, root)
