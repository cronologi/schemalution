"""Custom errors for schemalution-core."""

from __future__ import annotations


class schemalutionCoreError(Exception):
    """Base error for schemalution-core."""


class UnsupportedSchemaIdError(schemalutionCoreError):
    """Raised when a schema_id is not registered."""


class MissingSchemaVersionError(schemalutionCoreError):
    """Raised when a record is missing the schema_version."""


class InvalidSchemaVersionError(schemalutionCoreError):
    """Raised when a schema_version is not a valid int."""


class NoMigrationPathError(schemalutionCoreError):
    """Raised when a migration path is incomplete."""
