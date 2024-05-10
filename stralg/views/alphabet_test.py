from .alphabet import Alphabet


def test_alphabet() -> None:
    """Test the alphabet class."""
    for x in ["foo", "bar", "baz", "foobar", "bazfoo"]:
        y = Alphabet.map_string(x, with_sentinel=False)
        assert len(x) == len(y)
        assert len(y.alpha) == len(set(x)) + 1
        assert str(y) == x

        y = Alphabet.map_string(x, with_sentinel=True)
        assert len(x) == len(y) - 1
        assert len(y.alpha) == len(set(x)) + 1
        assert str(y[:-1]) == x
        assert str(y[0]) == x[0]
