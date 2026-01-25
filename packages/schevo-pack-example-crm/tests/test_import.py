from schevo_pack_example_crm import EXAMPLE_PACK, LATEST_VERSION, SCHEMA_ID, __version__, register


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_placeholder_constant() -> None:
    assert EXAMPLE_PACK == "example_crm"


def test_exports() -> None:
    assert SCHEMA_ID == "crm.customer"
    assert LATEST_VERSION == 3
    assert callable(register)
