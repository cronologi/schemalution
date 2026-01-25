"""Custom errors for schevo-core."""

from __future__ import annotations


class SchevoCoreError(Exception):
    """Base error for schevo-core."""


class UnsupportedSchemaIdError(SchevoCoreError):
    """Raised when a schema_id is not registered."""


class MissingSchemaVersionError(SchevoCoreError):
    """Raised when a record is missing the schema_version."""


class InvalidSchemaVersionError(SchevoCoreError):
    """Raised when a schema_version is not a valid int."""


class NoMigrationPathError(SchevoCoreError):
    """Raised when a migration path is incomplete."""
