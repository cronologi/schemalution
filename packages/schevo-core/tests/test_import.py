from schevo_core import (
    InvalidSchemaVersionError,
    MigrationRegistry,
    MissingSchemaVersionError,
    NoMigrationPathError,
    UnsupportedSchemaIdError,
    __version__,
    upcast,
    upcast_to_latest,
)


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_public_api_exports() -> None:
    assert MigrationRegistry() is not None
    assert callable(upcast)
    assert callable(upcast_to_latest)
    assert issubclass(UnsupportedSchemaIdError, Exception)
    assert issubclass(MissingSchemaVersionError, Exception)
    assert issubclass(InvalidSchemaVersionError, Exception)
    assert issubclass(NoMigrationPathError, Exception)
