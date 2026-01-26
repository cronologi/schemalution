from schemalution_pack import BasePack, Pack, SchemaSpec, __version__, register_schema


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_public_api_exports() -> None:
    assert SchemaSpec(schema_id="x", latest_version=1) is not None
    assert isinstance(BasePack("example"), BasePack)
    assert callable(register_schema)
    assert Pack is not None
