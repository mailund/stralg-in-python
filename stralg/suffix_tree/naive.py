from ..views import String
from .suffix_tree import Inner, Leaf, SuffixTree, break_edge, edge, node, tree_search


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
        match tree_search(root, x[i:]):
            case node(n, y) if y:
                n.add_children(Leaf(i, y))
            case edge(n, z, w, y) if len(z) < len(y):
                break_edge(i, n, len(z), w)
            case _:  # pragma: no cover
                assert False, "We can't match completely here"

    return SuffixTree(s, root)
