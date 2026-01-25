from schevo_compose import Composer, __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_placeholder_class() -> None:
    assert Composer() is not None
