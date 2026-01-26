from schemalution_mongo import __version__, backfill_to_latest, read_latest, write_latest


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_public_api_exports() -> None:
    assert callable(read_latest)
    assert callable(write_latest)
    assert callable(backfill_to_latest)
