from schevo_pack import PackHelper, __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_placeholder_class() -> None:
    assert PackHelper() is not None
