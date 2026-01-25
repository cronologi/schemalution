from schevo_core import MigrationRegistry, __version__, upcast, upcast_to_latest


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_public_api_exports() -> None:
    assert MigrationRegistry() is not None
    assert callable(upcast)
    assert callable(upcast_to_latest)
