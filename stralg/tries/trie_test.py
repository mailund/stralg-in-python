"""Test of tries."""

from test.helpers import random_string
from typing import Callable as Fn

from stralg.tries.trie import Trie, TrieNode, depth_first_trie

# FIXME: make ... a variadic tuple of strings...
TrieConstructor = Fn[..., Trie]


def get_path_label(node: TrieNode) -> str:
    """
    Get the path label for a node.

    This is a slow way to do it, but it is only for testing.
    """
    res: list[str] = []
    while node.parent:
        (out,) = [k for k, n in node.parent.children.items() if n is node]
        res.append(out)
        node = node.parent
    return "".join(reversed(res))


def test_simple_trie() -> None:
    """Basic test of trie construction."""
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    # we are testing the comparison impl, so disable
    # linting about it being unecessary
    assert trie == trie  # noqa pylint: disable=comparison-with-itself

    assert "foo" in trie
    assert "foobar" in trie
    assert "bar" in trie
    assert "fo" not in trie
    assert "baz" not in trie


def test_trie() -> None:
    """Test that we can build a trie depth-first."""
    trie = Trie()
    trie.insert("foo", 0)
    trie.insert("bar", 1)
    trie.insert("foobar", 2)

    assert trie == depth_first_trie("foo", "bar", "foobar")


def check_to_dot(constr: TrieConstructor, *x: str) -> None:
    """
    Check that we can write a trie to dot.

    The test isn't that great, since we don't look at the result,
    but that would be pretty hard without actually looking at it.
    We just check that creating the dot-file doesn't crash.
    """
    trie = constr(*x)
    print(trie.to_dot())


def test_simple_to_dot(constr: TrieConstructor = depth_first_trie) -> None:
    """
    Check that we can write a trie to dot.

    The test isn't that great, since we don't look at the result,
    but that would be pretty hard without actually looking at it.
    We just check that creating the dot-file doesn't crash.
    """
    check_to_dot(constr, "foo", "bar", "foobar", "baz", "barfoo")


def test_mississippi_suffixes(constr: TrieConstructor = depth_first_trie) -> None:
    """Test that we can create a trie over all suffixes of mississippi."""
    x = "mississippi"
    strings = [x[i:] for i in range(len(x))]
    trie = constr(*strings)
    print(trie.to_dot())


def check_suffix_links(n: TrieNode) -> None:
    """Check that suffix links are set correctly."""
    if n.parent:
        assert n in n.parent.children.values()

    if n.suffix_link:
        path = get_path_label(n)
        s_path = get_path_label(n.suffix_link)
        assert path.endswith(s_path)
    for v in n.children.values():
        check_suffix_links(v)


def check_suffix_links_suffixes(x: str, constr: TrieConstructor) -> None:
    """Check that suffix links are set correctly."""
    strings = [x[i:] for i in range(len(x))]
    trie = constr(*strings)
    check_suffix_links(trie.root)


def check_trie(constr: TrieConstructor, *x: str) -> None:
    """Do a consistency check on a trie."""
    trie = constr(*x)
    check_suffix_links(trie.root)


def test_abc_b_c() -> None:
    """Check trie of abc, b, c."""
    check_trie(depth_first_trie, "abc", "b", "c")


def test_suffix_links_abc() -> None:
    """Check trie on abc, b, c constructed depth-first."""
    check_suffix_links_suffixes("abc", depth_first_trie)


def test_suffix_links_mississippi() -> None:
    """Check suffix links on mississippi depth-first."""
    check_suffix_links_suffixes("mississippi", depth_first_trie)


def check_suffix_links_random(constr: TrieConstructor) -> None:
    """Check suffix links on random tries."""
    for _ in range(5):
        x = random_string(30)
        strings = [x[i:] for i in range(len(x))]
        trie = constr(*strings)
        check_suffix_links(trie.root)


def test_suffix_links_random() -> None:
    """Check suffix links on random tries, depth-first."""
    check_suffix_links_random(depth_first_trie)
