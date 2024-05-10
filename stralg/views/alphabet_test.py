from .alphabet import Alphabet


def test_alphabet() -> None:
    """Test the alphabet class."""
    for x in ["foo", "bar", "baz", "foobar", "bazfoo"]:
        y, alpha = Alphabet.map_string(x, with_sentinel=False)
        assert len(x) == len(y)
        assert len(alpha) == len(set(x)) + 1
        assert alpha.revmap(y) == x

        y, alpha = Alphabet.map_string(x, with_sentinel=True)
        assert len(x) == len(y) - 1
        assert len(alpha) == len(set(x)) + 1
        assert alpha.revmap(y[:-1]) == x
