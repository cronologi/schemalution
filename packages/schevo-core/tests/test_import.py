from schevo_core import SchevoCore, __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_placeholder_class() -> None:
    assert SchevoCore() is not None
