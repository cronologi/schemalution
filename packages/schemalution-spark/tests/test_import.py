from schemalution_spark import (
    __version__,
    from_json_to_column,
    make_upcast_to_latest_json_udf,
    upcast_record_to_latest_json,
)


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_public_api_exports() -> None:
    assert callable(upcast_record_to_latest_json)
    assert callable(make_upcast_to_latest_json_udf)
    assert callable(from_json_to_column)
